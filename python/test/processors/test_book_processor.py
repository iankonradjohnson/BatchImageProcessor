import os
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, call

from PIL import Image

from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline


class TestBookProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.input_dir = "/path/to/input"
        self.output_dir = "/path/to/output"
        self.deleted_dir = "/path/to/deleted"
        self.processors = [mock.MagicMock()]
        self.pipeline_class = MagicMock(spec=ImagePipeline)

        # First create the processor with a patch for _get_files_from_input_dir
        # to avoid file system operations during testing
        with patch.object(BatchProcessor, "_get_files_from_input_dir") as mock_get_files:
            mock_get_files.return_value = ["image1.jpg", "image2.jpg"]
            self.processor = BatchProcessor(
                self.input_dir, 
                self.output_dir, 
                self.processors,
                self.deleted_dir,
                pipeline_class=self.pipeline_class
            )

    @mock.patch("batch_image_processor.processors.batch.batch_processor.tqdm")
    @mock.patch("batch_image_processor.processors.batch.batch_processor.Pool")
    def test_batch_process(self, mock_pool_class, mock_tqdm):
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
        # Check that apply_async was called for each file
        self.assertEqual(mock_apply_async.call_count, 2)
        
        # Verify that the calls have correct arguments
        calls = [
            call(self.processor._process_single_file, args=("image1.jpg",), callback=mock.ANY),
            call(self.processor._process_single_file, args=("image2.jpg",), callback=mock.ANY)
        ]
        mock_apply_async.assert_has_calls(calls, any_order=True)

        # Check that the pool was closed and joined
        mock_pool.close.assert_called_once()
        mock_pool.join.assert_called_once()
        
        # Check tqdm was properly initialized and closed
        mock_tqdm.assert_called_once_with(total=2, unit="file", desc="Processing")
        mock_progress_bar.close.assert_called_once()

    @patch("os.walk")
    def test_get_files_from_input_dir(self, mock_walk):
        # Set up mock walk to return some files
        mock_walk.return_value = [
            ("/path/to/input", ["subdir"], ["file1.jpg", ".hidden.jpg", "file2.png"]),
            ("/path/to/input/subdir", [], ["file3.jpg", ".hidden2.jpg"])
        ]

        # Create a fresh processor to test _get_files_from_input_dir directly
        processor = BatchProcessor(self.input_dir, self.output_dir, self.processors)
        
        # Call the method directly
        files = processor._get_files_from_input_dir()
        
        # Check the result excludes hidden files
        expected_files = [
            os.path.join("/path/to/input", "file1.jpg"),
            os.path.join("/path/to/input", "file2.png"),
            os.path.join("/path/to/input/subdir", "file3.jpg")
        ]
        self.assertEqual(set(files), set(expected_files))
    
    def test_process_single_file_success(self):
        # Arrange
        filepath = "test/image.jpg"
        mock_pipeline = MagicMock()
        self.pipeline_class.return_value = mock_pipeline
        
        # Act
        self.processor._process_single_file(filepath)
        
        # Assert
        self.pipeline_class.assert_called_once_with(
            self.processors, self.input_dir, self.output_dir, self.deleted_dir
        )
        mock_pipeline.process_and_save.assert_called_once_with(filepath)

    @patch("builtins.print")
    @patch("traceback.format_exc")
    def test_process_single_file_exception(self, mock_format_exc, mock_print):
        # Arrange
        filepath = "test/image.jpg"
        error_msg = "Test error"
        mock_pipeline = MagicMock()
        self.pipeline_class.return_value = mock_pipeline
        mock_pipeline.process_and_save.side_effect = Exception(error_msg)
        mock_format_exc.return_value = "Traceback details"
        
        # Act
        self.processor._process_single_file(filepath)
        
        # Assert
        # Check that the exception was caught and printed
        mock_print.assert_any_call(mock.ANY)  # Exception object
        mock_print.assert_any_call("Traceback details")
