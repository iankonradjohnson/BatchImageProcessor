import random

from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class ResizeProcessor(ImageProcessor):
    def __init__(self, config):
        self.resize_range = config.get("resize_range", [0.25, 0.25])
        self.resampling_method = config.get("resampling_method", "bilinear").lower()

        self.resampling_methods = {
            "bilinear": Image.BILINEAR,
            "nearest": Image.NEAREST,
        }

        self.resampling_method = self.resampling_methods.get(self.resampling_method, Image.BILINEAR)

    def process(self, img: Image, is_left: bool = None) -> Image:
        resize_factor = random.uniform(self.resize_range[0], self.resize_range[1])
        new_width = int(img.width * resize_factor)
        new_height = int(img.height * resize_factor)

        return img.resize((new_width, new_height), resample=self.resampling_method)