from PIL import Image
from python.src.processors.image_processor import ImageProcessor


class ImageRotator(ImageProcessor):
    def __init__(self, rotation_angle=0):
        self.rotation_angle = rotation_angle

    def process(self, img: Image, is_left: bool) -> Image:
        angle = self.rotation_angle * (1 if is_left else -1)
        return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
