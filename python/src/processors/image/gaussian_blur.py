import os
import random

import PIL.Image
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from tqdm import tqdm
from blend_modes import overlay

from python.src.processors.image.image_processor import ImageProcessor


class GaussianBlur(ImageProcessor):
    def __init__(self, config):
        self.config = config

    def process(self, img: Image, is_left: bool = None) -> Image:
        return img.filter(ImageFilter.GaussianBlur(radius = self.config.get("radius", 1)))
