from python.src.processors.image.image_processor import ImageProcessor
from PIL import Image, ImageOps, ImageEnhance


from PIL import Image, ImageOps

from PIL import Image, ImageEnhance

class BrightnessContrast(ImageProcessor):
    def __init__(self, config):
        """
        Initializes the brightness and contrast adjustment processor.

        Config options:
        - "brightness": float, default 1.0 (1.0 = no change, <1.0 = darker, >1.0 = brighter)
        - "contrast": float, default 1.0 (1.0 = no change, <1.0 = less contrast, >1.0 = more contrast)
        """
        self.brightness = config.get("brightness", 1.0)
        self.contrast = config.get("contrast", 1.0)

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Adjusts brightness and contrast of the image.

        Args:
        - img (Image): The input PIL image.
        - is_left (bool, optional): Unused, but kept for API consistency.

        Returns:
        - Image: Adjusted image with brightness and contrast applied.
        """
        # Apply brightness adjustment
        if self.brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(self.brightness)

        # Apply contrast adjustment
        if self.contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(self.contrast)

        return img





