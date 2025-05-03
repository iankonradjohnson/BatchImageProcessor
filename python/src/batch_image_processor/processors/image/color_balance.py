from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image, ImageEnhance


class ColorBalance(ImageProcessor):
    def __init__(self, config):
        self.red_balance = config.get("red", 1.0)
        self.green_balance = config.get("green", 1.0)
        self.blue_balance = config.get("blue", 1.0)

    def process(self, img: Image, is_left: bool = None) -> Image:
        img = img.convert("RGB")

        r, g, b = img.split()

        r = ImageEnhance.Brightness(r).enhance(self.red_balance)
        g = ImageEnhance.Brightness(g).enhance(self.green_balance)
        b = ImageEnhance.Brightness(b).enhance(self.blue_balance)

        return Image.merge("RGB", (r, g, b))
