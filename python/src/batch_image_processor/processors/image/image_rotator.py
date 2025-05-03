from PIL import Image
from batch_image_processor.processors.image.image_processor import ImageProcessor


class ImageRotator(ImageProcessor):
    def __init__(self, config):
        self.config = config
        self.left = config.get("left")
        self.right = config.get("right")

    def process(self, img: Image) -> Image:
        # Use the config directly now that we don't have left/right pages
        curr_page = self.config
        angle = curr_page.get("angle", 0)

        return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
