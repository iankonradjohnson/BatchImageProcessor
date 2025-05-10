"""
Content Engine for video processing with aesthetic score tracking.

This script processes videos based on their aesthetic quality and
generates a JSON mapping of output filepaths to their aesthetic scores.
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List
from aesthetic_predictor.predictor import AestheticPredictor

# Add the project root to Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline
from batch_image_processor.processors.video.aesthetic_video_processor import AestheticVideoProcessor


class ContentEngine:
    """
    A content engine that processes videos and tracks their aesthetic scores.
    """
    
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        scores_output_path: Optional[str] = None,
        threshold: float = 5.0,
        sample_rate: float = 1.0,
        min_segment_duration: float = 2.0,
        combine_adjacent_segments: bool = True
    ):
        """
        Initialize the ContentEngine.
        
        Args:
            input_dir: Directory containing input videos
            output_dir: Directory to save processed videos
            scores_output_path: Path to save the JSON with filepath -> score mapping
            threshold: Minimum aesthetic score (0-10) to include a segment
            sample_rate: How many frames per second to analyze
            min_segment_duration: Minimum duration in seconds for segments
            combine_adjacent_segments: Whether to combine adjacent segments
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # If scores_output_path not specified, use default in output_dir
        if not scores_output_path:
            scores_output_path = os.path.join(output_dir, "aesthetic_scores.json")
            
        self.scores_output_path = scores_output_path
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.min_segment_duration = min_segment_duration
        self.combine_adjacent_segments = combine_adjacent_segments
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the aesthetic predictor
        self.predictor = AestheticPredictor()
        
        # Create the aesthetic processor with score tracking
        self.aesthetic_processor = AestheticVideoProcessor(
            aesthetic_predictor=self.predictor,
            threshold=threshold,
            sample_rate=sample_rate,
            min_segment_duration=min_segment_duration,
            combine_adjacent_segments=combine_adjacent_segments,
            scores_output_path=scores_output_path
        )
        
        # Create the batch processor
        self.batch_processor = BatchProcessor(
            input_dir=input_dir,
            output_dir=output_dir,
            processors=[self.aesthetic_processor],
            pipeline_class=VideoPipeline
        )
    
    def process_videos(self) -> Dict[str, float]:
        """
        Process all videos in the input directory.
        
        Returns:
            Dictionary mapping output filepaths to aesthetic scores
        """
        print(f"Processing videos in {self.input_dir}")
        print(f"Output scores will be saved to {self.scores_output_path}")
        
        # Process all videos
        self.batch_processor.batch_process()
        
        # Get the scores
        scores = self.aesthetic_processor.get_scores()
        
        # Print the scores
        print("\nAesthetic Scores:")
        for path, score in scores.items():
            print(f"  {path}: {score:.2f}")
            
        return scores


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process videos based on aesthetic quality")
    parser.add_argument("--input", "-i", required=True, help="Input directory with videos")
    parser.add_argument("--output", "-o", required=True, help="Output directory for processed videos")
    parser.add_argument("--scores", "-s", help="Path to save aesthetic scores JSON")
    parser.add_argument("--threshold", "-t", type=float, default=5.0, help="Minimum aesthetic score (0-10)")
    parser.add_argument("--sample-rate", type=float, default=1.0, help="Frames per second to analyze")
    parser.add_argument("--min-duration", type=float, default=2.0, help="Minimum segment duration in seconds")
    parser.add_argument("--no-combine", action="store_true", help="Don't combine adjacent segments")
    
    args = parser.parse_args()
    
    engine = ContentEngine(
        input_dir=args.input,
        output_dir=args.output,
        scores_output_path=args.scores,
        threshold=args.threshold,
        sample_rate=args.sample_rate,
        min_segment_duration=args.min_duration,
        combine_adjacent_segments=not args.no_combine
    )
    
    engine.process_videos()


if __name__ == "__main__":
    main()