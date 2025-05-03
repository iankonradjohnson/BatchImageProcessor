"""Video rotation processor for videos."""

from typing import Literal

from moviepy import VideoFileClip

from batch_image_processor.processors.video.video_processor import VideoProcessor


class VideoRotator(VideoProcessor):
    """Video rotation processor."""
    
    def __init__(
        self, 
        rotation_direction: Literal["left", "right"] = "left",
        target_orientation: Literal["vertical", "horizontal"] = "vertical"
    ):
        """Initialize the video rotator."""
        self.rotation_direction = rotation_direction
        self.target_orientation = target_orientation
    
    def process(self, clip: VideoFileClip) -> VideoFileClip:
        """Process the video clip by rotating it."""
        width = clip.w
        height = clip.h
        
        # Add debugging to see what's happening with the dimensions
        print(f"Original clip dimensions: w={width}, h={height}")
        
        # Check size attribute if it exists
        if hasattr(clip, 'size'):
            print(f"Clip size attribute: {clip.size}")
        
        # Check for rotation metadata
        print(f"Clip has rotation metadata: {clip.rotation}")
        
        is_horizontal = width > height
        print(f"Is horizontal: {is_horizontal}")
        
        # If already in target orientation, don't rotate
        if (self.target_orientation == "vertical" and not is_horizontal) or \
           (self.target_orientation == "horizontal" and is_horizontal):
            print(f"No rotation needed. Target: {self.target_orientation}, Current: {'horizontal' if is_horizontal else 'vertical'}")
            return clip
        
        print(f"Rotating video with angle {-90 if self.rotation_direction == 'left' else 90}")
        rotation_angle = -90 if self.rotation_direction == "left" else 90
        rotated_clip = clip.rotated(rotation_angle, expand=True)
        
        # Check dimensions after rotation
        print(f"After rotation: w={rotated_clip.w}, h={rotated_clip.h}")
        
        return rotated_clip