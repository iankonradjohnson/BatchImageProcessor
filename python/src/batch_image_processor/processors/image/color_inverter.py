from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image, ImageOps


class ColorInverter(ImageProcessor):
    def __init__(self, config):
        self.config = config

    def process(self, img: Image) -> Image:
        # Check the image mode and convert if necessary
        if img.mode not in ["L", "RGB"]:
            # Convert to RGB mode before inverting
            img = img.convert("RGB")

        # Invert the colors of the image
        try:
            inverted_image = ImageOps.invert(img)
        except Exception as e:
            print(e)
            return img

        return inverted_image
