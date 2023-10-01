import os.path
from typing import List

from PIL import Image, UnidentifiedImageError

from python.src.processors.image.image_processor import ImageProcessor


class ImagePipeline:
    def __init__(self, processors: List[ImageProcessor], input_dir, output_dir, deleted_dir):
        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.deleted_dir = deleted_dir

    def process_and_save_image(self, filename: str, is_left: bool = None, copy_num: int = 1) -> None:
        try:
            basename, ext = filename.split('.')
            image_path = os.path.join(self.input_dir, filename)
            save_path = os.path.join(
                self.output_dir,
                f"{basename}_{str.zfill(str(copy_num), 3)}.png")

            with Image.open(image_path) as img:
                for processor in self.processors:
                    original_iage = img
                    img = processor.process(img, is_left)

                    # If image is none, this is a result of a filter and image should not be saved
                    if img is None:
                        if not os.path.exists(self.deleted_dir):
                            os.mkdir(self.deleted_dir)

                        original_iage.save(os.path.join(self.deleted_dir, filename))
                        return

                if not os.path.exists(self.output_dir):
                    os.mkdir(self.output_dir)

                img.save(save_path)

        except UnidentifiedImageError as error:
            print(error)
