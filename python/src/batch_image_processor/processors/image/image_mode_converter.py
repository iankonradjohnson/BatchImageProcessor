from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image


class ImageModeConverter(ImageProcessor):
    def __init__(self, config):
        self.target_mode = config.get("mode", "RGB")

    def process(self, img: Image) -> Image:
        return img.convert(self.target_mode)
