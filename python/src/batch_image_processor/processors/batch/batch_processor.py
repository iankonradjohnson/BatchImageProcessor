import os
import traceback
from multiprocessing import Pool, cpu_count
from typing import List, TypeVar, Generic, Type, Optional
from functools import partial

from tqdm import tqdm

from batch_image_processor.processors.media_processor import MediaProcessor
from batch_image_processor.processors.pipeline.image_pipeline import MediaPipeline, ImagePipeline

T = TypeVar('T')  # Generic type for the media being processed


class BatchProcessor(Generic[T]):

    def __init__(
        self, 
        input_dir: str, 
        output_dir: str, 
        processors: List[MediaProcessor[T]], 
        deleted_dir: str = None,
        pipeline_class: Type[MediaPipeline[T]] = ImagePipeline,
        parallel: bool = False
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.processors = processors
        self.deleted_dir = deleted_dir
        self.pipeline_class = pipeline_class
        self.parallel = parallel
        self.filename_li = self._get_files_from_input_dir()

    def batch_process(self):
        if self.parallel:
            self._process_in_parallel()
        else:
            for filename in tqdm(self.filename_li, desc="Processing files"):
                self._process_single_file(filename)

    def _process_in_parallel(self):
        num_workers = cpu_count()
        with Pool(processes=num_workers) as pool:
            list(tqdm(
                pool.imap(self._process_single_file, self.filename_li),
                total=len(self.filename_li),
                desc=f"Processing files in parallel ({num_workers} workers)"
            ))

    def _get_files_from_input_dir(self):
        file_list = []
        for folder_name, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                if not os.path.basename(filename).startswith("."):
                    file_list.append(os.path.join(folder_name, filename))
        return file_list

    def _process_single_file(self, filepath: str) -> None:
        try:
            pipeline = self.pipeline_class(self.processors, self.input_dir, self.output_dir, self.deleted_dir)
            pipeline.process_and_save(filepath)
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())
