from multiprocessing import Pool, cpu_count

from tqdm import tqdm

from batch_image_processor.processors.batch.batch_processor import BatchProcessor


class SinglePageProcessor(BatchProcessor):
    def __init__(self, input_dir: str, output_dir: str, processors: list, deleted_dir: str = None, copies: int = 1):
        super().__init__(input_dir, output_dir, processors, deleted_dir, copies)

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