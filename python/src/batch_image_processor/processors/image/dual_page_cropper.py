import numpy as np
from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class DualPageCropper(ImageProcessor):
    def __init__(
        self,
        left_left: int = None,
        left_top: int = None,
        right_left: int = None,
        right_top: int = None,
        width: int = None,
        height: int = None,
        **kwargs
    ):
        """
        Args:
            left_left: X-coordinate of the crop origin for the left page
            left_top: Y-coordinate of the crop origin for the left page
            right_left: X-coordinate of the crop origin for the right page
            right_top: Y-coordinate of the crop origin for the right page
            width: Width of the crop box
            height: Height of the crop box
        """
        self.left_left = left_left
        self.left_top = left_top
        self.right_left = right_left
        self.right_top = right_top
        self.width = width
        self.height = height

    def process(self, img: Image, is_left: bool = None) -> Image:
        img_array = np.array(img)

        if is_left is None or is_left:
            left = self.left_left
            top = self.left_top
        else:
            left = self.right_left
            top = self.right_top

        cropped_array = img_array[top : top + self.height, left : left + self.width]
        cropped_img = Image.fromarray(cropped_array)

        return cropped_img
