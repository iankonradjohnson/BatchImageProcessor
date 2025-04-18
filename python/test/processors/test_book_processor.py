from concurrent.futures import ProcessPoolExecutor
from unittest import TestCase, mock

from batch_image_processor.processors.batch.dual_page_processor import DualPageProcessor


class TestBookProcessor(TestCase):
    def setUp(self) -> None:
        input_dir = "/path/to/input"
        output_dir = "/path/to/output"
        processors = [mock.MagicMock()]
        self.processor = DualPageProcessor(input_dir, output_dir, processors)

    @mock.patch("batch_image_processor.processors.batch.dual_page_processor.tqdm")
    @mock.patch.object(ProcessPoolExecutor, "submit")
    def test_process(self, mock_submit, mock_tqdm):
        # Set up mock tqdm
        mock_progress_bar = mock.MagicMock()
        mock_tqdm.return_value.__enter__.return_value = mock_progress_bar
        
        # When
        self.processor.batch_process(["image1.jpg", "image2.jpg"])

        # Then
        expected_calls = [
            mock.call(self.processor._process_single_image, "image1.jpg", True, 0),
            mock.call(
                self.processor._process_single_image,
                "image2.jpg",
                False,
                0,
            ),
        ]

        mock_submit.assert_has_calls(expected_calls)
        self.assertEqual(mock_submit.call_count, 2)
