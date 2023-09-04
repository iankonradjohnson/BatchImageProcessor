import os.path

import cv2
import numpy as np
from PIL import Image

from python.src.processors.image_processor import ImageProcessor


class ThresholdFilter(ImageProcessor):
    def __init__(self, config):
        self.min_thresh = config.get("min_thresh")
        self.max_thresh = config.get("max_thresh")
        self.save_path = config.get("save_path", None)

    def process(self, img: Image, is_left: bool) -> Image:
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
        average_threshold = int(cv2.mean(img_gray)[0])
        if self.min_thresh <= average_threshold <= self.max_thresh:
            return img

        if self.save_path:
            if not os.path.exists(self.save_path):
                os.mkdir(self.save_path)
            img.save(self.save_path)
        return None
