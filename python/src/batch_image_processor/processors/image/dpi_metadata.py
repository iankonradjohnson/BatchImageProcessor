from batch_image_processor.processors.image.image_processor import ImageProcessor

from PIL import Image


class DpiMetadata(ImageProcessor):
    def __init__(self, config):
        """
        Initializes the DPI metadata processor.

        Config options:
        - "dpi": int, desired DPI for the output image (default: 300)
        """
        self.dpi = config.get("dpi", 300)

    def process(self, img: Image) -> Image:
        """
        Updates the DPI metadata of an image without resizing its pixels.

        Args:
        - img (Image): The input PIL image.
        - Returns:
        - Image: Image with updated DPI metadata.
        """
        img.info["dpi"] = (self.dpi, self.dpi)  # Set DPI metadata
        return img
