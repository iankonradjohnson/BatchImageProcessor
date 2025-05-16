import numpy as np
from typing import List, Union, Optional, Dict, Any, Protocol
import math
from aesthetic_predictor import AestheticPredictor
import abc
from PIL import Image

from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_clip import VideoClipInterface
from batch_image_processor.processors.video.aesthetic_score_tracker import AestheticScoreTracker


class SegmentDetectionStrategy(abc.ABC):
    """Base strategy for detecting segments in a video based on aesthetic scores."""
    
    def __init__(self, threshold: float, min_segment_duration: float):
        self.threshold = threshold
        self.min_segment_duration = min_segment_duration
    
    @abc.abstractmethod
    def find_segments(self, scores: List[float], duration: float) -> List[tuple]:
        """Find segments that meet the aesthetic criteria."""
        pass


class BasicSegmentDetectionStrategy(SegmentDetectionStrategy):
    """Detects individual segments that exceed the threshold score."""
    
    def find_segments(self, scores: List[float], duration: float) -> List[tuple]:
        good_segments = []
        segment_start = None
        time_per_score = duration / len(scores)
        
        for i, score in enumerate(scores):
            frame_time = i * time_per_score
            
            if score >= self.threshold and segment_start is None:
                segment_start = frame_time
            
            elif score < self.threshold and segment_start is not None:
                segment_end = frame_time
                
                if segment_end - segment_start >= self.min_segment_duration:
                    good_segments.append((segment_start, segment_end))
                
                segment_start = None
        
        if segment_start is not None:
            segment_end = duration
            if segment_end - segment_start >= self.min_segment_duration:
                good_segments.append((segment_start, segment_end))
        
        return good_segments


class CombinedSegmentDetectionStrategy(SegmentDetectionStrategy):
    """Detects and combines adjacent segments that exceed the threshold score."""
    
    def find_segments(self, scores: List[float], duration: float) -> List[tuple]:
        # First get basic segments
        basic_strategy = BasicSegmentDetectionStrategy(self.threshold, self.min_segment_duration)
        segments = basic_strategy.find_segments(scores, duration)
        
        if not segments:
            return []
            
        # Then combine adjacent segments
        time_per_score = duration / len(scores)
        combined_segments = []
        current_start, current_end = segments[0]
        
        for i in range(1, len(segments)):
            next_start, next_end = segments[i]
            
            # If this segment starts exactly where the previous one ended (or very close)
            if abs(next_start - current_end) < time_per_score:
                # Extend the current segment
                current_end = next_end
            else:
                # Add the current segment and start a new one
                combined_segments.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        
        # Add the last segment
        combined_segments.append((current_start, current_end))
        return combined_segments


class AestheticVideoProcessor(VideoProcessor):
    def __init__(
        self, 
        aesthetic_predictor: AestheticPredictor,
        threshold: float = 5.0,
        sample_rate: float = 1.0,
        min_segment_duration: float = 1,
        combine_adjacent_segments: bool = False,
        scores_output_path: Optional[str] = None
    ):
        self.predictor = aesthetic_predictor
        self.sample_rate = sample_rate
        self.min_segment_duration = min_segment_duration
        
        # Create a score tracker to manage the scores
        self.score_tracker = AestheticScoreTracker(scores_output_path)
        
        # Dictionary to map clips to their tracker IDs
        self.clip_tracker_ids = {}
        
        # Select the appropriate segment detection strategy
        if combine_adjacent_segments:
            self.segment_strategy = CombinedSegmentDetectionStrategy(threshold, min_segment_duration)
        else:
            self.segment_strategy = BasicSegmentDetectionStrategy(threshold, min_segment_duration)

    def process(self, clip: VideoClipInterface) -> Union[VideoClipInterface, List[VideoClipInterface], None]:
        frames_to_analyze = self._get_frames_to_analyze(clip)
        
        scores = self._score_frames(clip, frames_to_analyze)
        
        # Use the selected strategy to find segments
        good_segments = self.segment_strategy.find_segments(scores, clip.duration)
        
        if not good_segments:
            return None
        
        # Pass the scores to extract_segments to calculate segment-specific scores
        result_clips = self._extract_segments(clip, good_segments, scores)
        
        return result_clips if result_clips else None
    
    def _get_frames_to_analyze(self, clip: VideoClipInterface) -> List[float]:
        duration = clip.duration
        num_frames = math.ceil(duration * self.sample_rate)
        
        return [i * (duration / num_frames) for i in range(num_frames)]
    
    def _score_frames(self, clip: VideoClipInterface, timestamps: List[float]) -> List[float]:
        scores = []
        
        for ts in timestamps:
            # The frame will now be oriented correctly from get_frame
            frame = clip.get_frame(ts)
            
            # Debug information
            print(f"Frame shape: {frame.shape}")
            print(f"Clip dimensions: width={clip.width}, height={clip.height}")
            print(f"Clip orientation: {clip.orientation}, rotation: {clip.rotation}")

            # Convert to PIL image
            pil_frame = Image.fromarray(frame.astype('uint8'), 'RGB')
            
            # Use the frame for prediction
            score = self.predictor.predict(pil_frame)
            
            # Show the image
            # pil_frame.show()
            
            print(f"Score is {score}")
            scores.append(score)
        
        return scores
    
    def _extract_segments(self, clip: VideoClipInterface, segments: List[tuple], 
                        all_scores: List[float] = None) -> List[VideoClipInterface]:
        result_clips = []
        
        for start_time, end_time in segments:
            try:
                subclip = clip.subclipped(start_time, end_time)
                
                # For each subclip, we need to get its own scores from the source video
                if all_scores:
                    # Extract frames to analyze for this subclip
                    subclip_frames = self._get_frames_to_analyze(subclip)
                    
                    # Score the frames for this specific subclip
                    subclip_scores = self._score_frames(subclip, subclip_frames)
                    
                    # Register with just the subclip and its specific scores
                    clip_id = self.score_tracker.register_clip_with_scores(
                        clip=subclip,
                        frame_scores=subclip_scores
                    )
                    
                    # Store the tracker ID for later association with output path
                    self.clip_tracker_ids[id(subclip)] = clip_id
                
                result_clips.append(subclip)
            except AttributeError:
                raise ValueError(f"Subclipping not supported for clip type: {type(clip)}")
        
        return result_clips
        
    def register_output_filepath(self, clip: VideoClipInterface, filepath: str) -> None:
        """
        Register the output filepath for a clip with its aesthetic score.
        
        Args:
            clip: The video clip that was saved
            filepath: The filepath where the clip was saved
        """
        clip_id = id(clip)
        if clip_id in self.clip_tracker_ids:
            tracker_id = self.clip_tracker_ids[clip_id]
            self.score_tracker.register_output_filepath(tracker_id, filepath)
    
    def save_scores(self) -> None:
        """Save the scores to the JSON file."""
        self.score_tracker.save_scores_to_json()
        
    def get_scores(self) -> Dict[str, float]:
        """Get the dictionary mapping output filepaths to scores."""
        return self.score_tracker.get_scores()