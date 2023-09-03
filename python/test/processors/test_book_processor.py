from concurrent.futures import ProcessPoolExecutor
from unittest import TestCase, mock

from python.src.processors.book_processor import BookProcessor
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class TestBookProcessor(TestCase):
    def setUp(self) -> None:
        book_config = {
            "image_directory": "/path/to/images",
            "save_directory": "/path/to/save",
            "processors": [{"type": "ImageRotator"}],
        }
        self.processor = BookProcessor(book_config)

    @mock.patch("os.listdir")
    @mock.patch.object(ProcessPoolExecutor, "submit")
    def test_process(self, mock_submit, mock_listdir):
        mock_listdir.return_value = ["image1.jpg", "image2.jpg"]

        # When
        self.processor.process_book()

        # Then
        expected_calls = [
            mock.call(
                self.processor._process_single_image, "/path/to/images/image1.jpg", True
            ),
            mock.call(
                self.processor._process_single_image,
                "/path/to/images/image2.jpg",
                False,
            ),
        ]

        mock_submit.assert_has_calls(expected_calls)
        self.assertEqual(mock_submit.call_count, 2)

    def test_create_pipeline(self):
        image_pipeline = self.processor._create_pipeline()
