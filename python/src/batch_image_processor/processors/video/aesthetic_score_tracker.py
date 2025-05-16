"""Helper class for tracking aesthetic scores and their corresponding output filepaths."""

import os
import json
import uuid
from typing import Dict, Optional, List, Tuple, Any

from batch_image_processor.processors.video.video_clip import VideoClipInterface


class AestheticScoreTracker:
    """Helper class for tracking aesthetic scores and their corresponding output filepaths."""
    
    def __init__(self, output_json_path: Optional[str] = None):
        """
        Initialize an AestheticScoreTracker.
        
        Args:
            output_json_path: Optional path to save the JSON mapping of filepaths to scores
        """
        self.output_json_path = output_json_path
        self.clip_scores = {}  # Maps clip_id -> score
        self.segment_scores = {}  # Maps clip_id -> [segment scores]
        self.filepath_scores = {}  # Maps output_path -> score
        
        # Load existing scores if available
        if output_json_path and os.path.exists(output_json_path):
            try:
                with open(output_json_path, 'r') as f:
                    self.filepath_scores = json.load(f)
                print(f"Loaded {len(self.filepath_scores)} existing scores from {output_json_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading existing scores: {str(e)}")
        
    def register_clip_with_scores(self, 
                                 clip: VideoClipInterface, 
                                 frame_scores: List[float]) -> str:
        """
        Register a clip with its frame scores.
        
        Args:
            clip: The video clip
            frame_scores: List of scores for individual frames
            
        Returns:
            A unique ID for the clip
        """
        clip_id = str(uuid.uuid4())
        
        # Use average of all frame scores
        if frame_scores:
            avg_score = sum(frame_scores) / len(frame_scores)
            self.clip_scores[clip_id] = avg_score
            self.segment_scores[clip_id] = frame_scores
                
        return clip_id
    
    def register_output_filepath(self, clip_id: str, filepath: str) -> None:
        """
        Register the output filepath for a clip with its aesthetic score.
        
        Args:
            clip_id: The unique ID returned from register_clip_with_scores
            filepath: The output filepath where the clip was saved
        """
        if clip_id in self.clip_scores:
            self.filepath_scores[filepath] = self.clip_scores[clip_id]
            
            # If output_path is set, save the scores
            if self.output_json_path:
                self.save_scores_to_json()
    
    def save_scores_to_json(self) -> None:
        """Save the mapping of filepaths to aesthetic scores to a JSON file."""
        if not self.output_json_path or not self.filepath_scores:
            return
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_json_path), exist_ok=True)
        
        # Save the scores to a JSON file
        with open(self.output_json_path, 'w') as f:
            json.dump(self.filepath_scores, f, indent=2)
        
        print(f"Saved aesthetic scores to {self.output_json_path}")
    
    def get_scores(self) -> Dict[str, float]:
        """Get the dictionary mapping output filepaths to scores."""
        return self.filepath_scores.copy()
        
    def get_score_for_clip(self, clip_id: str) -> Optional[float]:
        """Get the aesthetic score for a clip."""
        return self.clip_scores.get(clip_id)
        
    def get_detailed_scores(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about scores."""
        detailed = {}
        
        for filepath, score in self.filepath_scores.items():
            clip_id = None
            for cid, s in self.clip_scores.items():
                if s == score:
                    clip_id = cid
                    break
                    
            if clip_id:
                detailed[filepath] = {
                    "score": score,
                    "segment_scores": self.segment_scores.get(clip_id, [])
                }
            else:
                detailed[filepath] = {"score": score}
                
        return detailed