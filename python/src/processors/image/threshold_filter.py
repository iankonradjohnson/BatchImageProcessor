import os

import cv2
import numpy as np
from PIL import Image

from processors.image.image_processor import ImageProcessor


class ThresholdFilter(ImageProcessor):
    def __init__(self, config):
        self.min_thresh = config.get("min_thresh")
        self.max_thresh = config.get("max_thresh")
        self.blank_dir = config.get("deleted_dir")

    def process(self, img: Image, is_left: bool = None) -> Image:
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        _, binary_image = cv2.threshold(img_cv2, 128, 255, cv2.THRESH_BINARY)
        average_threshold = cv2.mean(binary_image)[0]
        if self.min_thresh <= average_threshold <= self.max_thresh:
            return img

        return None
