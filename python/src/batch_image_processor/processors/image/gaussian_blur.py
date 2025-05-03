from PIL import Image, ImageFilter

from batch_image_processor.processors.image.image_processor import ImageProcessor


class GaussianBlur(ImageProcessor):
    def __init__(self, config):
        self.config = config

    def process(self, img: Image) -> Image:
        return img.filter(ImageFilter.GaussianBlur(radius=self.config.get("radius", 1)))
