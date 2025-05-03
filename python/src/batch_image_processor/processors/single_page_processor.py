from batch_image_processor.processors.batch.batch_processor import BatchProcessor


class SinglePageProcessor(BatchProcessor):
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        processors: list,
        deleted_dir: str = None,
        copies: int = 1,
    ):
        super().__init__(input_dir, output_dir, processors, deleted_dir, copies)

    # Inherits batch_process from BatchProcessor
