import cv2
import numpy as np
from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image, ImageEnhance


class VibranceSaturation(ImageProcessor):
    def __init__(self, config):
        self.vibrance = config.get("vibrance", 1.0)
        self.saturation = config.get("saturation", 1.0)

    def process(self, img: Image) -> Image:
        img = img.convert("RGB")
        img = ImageEnhance.Color(img).enhance(self.saturation)
        img_np = np.array(img)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        if self.vibrance != 1.0:
            img_np = self.adjust_vibrance(img_np, self.vibrance)

        img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img_np)

        return img

    def adjust_vibrance(self, img_np: np.array, vibrance_factor: float) -> np.array:
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = s.astype(np.float32) / 255.0
        mask = cv2.inRange(s, 0, 0.5)
        mask_inv = cv2.bitwise_not(mask)
        s[mask > 0] *= vibrance_factor
        s[mask_inv > 0] *= 1 + (vibrance_factor - 1) * 0.3
        s = np.clip(s, 0, 1)
        s = (s * 255).astype(np.uint8)
        hsv_adjusted = cv2.merge([h, s, v])
        result = cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)

        return result
