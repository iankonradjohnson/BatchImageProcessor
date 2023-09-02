import os
import sys
import yaml
from concurrent.futures import ThreadPoolExecutor

from python.src.processors.book_processor import BookProcessor


def process_book(book_config, shared_processors):
    """Process a single book."""
    print(f"Processing book: {book_config['name']}")
    book_processor = BookProcessor(book_config, shared_processors)
    book_processor.process()


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>")
        return

    config_file = sys.argv[1]

    with open(config_file, "r") as config_stream:
        config_data = yaml.safe_load(config_stream)

    shared_processors = config_data.get("shared_processors", [])

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_book, book_config, shared_processors)
            for book_config in config_data.get("books", [])
        ]


if __name__ == "__main__":
    main()
