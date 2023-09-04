import os.path
from typing import List

from PIL import Image, UnidentifiedImageError

from python.src.processors.image_processor import ImageProcessor


class ImagePipeline:
    def __init__(self, processors: List[ImageProcessor], input_dir, output_dir):
        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir

    def process_and_save_image(self, filename: str, is_left: bool) -> None:
        try:
            image_path = os.path.join(self.input_dir, filename)
            save_path = os.path.join(self.output_dir, filename)

            with Image.open(image_path) as img:
                for processor in self.processors:
                    img = processor.process(img, is_left)

                    # If image is none, this is a result of a filter and image should not be saved
                    if img is None:
                        return

                if not os.path.exists(self.output_dir):
                    os.mkdir(self.output_dir)

                img.save(save_path)

        except UnidentifiedImageError as error:
            print(error)
