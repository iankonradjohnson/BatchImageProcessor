import numpy as np
from PIL import Image

from python.src.processors.image_processor import ImageProcessor


class DualPageCropper(ImageProcessor):
    def __init__(self, config):
        self.left = config.get("left")
        self.right = config.get("right")
        self.image_size = config.get("image_size")

    def process(self, img: Image, is_left: bool) -> Image:
        img_array = np.array(img)

        # Toggle between left and right for the next process
        curr_page = self.left if is_left else self.right

        x_start = curr_page.get("x_start")
        y_start = curr_page.get("y_start")
        width = self.image_size.get("width")
        height = self.image_size.get("height")

        # Crop using numpy array slicing
        cropped_array = img_array[y_start : y_start + height, x_start : x_start + width]

        # Convert back to PIL Image
        cropped_img = Image.fromarray(cropped_array)

        return cropped_img
