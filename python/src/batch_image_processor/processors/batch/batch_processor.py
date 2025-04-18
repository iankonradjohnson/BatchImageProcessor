import os
import traceback

from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline


class BatchProcessor:

    def __init__(self, input_dir: str, output_dir: str, processors: list, deleted_dir: str = None, copies: int = 1):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.processors = processors
        self.deleted_dir = deleted_dir
        self.copies = copies
        self.filename_li = self._get_files_from_input_dir()

    def batch_process(self):
        pass

    def _get_files_from_input_dir(self):
        """Get all files from input directory, excluding hidden files"""
        file_list = []
        for folder_name, _, filenames in os.walk(self.input_dir):
            for filename in filenames:
                if not os.path.basename(filename).startswith("."):
                    file_list.append(os.path.join(folder_name, filename))
        return file_list

    def _create_pipeline(self) -> ImagePipeline:
        return ImagePipeline(self.processors, self.input_dir, self.output_dir, self.deleted_dir)

    def _process_single_image(self, filepath: str, is_left: bool = None, copy_num: int = None) -> None:
        try:
            pipeline = self._create_pipeline()
            pipeline.process_and_save_image(filepath, is_left, copy_num)
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())
