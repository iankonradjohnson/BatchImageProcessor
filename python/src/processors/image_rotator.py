from PIL import Image
from python.src.processors.image_processor import ImageProcessor


class ImageRotator(ImageProcessor):
    def __init__(self, rotation_angle=0):
        self.rotation_angle = rotation_angle

    def process(self, img: Image) -> Image:
        return img.rotate(
            self.rotation_angle, resample=Image.Resampling.BICUBIC, expand=True
        )
