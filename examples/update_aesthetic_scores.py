"""
Utility script to update or generate aesthetic scores for existing video files.

This script scans a directory of processed videos and generates or updates
a JSON file mapping filepaths to their aesthetic scores.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import glob

# Add the project root to Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aesthetic_predictor.predictor import AestheticPredictor
from batch_image_processor.factory.video_processor_factory import VideoProcessorFactory
from batch_image_processor.processors.video.video_clip import VideoClipInterface


def analyze_video_aesthetic(video_path: str, sample_rate: float = 1.0) -> float:
    """
    Analyze a video file and return its average aesthetic score.
    
    Args:
        video_path: Path to the video file
        sample_rate: How many frames per second to analyze
        
    Returns:
        Average aesthetic score (0-10)
    """
    predictor = AestheticPredictor()
    clip = VideoProcessorFactory.create_video_clip(video_path)
    
    # Sample frames at regular intervals
    duration = clip.duration
    num_frames = int(duration * sample_rate)
    frame_times = [i * (duration / max(1, num_frames)) for i in range(num_frames)]
    
    scores = []
    for t in frame_times:
        try:
            frame = clip.get_frame(t)
            
            # Convert to PIL image for prediction
            from PIL import Image
            pil_frame = Image.fromarray(frame.astype('uint8'), 'RGB')
            
            # Get aesthetic score
            score = predictor.predict(pil_frame)
            scores.append(score)
            print(f"Frame at {t:.2f}s: score {score:.2f}")
        except Exception as e:
            print(f"Error analyzing frame at {t}s: {str(e)}")
    
    # Close the clip
    clip.close()
    
    # Calculate average score
    if not scores:
        return 0.0
        
    avg_score = sum(scores) / len(scores)
    print(f"Average score for {os.path.basename(video_path)}: {avg_score:.2f}")
    return avg_score


def load_existing_scores(json_path: str) -> Dict[str, float]:
    """
    Load existing scores from a JSON file if it exists.
    
    Args:
        json_path: Path to the JSON file
        
    Returns:
        Dictionary mapping filepaths to scores
    """
    if not os.path.exists(json_path):
        return {}
        
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading existing scores: {str(e)}")
        return {}


def save_scores(scores: Dict[str, float], json_path: str) -> None:
    """
    Save scores to a JSON file.
    
    Args:
        scores: Dictionary mapping filepaths to scores
        json_path: Path to save the JSON file
    """
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    try:
        with open(json_path, 'w') as f:
            json.dump(scores, f, indent=2)
        print(f"Saved {len(scores)} scores to {json_path}")
    except IOError as e:
        print(f"Error saving scores: {str(e)}")


def update_scores_for_directory(
    video_dir: str, 
    json_path: str,
    sample_rate: float = 1.0,
    force_update: bool = False
) -> Dict[str, float]:
    """
    Update scores for all videos in a directory.
    
    Args:
        video_dir: Directory containing videos
        json_path: Path to save the JSON file
        sample_rate: Frames per second to analyze
        force_update: Whether to recompute scores for videos already in the JSON
        
    Returns:
        Updated scores dictionary
    """
    # Load existing scores
    scores = load_existing_scores(json_path)
    original_count = len(scores)
    
    # Find all video files
    video_patterns = ['*.mp4', '*.avi', '*.mov', '*.mkv']
    video_files = []
    
    for pattern in video_patterns:
        video_files.extend(glob.glob(os.path.join(video_dir, pattern)))
    
    # Make paths absolute if they aren't already
    video_files = [os.path.abspath(p) for p in video_files]
    
    print(f"Found {len(video_files)} video files in {video_dir}")
    
    # Process videos not in the scores dict or if force_update is True
    for video_path in video_files:
        if video_path not in scores or force_update:
            print(f"Analyzing {os.path.basename(video_path)}...")
            try:
                scores[video_path] = analyze_video_aesthetic(video_path, sample_rate)
                
                # Save after each video in case of crashes
                save_scores(scores, json_path)
            except Exception as e:
                print(f"Error processing {video_path}: {str(e)}")
        else:
            print(f"Skipping {os.path.basename(video_path)} (already analyzed)")
    
    new_count = len(scores)
    print(f"Added scores for {new_count - original_count} new videos")
    
    return scores


def main():
    parser = argparse.ArgumentParser(description="Update aesthetic scores for video files")
    parser.add_argument("--dir", "-d", required=True, help="Directory containing video files")
    parser.add_argument("--output", "-o", help="Path to save JSON file (default: <dir>/aesthetic_scores.json)")
    parser.add_argument("--sample-rate", type=float, default=1.0, help="Frames per second to analyze")
    parser.add_argument("--force", "-f", action="store_true", help="Force recomputation of all scores")
    
    args = parser.parse_args()
    
    video_dir = args.dir
    json_path = args.output or os.path.join(video_dir, "aesthetic_scores.json")
    
    update_scores_for_directory(
        video_dir=video_dir,
        json_path=json_path,
        sample_rate=args.sample_rate,
        force_update=args.force
    )


if __name__ == "__main__":
    main()