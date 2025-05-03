"""
A module defining a base class for image processing.

This module introduces an `ImageProcessor` class intended to be a base class
for other image processing operations. The `process` method should be overridden
by derived classes to provide the actual image processing logic.
"""

from PIL import Image
from typing import Dict, Any, Optional

from batch_image_processor.processors.media_processor import MediaProcessor


class ImageProcessor(MediaProcessor[Image.Image]):
    """
    A base class for image processing operations that extends MediaProcessor.

    This class specializes MediaProcessor for PIL Image objects and should be 
    inherited by classes that perform specific image processing tasks.
    The derived classes should override the `process` method to implement
    the desired image operation.
    """

    def process(self, img: Image.Image) -> Image.Image:
        """
        Process the input image.

        This method should be overridden by derived classes to provide
        specific image processing logic.

        Args:
            img: The input PIL image to be processed.

        Returns:
            The processed PIL image.
        """
        # Default implementation for base class
        return img
