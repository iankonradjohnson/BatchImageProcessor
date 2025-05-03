from PIL import Image
from typing import Optional

from batch_image_processor.processors.image.image_processor import ImageProcessor


class ThresholdProcessor(ImageProcessor):
    def __init__(self, threshold_value: int = 128):
        self.threshold_value = threshold_value

    def process(self, img: Image) -> Image:
        img_gray = img.convert("L")
        return img_gray.point(lambda p: p > self.threshold_value and 255)
