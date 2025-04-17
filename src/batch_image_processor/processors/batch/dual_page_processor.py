from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm

from batch_image_processor.processors.batch.batch_processor import BatchProcessor


class DualPageProcessor(BatchProcessor):
    def __init__(self, input_dir: str, output_dir: str, processors: list, deleted_dir: str = None, copies: int = 1):
        super().__init__(input_dir, output_dir, processors, deleted_dir, copies)

    def batch_process(self, filename_li):
        """Process a single book based on the provided configuration."""

        is_left = True
        with tqdm(total=len(filename_li * self.copies)) as pbar:
            with ProcessPoolExecutor() as executor:
                futures = {}

                for filename in filename_li:
                    for copy_num in range(self.copies):
                        futures.update({
                            executor.submit(self._process_single_image, filename, is_left, copy_num): filename})
                    is_left = not is_left
                for _ in as_completed(futures):
                    pbar.update(1)
