"""
A concrete factory implementation for creating video processors.

This module implements the MediaProcessorFactory abstract class for VideoClip
processors. It provides a registry-based approach to creating VideoProcessor
instances based on configuration.
"""

from typing import Dict, Any, Type, Optional

from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
from batch_image_processor.processors.video.video_clip import VideoClipInterface
from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_rotator import AutoOrientationResolver
from batch_image_processor.processors.video.moviepy_video_clip import MoviePyVideoClipInterface
from batch_image_processor.processors.video.aesthetic_video_processor import AestheticVideoProcessor


class VideoProcessorFactory(MediaProcessorFactory[VideoClipInterface]):
    _processor_registry: Dict[str, Type[VideoProcessor]] = {}
    
    _video_clip_impl: Type[VideoClipInterface] = MoviePyVideoClipInterface
    
    @classmethod
    def create_processor(cls, config: Dict[str, Any]) -> VideoProcessor:
        processor_type = config.get("type")
        
        params = {k: v for k, v in config.items() if k != "type"}
            
        if processor_type in cls._processor_registry:
            processor_class = cls._processor_registry[processor_type]
            return processor_class(**params)
                
        raise ValueError(f"Invalid processor type: {processor_type}")
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[VideoProcessor]):
        cls._processor_registry[processor_type] = processor_class
    
    @classmethod
    def create_video_clip(cls, file_path: str) -> VideoClipInterface:
        return cls._video_clip_impl.load(file_path)
    
    @classmethod
    def set_video_clip_impl(cls, impl_class: Type[VideoClipInterface]) -> None:
        cls._video_clip_impl = impl_class


VideoProcessorFactory.register_processor("VideoRotator", AutoOrientationResolver)
VideoProcessorFactory.register_processor("AestheticProcessor", AestheticVideoProcessor)