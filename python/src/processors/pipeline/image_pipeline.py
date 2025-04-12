import os.path
from typing import List

from PIL import Image, UnidentifiedImageError

from python.src.processors.image.image_processor import ImageProcessor

Image.MAX_IMAGE_PIXELS = None

class ImagePipeline:
    def __init__(self, processors: List[ImageProcessor], input_dir, output_dir, deleted_dir):
        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.deleted_dir = deleted_dir

    def process_and_save_image(self, filepath: str, is_left: bool = None, copy_num: int = 1) -> None:
        try:
            split = os.path.basename(filepath).split('.')
            basename, ext = '.'.join(split[:-1]), split[-1]
            image_path = os.path.join(self.input_dir, filepath)
            save_path = os.path.join(
                self.output_dir,
                f"{basename}.png")

            with Image.open(image_path) as img:
                if not self.is_image(image_path):
                    return
                for processor in self.processors:
                    original_img = img
                    img = processor.process(img, is_left)

                    # If image is none, this is a result of a filter and image should not be saved
                    if img is None:
                        if self.deleted_dir:  # Check if deleted_dir is not None
                            if not os.path.exists(self.deleted_dir):
                                os.mkdir(self.deleted_dir)

                            filename = os.path.basename(filepath)
                            original_img.save(os.path.join(self.deleted_dir, filename))
                        return

                if not os.path.exists(self.output_dir):
                    os.mkdir(self.output_dir)

                img.save(save_path)

        except UnidentifiedImageError as error:
            print(error)

    def is_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                # Attempt to load the image to ensure it's valid
                img.verify()
            return True
        except (IOError, FileNotFoundError, Exception):
            # If an error occurs, it's likely not an image file that PIL can recognize
            return False
