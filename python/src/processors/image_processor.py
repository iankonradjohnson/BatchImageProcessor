"""
A module defining a base class for image processing.

This module introduces an `ImageProcessor` class intended to be a base class
for other image processing operations. The `process` method should be overridden
by derived classes to provide the actual image processing logic.
"""

from PIL import Image


class ImageProcessor:
    """
    A base class for image processing operations.

    This class should be inherited by other classes intended for specific
    image processing tasks. The derived classes should override the `process`
    method to implement the desired image operation.
    """

    def process(self, img: Image, is_left: bool) -> Image:
        """
        Process the input image.

        This method should be overridden by derived classes to provide
        specific image processing logic.

        Args:
        - img (Image): The input image to be processed.

        Returns:
        Image: The processed image.
        """
