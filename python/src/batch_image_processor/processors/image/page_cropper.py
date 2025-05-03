from typing import Optional
import cv2 as cv
import numpy as np
from PIL import Image

from batch_image_processor.processors.image.image_processor import ImageProcessor


class PageCropper(ImageProcessor):
    def __init__(
        self,
        padding: int = 6,
        threshold: int = 200,
        coverage_ratio: float = 0.10,
        debug: bool = False,
    ):
        self.padding = padding
        self.threshold = threshold
        self.coverage_ratio = coverage_ratio
        self.debug = debug

    def process(self, img: Image) -> Image:
        cv_img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
        cropped = self._detect_and_crop(cv_img)

        if cropped is None:
            if self.debug:
                print("[PageCropper] Detection failed — returning original image")
            return img.copy()

        return Image.fromarray(cv.cvtColor(cropped, cv.COLOR_BGR2RGB))

    def _detect_and_crop(self, img: np.ndarray) -> Optional[np.ndarray]:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        _, bin_img = cv.threshold(gray, self.threshold, 255, cv.THRESH_BINARY)

        row_sum = (bin_img > 0).sum(axis=1)
        col_sum = (bin_img > 0).sum(axis=0)
        h, w = bin_img.shape

        row_thresh = self.coverage_ratio * w
        col_thresh = self.coverage_ratio * h

        rows = np.where(row_sum > row_thresh)[0]
        cols = np.where(col_sum > col_thresh)[0]

        if rows.size == 0 or cols.size == 0:
            return None

        y0, y1 = rows[0], rows[-1] + 1
        x0, x1 = cols[0], cols[-1] + 1

        cropped = img[y0:y1, x0:x1]
        return self._safe_trim(cropped)

    def _safe_trim(self, img: np.ndarray) -> np.ndarray:
        if self.padding == 0:
            return img
        h, w = img.shape[:2]
        p = self.padding
        if h <= 2 * p or w <= 2 * p:
            return img
        return img[p : h - p, p : w - p]
