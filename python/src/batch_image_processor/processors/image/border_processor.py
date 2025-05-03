"""
A module implementing a processor for filling the border pixels of an image with white.

This module provides a BorderProcessor class that fills the border pixels
of specified dimensions with white.
"""

from PIL import Image, ImageDraw

from batch_image_processor.processors.image.image_processor import ImageProcessor


class BorderProcessor(ImageProcessor):
    """
    A processor for filling border pixels with white.

    This processor modifies the image by filling the border pixels with white.
    The border dimensions are specified in pixels.
    """

    def __init__(self, top: int = 0, bottom: int = 0, left: int = 0, right: int = 0):
        """
        Initialize the border processor with specified border dimensions.

        Args:
            top (int): Width of the top border in pixels.
            bottom (int): Width of the bottom border in pixels.
            left (int): Width of the left border in pixels.
            right (int): Width of the right border in pixels.
        """
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Fill border pixels with white.

        Args:
            img (Image): The input image.
            is_left (bool, optional): Unused parameter for compatibility with the base class.

        Returns:
            Image: The image with border pixels filled with white.
        """
        # Create a copy of the image to avoid modifying the original
        img_copy = img.copy()
        width, height = img_copy.size
        draw = ImageDraw.Draw(img_copy)
        
        # Get the white color value based on the image mode
        white_color = "white"
        if img_copy.mode == "1":
            white_color = 1
        elif img_copy.mode == "L":
            white_color = 255
        
        # Fill top border
        if self.top > 0:
            draw.rectangle([(0, 0), (width - 1, self.top - 1)], fill=white_color)
        
        # Fill bottom border
        if self.bottom > 0:
            draw.rectangle([(0, height - self.bottom), (width - 1, height - 1)], fill=white_color)
        
        # Fill left border
        if self.left > 0:
            draw.rectangle([(0, 0), (self.left - 1, height - 1)], fill=white_color)
        
        # Fill right border
        if self.right > 0:
            draw.rectangle([(width - self.right, 0), (width - 1, height - 1)], fill=white_color)
        
        return img_copy