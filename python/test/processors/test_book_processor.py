from unittest import TestCase, mock

from batch_image_processor.processors.batch.batch_processor import BatchProcessor


class TestBookProcessor(TestCase):
    def setUp(self) -> None:
        input_dir = "/path/to/input"
        output_dir = "/path/to/output"
        processors = [mock.MagicMock()]

        # First create the processor with a mock for _get_files_from_input_dir
        self.processor = BatchProcessor(input_dir, output_dir, processors)

        # Then manually set the filename_li attribute
        self.processor.filename_li = ["image1.jpg", "image2.jpg"]

    @mock.patch("batch_image_processor.processors.batch.batch_processor.tqdm")
    @mock.patch("batch_image_processor.processors.batch.batch_processor.Pool")
    def test_process(self, mock_pool_class, mock_tqdm):
        # Set up mock pool
        mock_pool = mock.MagicMock()
        mock_pool_class.return_value = mock_pool
        mock_apply_async = mock_pool.apply_async

        # Set up mock tqdm
        mock_progress_bar = mock.MagicMock()
        mock_tqdm.return_value = mock_progress_bar

        # When
        self.processor.batch_process()

        # Then
        expected_calls = [
            mock.call(
                self.processor._process_single_image,
                args=("image1.jpg", 0),
                callback=mock.ANY,
            ),
            mock.call(
                self.processor._process_single_image,
                args=("image2.jpg", 0),
                callback=mock.ANY,
            ),
        ]

        # Check that apply_async was called correctly
        self.assertEqual(mock_apply_async.call_count, 2)

        # Check that the pool was closed and joined
        mock_pool.close.assert_called_once()
        mock_pool.join.assert_called_once()
