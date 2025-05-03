import sys
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm
import yaml

from batch_image_processor.factory.batch_processor_factory import BatchProcessorFactory
from batch_image_processor.factory.image_processor_factory import ImageProcessorFactory


def worker(dir_config):
    """Process a single book."""
    try:
        processor_type = dir_config.get("type")
        input_dir = dir_config["input_dir"]
        output_dir = dir_config["output_dir"]
        deleted_dir = dir_config.get("deleted_dir", None)
        copies = dir_config.get("copies", 1)

        print(f"Processing directory: {input_dir}")

        processors = [
            ImageProcessorFactory.create_processor(processor_config)
            for processor_config in dir_config["processors"]
        ]

        batch_processor = BatchProcessorFactory.create_batch_processor(
            processor_type, input_dir, output_dir, processors, deleted_dir, copies
        )

        batch_processor.batch_process()
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
            futures = {executor.submit(worker, item): item for item in directory_list}
            for _ in as_completed(futures):
                pbar.update(1)


if __name__ == "__main__":
    main()
