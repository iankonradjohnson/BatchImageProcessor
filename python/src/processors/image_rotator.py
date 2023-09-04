from PIL import Image
from python.src.processors.image_processor import ImageProcessor


class ImageRotator(ImageProcessor):
    def __init__(self, config):
        self.left = config.get("left")
        self.right = config.get("right")

    def process(self, img: Image, is_left: bool) -> Image:
        angle = self.left.get("angle", 90) if is_left else self.right.get("angle", -90)

        return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
