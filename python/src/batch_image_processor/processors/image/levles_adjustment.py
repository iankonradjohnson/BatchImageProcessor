from batch_image_processor.processors.image.image_processor import ImageProcessor

import numpy as np
from PIL import Image


class LevelsAdjustment(ImageProcessor):
    def __init__(self, config):
        """
        Initializes the Levels Adjustment processor.

        Config options:
        - "black_point": int (0-255) - Defines the darkest point (default: 0)
        - "white_point": int (0-255) - Defines the brightest point (default: 255)
        - "gamma": float (>0) - Adjusts midtones (default: 1.0)
        """
        self.black_point = config.get("black_point", 0)
        self.white_point = config.get("white_point", 255)
        self.gamma = config.get("gamma", 1.0)

        # Ensure valid input ranges
        if not (0 <= self.black_point < self.white_point <= 255):
            raise ValueError(
                "black_point must be < white_point, and both must be between 0-255."
            )
        if self.gamma <= 0:
            raise ValueError("gamma must be greater than 0.")

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Adjusts the levels of an image like Photoshop's Levels tool.

        Args:
        - img (Image): The input PIL image.
        - is_left (bool, optional): Unused, but kept for API consistency.

        Returns:
        - Image: Processed image with Levels applied.
        """
        img = img.convert("RGB")  # Ensure image is in RGB mode
        img_array = np.array(img, dtype=np.float32)

        # Normalize pixel values between 0 and 1
        img_array = (img_array - self.black_point) / (
            self.white_point - self.black_point
        )
        img_array = np.clip(img_array, 0, 1)  # Clip to valid range

        # Apply gamma correction
        img_array = img_array ** (1.0 / self.gamma)

        # Scale back to 0-255
        img_array = (img_array * 255).astype(np.uint8)

        return Image.fromarray(img_array)
