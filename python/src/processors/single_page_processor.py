import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool, cpu_count

from tqdm import tqdm

from python.src.processors.batch.batch_processor import BatchProcessor


class SinglePageProcessor(BatchProcessor):
    def __init__(self, config):
        super().__init__(config)

    def batch_process(self, filename_li):
        """Process a single book based on the provided configuration."""

        pbar = tqdm(total=len(filename_li * self.copies), unit='image', desc='Extract')
        pool = Pool(cpu_count())
        for filename in filename_li:
            for copy_num in range(self.copies):
                pool.apply_async(self._process_single_image, args=(filename, None, copy_num), callback=lambda arg: pbar.update(1))
        pool.close()
        pool.join()
        pbar.close()