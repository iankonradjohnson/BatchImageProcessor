from python.src.processors.image_processor import ImageProcessor
from PIL import Image


class ImageRotator(ImageProcessor):

    def __init__(self, rotation_angle=0):
        self.rotation_angle = rotation_angle

    def process(self, img: Image) -> Image:
        return img.rotate(self.rotation_angle, resample=Image.BICUBIC, expand=True)


