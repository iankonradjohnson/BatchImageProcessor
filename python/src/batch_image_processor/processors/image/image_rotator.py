from PIL import Image
from batch_image_processor.processors.image.image_processor import ImageProcessor


class ImageRotator(ImageProcessor):
    def __init__(self, config):
        self.config = config
        self.left = config.get("left")
        self.right = config.get("right")

    def process(self, img: Image, is_left: bool = None) -> Image:
        # Toggle between left and right for the next process
        if is_left is None:
            curr_page = self.config
        elif is_left:
            curr_page = self.left
        else:
            curr_page = self.right

        angle = curr_page["angle"]

        return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
