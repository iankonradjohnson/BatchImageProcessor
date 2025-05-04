"""
A concrete factory implementation for creating video processors.

This module implements the MediaProcessorFactory abstract class for VideoClip
processors. It provides a registry-based approach to creating VideoProcessor
instances based on configuration.
"""

from typing import Dict, Any, Type, Optional

from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
from batch_image_processor.processors.video.video_clip import VideoClip
from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_rotator import AutoOrientationResolver
from batch_image_processor.processors.video.moviepy_video_clip import MoviePyVideoClip


class VideoProcessorFactory(MediaProcessorFactory[VideoClip]):
    """
    Factory for creating video processors.
    
    This factory implements the MediaProcessorFactory abstract class
    for VideoClip processors. It maintains a registry of processor types
    and their corresponding classes.
    """
    
    # Registry of processor types and their classes
    _processor_registry: Dict[str, Type[VideoProcessor]] = {}
    
    # Default video clip implementation to use
    _video_clip_impl: Type[VideoClip] = MoviePyVideoClip
    
    @classmethod
    def create_processor(cls, config: Dict[str, Any]) -> VideoProcessor:
        """
        Create a video processor based on the provided configuration.
        
        Args:
            config: Configuration dictionary with processor parameters
                   including the 'type' key to determine which processor to create.
                   
        Returns:
            A VideoProcessor instance.
            
        Raises:
            ValueError: If the processor type is invalid or not supported.
        """
        processor_type = config.get("type")
        
        # Extract parameters, removing 'type' key
        params = {k: v for k, v in config.items() if k != "type"}
            
        # Use the registry for processor types
        if processor_type in cls._processor_registry:
            processor_class = cls._processor_registry[processor_type]
            return processor_class(**params)
                
        raise ValueError(f"Invalid processor type: {processor_type}")
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[VideoProcessor]):
        """
        Register a new processor type with the factory.
        
        Args:
            processor_type: The name/type of the processor to register.
            processor_class: The VideoProcessor class to instantiate for this type.
        """
        cls._processor_registry[processor_type] = processor_class
    
    @classmethod
    def create_video_clip(cls, file_path: str) -> VideoClip:
        """
        Create a VideoClip instance for the given file.
        
        This uses the default VideoClip implementation (MoviePyVideoClip by default).
        
        Args:
            file_path: Path to the video file
            
        Returns:
            A VideoClip instance
        """
        return cls._video_clip_impl.load(file_path)
    
    @classmethod
    def set_video_clip_impl(cls, impl_class: Type[VideoClip]) -> None:
        """
        Set the default VideoClip implementation to use.
        
        This can be used to override the default implementation for testing
        or to use a different backend.
        
        Args:
            impl_class: The VideoClip implementation class to use
        """
        cls._video_clip_impl = impl_class


# Register video processor types as they are implemented
VideoProcessorFactory.register_processor("VideoRotator", AutoOrientationResolver)