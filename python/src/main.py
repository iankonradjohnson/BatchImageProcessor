import sys
import traceback
from concurrent.futures import ProcessPoolExecutor

import yaml

from python.src.processors.book_processor import BookProcessor


def process_book(book_config, config_data):
    """Process a single book."""
    print(f"Processing book: {book_config['name']}")
    book_processor = BookProcessor(
        book_config, config_data.get("input_dir"), config_data.get("output_dir")
    )

    try:
        book_processor.process_book()
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

    with ProcessPoolExecutor() as executor:
        for book_config in config_data.get("books", []):
            executor.submit(process_book, book_config, config_data)


if __name__ == "__main__":
    main()
