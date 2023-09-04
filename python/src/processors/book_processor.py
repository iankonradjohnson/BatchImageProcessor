import os
import traceback
from concurrent.futures import ProcessPoolExecutor

from python.src.factory.image_processor_factory import ImageProcessorFactory
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class BookProcessor:
    def __init__(self, book_config, input_dir, output_dir):
        self.book_config = book_config
        self.book_name = book_config.get("name")
        self.input_book_dir = os.path.join(input_dir, self.book_name)
        self.output_book_dir = os.path.join(output_dir, self.book_name)

    def _create_pipeline(self) -> ImagePipeline:
        processors = [
            ImageProcessorFactory.create_processor(config)
            for config in self.book_config["processors"]
        ]

        return ImagePipeline(processors, self.input_book_dir, self.output_book_dir)

    def _process_single_image(self, filename: str, is_left: bool) -> None:
        try:
            pipeline = self._create_pipeline()
            pipeline.process_and_save_image(filename, is_left)
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())

    def process_book(self):
        """Process a single book based on the provided configuration."""

        filename_li = sorted(os.listdir(self.input_book_dir))
        filename_li = [
            f for f in filename_li if not os.path.basename(f).startswith(".")
        ]

        is_left = True
        with ProcessPoolExecutor() as executor:
            for filename in filename_li:
                executor.submit(self._process_single_image, filename, is_left)
                is_left = not is_left
