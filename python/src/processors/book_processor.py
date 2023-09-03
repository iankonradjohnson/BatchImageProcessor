import os
from concurrent.futures import ProcessPoolExecutor

from python.src.factory.image_processor_factory import ImageProcessorFactory
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class BookProcessor:
    def __init__(self, book_config):
        self.book_config = book_config

    def _create_pipeline(self) -> ImagePipeline:
        processors = [
            ImageProcessorFactory.create_processor(config)
            for config in self.book_config["processors"]
        ]

        save_dir = self.book_config["save_directory"]
        return ImagePipeline(processors, save_dir)

    def _process_single_image(self, image_path: str, is_left: bool) -> None:
        pipeline = self._create_pipeline()
        pipeline.process_and_save_image(image_path, is_left)

    def process_book(self):
        """Process a single book based on the provided configuration."""

        input_dir = self.book_config["image_directory"]
        image_path_list = sorted(
            [
                os.path.join(input_dir, filename)
                for filename in os.listdir(
                    input_dir,
                )
            ]
        )
        image_path_list = [
            f for f in image_path_list if not os.path.basename(f).startswith(".")
        ]

        is_left = True
        with ProcessPoolExecutor() as executor:
            for image_path in image_path_list:
                executor.submit(self._process_single_image, image_path, is_left)
                is_left = not is_left
