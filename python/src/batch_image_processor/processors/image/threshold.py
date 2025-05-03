import numpy as np
from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class MoireProcessor(ImageProcessor):
    def __init__(self, config):
        self.config = config

    def process(self, img: Image) -> Image:
        img = img.convert("RGBA")
        screen = self.create_screen(img.width, img.height)
        return Image.blend(img, screen, 0.25)

    def create_screen(self, width, height) -> Image:
        canvas = np.ones((height, width)) * 255

        num_lines = height // 5
        line_spacing = height // num_lines
        width = line_spacing // 2

        # Draw evenly spaced horizontal lines with subpixel precision
        for i in range(0, num_lines):
            y = i * line_spacing
            canvas[int(y - width) : int(y), :] = 0

        screen = Image.fromarray(canvas)
        return screen.convert("RGBA")
