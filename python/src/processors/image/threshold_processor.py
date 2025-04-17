from PIL import Image
import numpy as np

from processors.image.image_processor import ImageProcessor


class ThresholdProcessor(ImageProcessor):

    def __init__(self, config):
        self.threshold_value = config.get("threshold_value", 128)

    def process(self, img: Image, is_left: bool = None) -> Image:
        img_gray = img.convert("L")
        return img_gray.point(lambda p: p > self.threshold_value and 255)