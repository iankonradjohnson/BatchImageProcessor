"""
Base class for video processors.

This module defines the VideoProcessor base class that implements the MediaProcessor
interface for video processing operations using the VideoClip interface.
"""

from batch_image_processor.processors.media_processor import MediaProcessor
from batch_image_processor.processors.video.video_clip import VideoClip


class VideoProcessor(MediaProcessor[VideoClip]):
    """
    Base class for video processors.
    
    This class implements the MediaProcessor interface for video processing
    operations. Subclasses should override the process method to implement
    specific video processing algorithms.
    """
    
    def process(self, clip: VideoClip) -> VideoClip:
        """
        Process the video clip.
        
        This method must be implemented by subclasses to provide specific
        video processing logic.
        
        Args:
            clip: The input video clip to be processed
            
        Returns:
            The processed video clip
        """
        raise NotImplementedError("Subclasses must implement process()")