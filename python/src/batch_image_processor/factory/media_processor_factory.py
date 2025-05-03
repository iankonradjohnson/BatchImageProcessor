"""
A module providing a factory pattern for media processors.

This module defines a factory interface for creating media processors
of different types (image, video, audio, etc). Concrete factory implementations
should be created for each media type.
"""

from typing import Dict, Any, TypeVar, Generic, Protocol, Type, ClassVar, runtime_checkable

from batch_image_processor.processors.media_processor import MediaProcessor

T = TypeVar('T')  # Generic type for the media processor


@runtime_checkable
class MediaProcessorFactory(Protocol[T]):
    """
    Factory interface for creating media processors.
    
    This interface defines the methods required for creating media processors.
    Concrete factory implementations should be created for each media type.
    """
    
    @classmethod
    def create_processor(cls, config: Dict[str, Any]) -> MediaProcessor[T]:
        """
        Create a media processor based on the provided configuration.
        
        Args:
            config: Configuration dictionary with processor parameters
                   including the 'type' key to determine which processor to create.
                   
        Returns:
            A concrete MediaProcessor instance.
            
        Raises:
            ValueError: If the processor type is invalid or not supported.
        """
        ...
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type) -> None:
        """
        Register a new processor type with the factory.
        
        Args:
            processor_type: The name/type of the processor to register.
            processor_class: The class to instantiate for this type.
        """
        ...