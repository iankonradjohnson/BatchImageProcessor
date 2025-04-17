from PIL import Image

from processors.image.image_processor import ImageProcessor


class Greyscale(ImageProcessor):
    def __init__(self, config):
        self.config = config

    def process(self, img: Image, is_left: bool = None) -> Image:
        return img.convert("L")
