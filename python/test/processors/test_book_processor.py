from concurrent.futures import ProcessPoolExecutor
from unittest import TestCase, mock

from processors.batch.dual_page_processor import DualPageProcessor


class TestBookProcessor(TestCase):
    def setUp(self) -> None:
        book_config = {
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "processors": [{"type": "ImageRotator"}],
        }
        self.processor = DualPageProcessor(book_config)

    @mock.patch("os.listdir")
    @mock.patch.object(ProcessPoolExecutor, "submit")
    def test_process(self, mock_submit, mock_listdir):
        # When
        self.processor.batch_process(["image1.jpg", "image2.jpg"])

        # Then
        expected_calls = [
            mock.call(self.processor._process_single_image, "image1.jpg", True),
            mock.call(
                self.processor._process_single_image,
                "image2.jpg",
                False,
            ),
        ]

        mock_submit.assert_has_calls(expected_calls)
        self.assertEqual(mock_submit.call_count, 2)
