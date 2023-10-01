import os
import random

import PIL.Image
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from tqdm import tqdm
from blend_modes import overlay

from python.src.processors.image.image_processor import ImageProcessor


class MoireProcessor(ImageProcessor):
    def __init__(self, config):
        self.config = config
        self.frequency_range = config.get("frequency_range", [0.1, 0.2])

    def process(self, img: Image, is_left: bool = None) -> Image:
        img = img.convert("RGBA")
        screen = self.create_screen(img.width, img.height)

        return self.blend_moire(img, screen)

    def blend_moire(self, original_image, moire_overlay):

        # original_image_gray = ImageOps.grayscale(original_image)
        #
        # threshold_value = self.config.get("threshold", 128)
        # original_image_thresholded = original_image_gray.point(lambda p: 255 if p > threshold_value else 0)
        #
        # mask = ImageOps.invert(original_image_thresholded)
        #
        # erased = self.erase_pixels_in_mask(moire_overlay, mask)
        #
        # return self.blend_overlay(original_image, erased, self.config.get("opacity", 0.5))
        return self.blend_overlay(original_image, moire_overlay, self.config.get("opacity", 0.5))

    def blend_overlay(self, original_image, overlay_image, opacity):
        original_image_np = np.array(original_image).astype(float)
        overlay_np = np.array(overlay_image).astype(float)

        blended_np = overlay(original_image_np, overlay_np, opacity)
        return Image.fromarray(np.uint8(blended_np))

    def create_screen(self, width, height) -> Image:
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        canvas[:, :, :] = (255, 255, 255, 255)

        frequency = random.uniform(self.frequency_range[0], self.frequency_range[1])

        num_lines = int(height * frequency)
        line_spacing = height // num_lines
        line_width = line_spacing // 2

        for i in range(0, num_lines):
            y = i * line_spacing
            canvas[int(y - line_width):int(y), :] = (0, 0, 0, 255)

        screen = Image.fromarray(canvas).convert("RGBA")
        screen = screen.filter(ImageFilter.GaussianBlur(radius=line_width * .5))
        return screen.convert('RGBA')

    def erase_pixels_in_mask(self, img: Image, mask: Image) -> Image:
        new_img = Image.new("RGBA", (img.width, img.height))
        for x in range(img.width):
            for y in range(img.height):
                mask_pixel = mask.getpixel((x, y))
                img_pixel = img.getpixel((x, y))
                if mask_pixel == 0:
                    new_img.putpixel((x, y), (255, 255, 255, 255))
                else:
                    new_img.putpixel((x, y), img_pixel)
        return new_img

# if __name__ == "__main__":
#     img = MoireProcessor({}).process(Image.new("RGBA", (100, 100)))
#     img.save("/Users/iankonradjohnson/base/abacus/BatchImageProcessor/test/out_moire/result.png")