from processors.image.image_processor import ImageProcessor
from PIL import Image, ImageOps


class ImageModeConverter(ImageProcessor):
    def __init__(self, config):
        self.target_mode = config.get("mode", "RGB")

    def process(self, img: Image, is_left: bool = None) -> Image:
        return img.convert(self.target_mode)
