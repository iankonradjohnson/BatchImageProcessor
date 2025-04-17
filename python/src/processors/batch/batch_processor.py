import traceback

from factory.image_processor_factory import ImageProcessorFactory
from processors.pipeline.image_pipeline import ImagePipeline


class BatchProcessor:

    def __init__(self, config):
        self.config = config
        self.input_dir = config["input_dir"]
        self.output_dir = config["output_dir"]
        self.deleted_dir = config.get("deleted_dir", None)
        self.copies = config.get("copies", 1)

    def batch_process(self, filename_li):
        pass

    def _create_pipeline(self) -> ImagePipeline:
        processors = [
            ImageProcessorFactory.create_processor(config)
            for config in self.config["processors"]
        ]

        return ImagePipeline(processors, self.input_dir, self.output_dir, self.deleted_dir)

    def _process_single_image(self, filepath: str, is_left: bool = None, copy_num: int = None) -> None:
        try:
            pipeline = self._create_pipeline()
            pipeline.process_and_save_image(filepath, is_left, copy_num)
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())
