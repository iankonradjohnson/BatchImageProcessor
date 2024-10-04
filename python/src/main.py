import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Pool, cpu_count

from tqdm import tqdm
import yaml

from python.src.factory.batch_processor_factory import BatchProcessorFactory
from python.src.processors.batch.dual_page_processor import DualPageProcessor


def worker(dir_config):
    """Process a single book."""
    try:
        input_dir = dir_config['input_dir']
        print(f"Processing directory: {input_dir}")
        batch_processor = BatchProcessorFactory.create_batch_processor(dir_config)

        filename_li = [f for f in get_all_files(input_dir) if not os.path.basename(f).startswith(".")]
        batch_processor.batch_process(filename_li)
    except Exception as exception:
        print(exception)
        print(traceback.format_exc())


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>")
        return

    config_file = sys.argv[1]

    with open(config_file, "r", encoding="utf-8") as config_stream:
        config_data = yaml.safe_load(config_stream)

    directory_list = config_data.get("directories", [])

    with tqdm(total=len(directory_list)) as pbar:
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(worker, item):
                    item for item in directory_list
            }
            for _ in as_completed(futures):
                pbar.update(1)


def get_all_files(directory):
    file_list = []
    for folder_name, sub_folders, filenames in os.walk(directory):
        for filename in filenames:
            file_list.append(os.path.join(folder_name, filename))
    return file_list


if __name__ == "__main__":
    main()
