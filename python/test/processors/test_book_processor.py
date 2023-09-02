from concurrent.futures import ProcessPoolExecutor
from unittest import TestCase, mock

from python.src.processors.book_processor import BookProcessor
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class TestBookProcessor(TestCase):
    @mock.patch("os.listdir")
    @mock.patch.object(ProcessPoolExecutor, "submit")
    def test_process(self, mock_submit, mock_listdir):
        # Given
        book_config = {
            "image_directory": "/path/to/images",
            "save_directory": "/path/to/save",
            "processors": [{"type": "ImageRotator", "rotation_angle": 45}],
        }
        processor = BookProcessor(book_config)

        mock_listdir.return_value = ["image1.jpg", "image2.jpg"]

        # When
        processor.process_book()

        # Then
        expected_calls = [
            mock.call(
                processor._process_single_image, "/path/to/images/image1.jpg", True
            ),
            mock.call(
                processor._process_single_image, "/path/to/images/image2.jpg", False
            ),
        ]

        mock_submit.assert_has_calls(expected_calls)
        self.assertEqual(mock_submit.call_count, 2)
