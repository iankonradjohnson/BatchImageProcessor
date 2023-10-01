import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count

from tqdm import tqdm

from python.src.factory.image_processor_factory import ImageProcessorFactory
from python.src.processors.batch.batch_processor import BatchProcessor
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class DualPageProcessor(BatchProcessor):
    def __init__(self, config):
        super().__init__(config)

    def batch_process(self):
        """Process a single book based on the provided configuration."""

        filename_li = sorted(os.listdir(self.input_dir))
        filename_li = [
            f for f in filename_li if not os.path.basename(f).startswith(".")
        ]

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
