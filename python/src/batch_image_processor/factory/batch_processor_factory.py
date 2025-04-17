from batch_image_processor.factory.image_processor_factory import ImageProcessorFactory
from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.batch.dual_page_processor import DualPageProcessor
from batch_image_processor.processors.single_page_processor import SinglePageProcessor


class BatchProcessorFactory:
    @staticmethod
    def create_processor_from_config(config) -> BatchProcessor:
        processor_type = config.get("type")
        input_dir = config["input_dir"]
        output_dir = config["output_dir"]
        deleted_dir = config.get("deleted_dir", None)
        copies = config.get("copies", 1)
        
        processors = [
            ImageProcessorFactory.create_processor(processor_config)
            for processor_config in config["processors"]
        ]

        return BatchProcessorFactory.create_batch_processor(
            processor_type, input_dir, output_dir, processors, deleted_dir, copies
        )

    @staticmethod
    def create_batch_processor(
        processor_type: str, 
        input_dir: str, 
        output_dir: str, 
        processors: list,
        deleted_dir: str = None, 
        copies: int = 1
    ) -> BatchProcessor:
        if processor_type == "DualPage":
            return DualPageProcessor(input_dir, output_dir, processors, deleted_dir, copies)

        if processor_type == "SinglePage":
            return SinglePageProcessor(input_dir, output_dir, processors, deleted_dir, copies)

        raise ValueError("Processor invalid")
