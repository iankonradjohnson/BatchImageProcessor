from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image
from typing import Dict, Any


class ImageModeConverter(ImageProcessor):
    def __init__(self, mode: str = "RGB", **kwargs):
        self.target_mode = mode
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ImageModeConverter":
        return cls(mode=config.get("mode", "RGB"))

    def process(self, img: Image) -> Image:
        return img.convert(self.target_mode)
