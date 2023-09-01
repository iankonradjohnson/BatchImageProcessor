import os
from concurrent.futures.thread import ThreadPoolExecutor
from python.src.factory.image_processor_factory import ImageProcessorFactory
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class BookProcessor:
    def __init__(self, book_config, shared_processors):
        self.book_config = book_config
        self.shared_processors = shared_processors

    def _create_pipeline(self):
        # Combine shared processors with book-specific processors
        processors = [ImageProcessorFactory.create_processor(config) for config in self.shared_processors]
        processors.extend([ImageProcessorFactory.create_processor(config) for config in self.book_config["processors"]])

        save_dir = self.book_config["save_directory"]
        return ImagePipeline(processors, save_dir)

    def _process_single_image(self, image_path):
        pipeline = self._create_pipeline()
        pipeline.process_and_save_image(image_path)

    def process(self):
        """Process a single book based on the provided configuration."""

        input_dir = self.book_config["image_directory"]
        image_path_list = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir)]

        with ThreadPoolExecutor() as executor:
            list(executor.map(self._process_single_image, image_path_list))
