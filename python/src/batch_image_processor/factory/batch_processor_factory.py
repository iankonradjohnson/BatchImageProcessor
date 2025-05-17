"""
A factory for creating batch processors.

This module provides a factory pattern for creating batch processors
based on configuration.
"""

from typing import List

from PIL import Image

from batch_image_processor.processors.media_processor import MediaProcessor
# Import BatchProcessor at function level to avoid circular import
# from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline
from batch_image_processor.processors.video.video_clip import VideoClipInterface


class BatchProcessorFactory:
    """
    Factory for creating batch processors for media files.
    
    This class provides static methods for creating batch processors
    configured for different media types.
    """

    @classmethod
    def create_batch_processor(
        cls,
        processor_type: str,
        input_dir: str,
        output_dir: str,
        processors: List[MediaProcessor],
        deleted_dir: str = None,
        copies: int = 1,
        parallel: bool = False,
    ):
        """
        Create a batch processor based on the specified type.
        
        Args:
            processor_type: Type of batch processor to create
            input_dir: Directory containing input files
            output_dir: Directory to save processed files
            processors: List of media processors to apply
            deleted_dir: Directory to save filtered files (optional)
            copies: Number of copies to generate
            parallel: If True, process files in parallel using multiprocessing
            
        Returns:
            A BatchProcessor instance.
            
        Raises:
            ValueError: If the processor type is invalid or not supported.
        """
        # Import here to avoid circular import
        from batch_image_processor.processors.batch.batch_processor import BatchProcessor
        
        # Handle SinglePage, DualPage (for backward compatibility), and ImageBatch
        if processor_type in ("Image"):
            return BatchProcessor[Image.Image](
                input_dir, output_dir, processors, deleted_dir, 
                pipeline_class=ImagePipeline,
                parallel=parallel
            )
        elif processor_type in ("video"):
            # Import VideoPipeline here to avoid circular imports
            from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline
            return BatchProcessor[VideoClipInterface](
                input_dir, output_dir, processors, deleted_dir, 
                pipeline_class=VideoPipeline,
                parallel=parallel
            )

        raise ValueError(f"Invalid processor type: {processor_type}")
