import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import io

from batch_image_processor.main import main, worker


class TestMain(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            "directories": [
                {
                    "type": "SinglePage",
                    "input_dir": "/path/to/input1",
                    "output_dir": "/path/to/output1",
                    "processors": [
                        {"type": "ImageRotator", "angle": 90}
                    ]
                },
                {
                    "type": "SinglePage",
                    "input_dir": "/path/to/input2",
                    "output_dir": "/path/to/output2",
                    "processors": [
                        {"type": "Threshold", "value": 128}
                    ]
                }
            ]
        }
        self.config_yaml = """
        directories:
          - type: SinglePage
            input_dir: /path/to/input1
            output_dir: /path/to/output1
            processors:
              - type: ImageRotator
                angle: 90
          - type: SinglePage
            input_dir: /path/to/input2
            output_dir: /path/to/output2
            processors:
              - type: Threshold
                value: 128
        """

    @patch('batch_image_processor.main.BatchProcessorFactory')
    @patch('batch_image_processor.main.ImageProcessorFactory')
    def test_worker_success(self, mock_image_factory, mock_batch_factory):
        # Arrange
        mock_image_processor = MagicMock()
        mock_image_factory.create_processor.return_value = mock_image_processor
        
        mock_batch_processor = MagicMock()
        mock_batch_factory.create_batch_processor.return_value = mock_batch_processor
        
        dir_config = {
            "type": "SinglePage",
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "deleted_dir": "/path/to/deleted",
            "copies": 2,
            "processors": [
                {"type": "ImageRotator", "angle": 90}
            ]
        }
        
        # Act
        worker(dir_config)
        
        # Assert
        mock_image_factory.create_processor.assert_called_once_with({"type": "ImageRotator", "angle": 90})
        mock_batch_factory.create_batch_processor.assert_called_once_with(
            "SinglePage", 
            "/path/to/input", 
            "/path/to/output", 
            [mock_image_processor],
            "/path/to/deleted",
            2
        )
        mock_batch_processor.batch_process.assert_called_once()
    
    @patch('batch_image_processor.main.BatchProcessorFactory')
    @patch('batch_image_processor.main.ImageProcessorFactory')
    def test_worker_exception(self, mock_image_factory, mock_batch_factory):
        # Arrange - make the factory raise an exception
        mock_image_factory.create_processor.side_effect = ValueError("Invalid processor")
        
        dir_config = {
            "type": "SinglePage",
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "processors": [
                {"type": "InvalidProcessor"}
            ]
        }
        
        # Act - worker should catch the exception
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            worker(dir_config)
            
            # Assert - exception should be caught, not propagated
            output = fake_stdout.getvalue()
            self.assertIn("Invalid processor", output)
    
    @patch('batch_image_processor.main.worker')
    @patch('batch_image_processor.main.ProcessPoolExecutor')
    @patch('batch_image_processor.main.as_completed')
    @patch('batch_image_processor.main.tqdm')
    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_main_success(self, mock_file, mock_yaml_load, mock_tqdm, mock_as_completed, 
                          mock_executor_class, mock_worker):
        # Arrange
        mock_yaml_load.return_value = self.config_data
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock futures and as_completed
        future1 = MagicMock()
        future2 = MagicMock()
        mock_executor.submit.side_effect = [future1, future2]
        mock_as_completed.return_value = [future1, future2]
        
        # Mock tqdm
        mock_progress = MagicMock()
        mock_tqdm.return_value = mock_progress
        mock_progress.__enter__.return_value = mock_progress
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['main.py', 'config.yml']):
            # Act
            main()
            
            # Assert
            mock_file.assert_called_once_with('config.yml', 'r', encoding='utf-8')
            mock_yaml_load.assert_called_once()
            
            # Check that worker was called for each directory
            self.assertEqual(mock_executor.submit.call_count, 2)
            mock_executor.submit.assert_any_call(mock_worker, self.config_data['directories'][0])
            mock_executor.submit.assert_any_call(mock_worker, self.config_data['directories'][1])
            
            # Check that tqdm was initialized with correct total
            mock_tqdm.assert_called_once_with(total=2)
            
            # Check that as_completed was called with the futures
            futures_dict = {future1: self.config_data['directories'][0], future2: self.config_data['directories'][1]}
            mock_as_completed.assert_called_once()

    @patch('builtins.print')
    def test_main_invalid_args(self, mock_print):
        # Test main with invalid args (no config file)
        with patch.object(sys, 'argv', ['main.py']):
            main()
            mock_print.assert_called_once_with("Usage: python main.py <config_file>")


if __name__ == '__main__':
    unittest.main()