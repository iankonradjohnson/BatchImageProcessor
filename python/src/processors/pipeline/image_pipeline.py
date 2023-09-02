import os.path
from typing import List

from PIL import Image, UnidentifiedImageError

from python.src.processors.image_processor import ImageProcessor


class ImagePipeline:
    def __init__(self, processors: List[ImageProcessor], save_dir: str = None):
        self.processors = processors
        self.save_dir = save_dir

    def process_and_save_image(self, img_path: str):
        try:
            with Image.open(img_path) as img:
                for processor in self.processors:
                    img = processor.process(img)

                if not os.path.exists(self.save_dir):
                    os.mkdir(self.save_dir)

                img.save(self.get_save_path(img_path))

        except UnidentifiedImageError as e:
            print(e)

    def get_save_path(self, img_path: str) -> str:
        if self.save_dir is None:
            return img_path
        else:
            return os.path.join(self.save_dir, os.path.basename(img_path))
