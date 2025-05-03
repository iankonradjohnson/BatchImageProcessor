import os
import traceback
from multiprocessing import Pool, cpu_count
from typing import List, TypeVar, Generic, Type, Optional

from tqdm import tqdm

from batch_image_processor.processors.media_processor import MediaProcessor
from batch_image_processor.processors.pipeline.image_pipeline import MediaPipeline

T = TypeVar('T')  # Generic type for the media being processed


class BatchProcessor(Generic[T]):
    """
    A generic class for batch processing media files.
    
    This class handles the workflow of processing multiple files
    in parallel using a media pipeline. It is parameterized by the media type.
    """

    def __init__(
        self, 
        input_dir: str, 
        output_dir: str, 
        processors: List[MediaProcessor[T]], 
        deleted_dir: str = None, 
        copies: int = 1,
        pipeline_class: Type[MediaPipeline[T]] = None
    ):
        """
        Initialize the batch processor.
        
        Args:
            input_dir: Directory containing input files
            output_dir: Directory to save processed files
            processors: List of media processors to apply
            deleted_dir: Directory to save filtered files (optional)
            copies: Number of copies to generate
            pipeline_class: The specific MediaPipeline class to use
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.processors = processors
        self.deleted_dir = deleted_dir
        self.pipeline_class = pipeline_class
        self.filename_li = self._get_files_from_input_dir()

    def batch_process(self):
        """
        Process all files in the input directory in parallel.
        """
        pbar = tqdm(
            total=len(self.filename_li), unit="file", desc="Processing"
        )
        pool = Pool(cpu_count())
        for filename in self.filename_li:
            pool.apply_async(
                self._process_single_file,
                args=(filename,),
                callback=lambda arg: pbar.update(1)
            )
        pool.close()
        pool.join()
        pbar.close()

    def _get_files_from_input_dir(self):
        """
        Get all files from input directory, excluding hidden files.
        
        Returns:
            List of file paths relative to input_dir
        """
        file_list = []
        for folder_name, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                if not os.path.basename(filename).startswith("."):
                    file_list.append(os.path.join(folder_name, filename))
        return file_list

    def _process_single_file(self, filepath: str) -> None:
        """
        Process a single file using the media pipeline.
        
        Args:
            filepath: Path to the file relative to input_dir
        """
        try:
            pipeline = self.pipeline_class(self.processors, self.input_dir, self.output_dir, self.deleted_dir)
            pipeline.process_and_save(filepath)
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())
