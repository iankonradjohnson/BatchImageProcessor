import numpy as np
from PIL import Image

from python.src.processors.image_processor import ImageProcessor


class DualPageCropper(ImageProcessor):
    def __init__(self, config):
        self.left = config.get("left")
        self.right = config.get("right")

        # Initialize curr_page to self.left
        self.curr_page = self.left

    def process(self, img: Image) -> Image:
        img_array = np.array(img)

        x0 = self.curr_page.get("x0")
        y0 = self.curr_page.get("y0")
        x1 = self.curr_page.get("x1")
        y1 = self.curr_page.get("y1")

        # Toggle between left and right for the next process
        if self.curr_page == self.left:
            self.curr_page = self.right
        else:
            self.curr_page = self.left

        # Crop using numpy array slicing
        cropped_array = img_array[y0:y1, x0:x1]

        # Convert back to PIL Image
        cropped_img = Image.fromarray(cropped_array)

        return cropped_img
