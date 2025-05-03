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
        """
        Process the video clip by rotating it based on the target orientation.
        
        Args:
            clip: The video clip to process
            
        Returns:
            The processed video clip with appropriate rotation
        """
        # Check if the video already matches the target orientation
        is_horizontal = clip.is_horizontal
        
        # Determine if we need to rotate based on target orientation
        needs_rotation = (self.target_orientation == "vertical" and is_horizontal) or \
                         (self.target_orientation == "horizontal" and not is_horizontal)
        
        if needs_rotation:
            # Determine rotation angle based on direction
            angle = 90 if self.rotation_direction == "right" else -90
            clip = clip.rotate(angle)
        
        # Return the clip (rotated or unchanged)
        return clip