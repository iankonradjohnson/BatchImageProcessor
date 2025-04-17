from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.batch.dual_page_processor import DualPageProcessor
from batch_image_processor.processors.single_page_processor import SinglePageProcessor


class BatchProcessorFactory:
    @staticmethod
    def create_batch_processor(config) -> BatchProcessor:
        processor_type = config.get("type")

        if processor_type == "DualPage":
            return DualPageProcessor(config)

        if processor_type == "SinglePage":
            return SinglePageProcessor(config)

        raise ValueError("Processor invalid")
