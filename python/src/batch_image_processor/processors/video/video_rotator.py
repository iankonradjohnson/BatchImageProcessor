"""Video rotation processor for videos."""

from typing import Literal

from batch_image_processor.processors.video.video_clip import VideoClip
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
    
    def process(self, clip: VideoClip) -> VideoClip:
        """Process the video clip by rotating it."""
        width = clip.width
        height = clip.height
        
        # Add debugging to see what's happening with the dimensions
        print(f"Original clip dimensions: width={width}, height={height}")
        
        # Check for rotation metadata
        print(f"Clip has rotation metadata: {clip.rotation}")
        
        # Use the built-in is_horizontal property which considers rotation metadata
        is_horizontal = clip.is_horizontal
        print(f"Is horizontal: {is_horizontal}")
        
        # If already in target orientation, don't rotate
        if (self.target_orientation == "vertical" and not is_horizontal) or \
           (self.target_orientation == "horizontal" and is_horizontal):
            print(f"No rotation needed. Target: {self.target_orientation}, Current: {'horizontal' if is_horizontal else 'vertical'}")
            return clip
        
        print(f"Rotating video with angle {-90 if self.rotation_direction == 'left' else 90}")
        rotation_angle = -90 if self.rotation_direction == "left" else 90
        rotated_clip = clip.rotate(rotation_angle)
        
        # Check dimensions after rotation
        print(f"After rotation: width={rotated_clip.width}, height={rotated_clip.height}")
        
        return rotated_clip