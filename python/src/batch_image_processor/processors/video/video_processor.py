"""
Base class for video processors.

This module defines the VideoProcessor base class that implements the MediaProcessor
interface for video processing operations using the VideoClip interface.
"""

from typing import Union, List
from batch_image_processor.processors.media_processor import MediaProcessor
from batch_image_processor.processors.video.video_clip import VideoClipInterface


class VideoProcessor(MediaProcessor[VideoClipInterface]):
    """
    Base class for video processors.
    
    This class implements the MediaProcessor interface for video processing
    operations. Subclasses should override the process method to implement
    specific video processing algorithms.
    """
    
    def process(self, clip: VideoClipInterface) -> Union[VideoClipInterface, List[VideoClipInterface], None]:
        """
        Process the video clip.
        
        This method must be implemented by subclasses to provide specific
        video processing logic.
        
        Args:
            clip: The input video clip to be processed
            
        Returns:
            - The processed video clip
            - A list of processed video clips (for splitting operations)
            - None if the video should be filtered out
        """
        raise NotImplementedError("Subclasses must implement process()")