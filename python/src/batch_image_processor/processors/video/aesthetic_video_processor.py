import numpy as np
from typing import List, Union, Optional, Dict, Any
import math
from aesthetic_predictor import AestheticPredictor

from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_clip import VideoClipInterface


class AestheticVideoProcessor(VideoProcessor):
    def __init__(
        self, 
        aesthetic_predictor: AestheticPredictor,
        threshold: float = 5.0,
        sample_rate: float = 1.0,
        min_segment_duration: float = 1
    ):
        self.predictor = aesthetic_predictor
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.min_segment_duration = min_segment_duration

    def process(self, clip: VideoClipInterface) -> Union[VideoClipInterface, List[VideoClipInterface], None]:
        frames_to_analyze = self._get_frames_to_analyze(clip)
        
        scores = self._score_frames(clip, frames_to_analyze)
        
        good_segments = self._find_good_segments(scores, clip.duration)
        
        if not good_segments:
            return None
        
        result_clips = self._extract_segments(clip, good_segments)
        
        return result_clips if result_clips else None
    
    def _get_frames_to_analyze(self, clip: VideoClipInterface) -> List[float]:
        duration = clip.duration
        num_frames = math.ceil(duration * self.sample_rate)
        
        return [i * (duration / num_frames) for i in range(num_frames)]
    
    def _score_frames(self, clip: VideoClipInterface, timestamps: List[float]) -> List[float]:
        scores = []
        
        for ts in timestamps:
            frame = clip.get_frame(ts)
            
            from PIL import Image
            pil_frame = Image.fromarray(frame.astype('uint8'))
            
            score = self.predictor.predict(pil_frame)

            pil_frame.show()

            print(f"Score is {score}")
            scores.append(score)
        
        return scores
    
    def _find_good_segments(self, scores: List[float], duration: float) -> List[tuple]:
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
    
    def _extract_segments(self, clip: VideoClipInterface, segments: List[tuple]) -> List[VideoClipInterface]:
        result_clips = []
        
        for start_time, end_time in segments:
            try:
                subclip = clip.subclipped(start_time, end_time)
                result_clips.append(subclip)
            except AttributeError:
                raise ValueError(f"Subclipping not supported for clip type: {type(clip)}")
        
        return result_clips