import cv2
import numpy as np
import os
from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class ThresholdFilter(ImageProcessor):
    def __init__(
        self, min_thresh: float = 0, max_thresh: float = 255, blank_dir: str = None
    ):
        self.min_thresh = min_thresh
        self.max_thresh = max_thresh
        self.blank_dir = blank_dir

    def process(self, img: Image, is_left: bool = None) -> Image:
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        _, binary_image = cv2.threshold(img_cv2, 128, 255, cv2.THRESH_BINARY)
        average_threshold = cv2.mean(binary_image)[0]
        if self.min_thresh <= average_threshold <= self.max_thresh:
            return img

        # If we have a blank_dir, save the image there
        if self.blank_dir:
            if not os.path.exists(self.blank_dir):
                os.mkdir(self.blank_dir)
            img.save(self.blank_dir)

        return None
