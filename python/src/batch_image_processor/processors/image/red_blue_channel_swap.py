from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class RedBlueChannelSwap(ImageProcessor):
    def __init__(self, config=None):
        self.config = config

    def process(self, img: Image, is_left: bool = None) -> Image:
        img = img.convert('RGB')
        r, g, b = img.split()
        return Image.merge('RGB', (b, g, r))
