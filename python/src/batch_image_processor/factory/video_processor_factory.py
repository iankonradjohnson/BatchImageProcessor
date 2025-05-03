"""
A concrete factory implementation for creating video processors.

This module implements the MediaProcessorFactory abstract class for MoviePy VideoFileClip
processors. It provides a registry-based approach to creating VideoProcessor
instances based on configuration.
"""

from typing import Dict, Any, Type
from moviepy.editor import VideoFileClip

from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
from batch_image_processor.processors.video.video_processor import VideoProcessor


class VideoProcessorFactory(MediaProcessorFactory[VideoFileClip]):
    """
    Factory for creating video processors.
    
    This factory implements the MediaProcessorFactory abstract class
    for MoviePy VideoFileClip processors. It maintains a registry of processor types
    and their corresponding classes.
    """
    
    # Registry of processor types and their classes
    _processor_registry: Dict[str, Type[VideoProcessor]] = {}
    
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
            
        # Use the registry for processor types
        if processor_type in cls._processor_registry:
            processor_class = cls._processor_registry[processor_type]
            return processor_class(config)
                
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


# Register video processor types as they are implemented
# Example: VideoProcessorFactory.register_processor("Resize", VideoResizeProcessor)