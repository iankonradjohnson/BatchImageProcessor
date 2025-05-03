import numpy as np
from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class DualPageCropper(ImageProcessor):
    def __init__(
        self,
        left: int = None,
        top: int = None,
        width: int = None,
        height: int = None,
        **kwargs
    ):
        """
        Args:
            left: X-coordinate of the crop origin
            top: Y-coordinate of the crop origin
            width: Width of the crop box
            height: Height of the crop box
        """
        # For backward compatibility, handle old parameter names
        self.left = kwargs.get("left_left", left)
        self.top = kwargs.get("left_top", top)
        self.width = width
        self.height = height

    def process(self, img: Image) -> Image:
        img_array = np.array(img)

        cropped_array = img_array[
            self.top : self.top + self.height, self.left : self.left + self.width
        ]
        cropped_img = Image.fromarray(cropped_array)

        return cropped_img
