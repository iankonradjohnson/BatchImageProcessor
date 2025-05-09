"""
This package contains pipeline implementations for different media types.

It includes pipeline classes that orchestrate the workflow of loading media,
applying a series of processors, and saving the result.
"""

from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline, MediaPipeline

# Avoid circular import by not importing VideoPipeline here
# from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline

__all__ = ['ImagePipeline', 'MediaPipeline'] # 'VideoPipeline' removed to avoid circular import