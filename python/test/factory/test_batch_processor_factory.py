import unittest
from unittest.mock import patch, MagicMock

from batch_image_processor.factory.batch_processor_factory import BatchProcessorFactory
from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline


class TestBatchProcessorFactory(unittest.TestCase):
    def test_create_processor_from_config_single_page(self):
        # Arrange
        config = {
            "type": "SinglePage",
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "deleted_dir": "/path/to/deleted",
            "copies": 2,
            "processors": [
                {"type": "ImageRotator", "angle": 90}
            ]
        }
        
        # Mock the ImageProcessorFactory.create_processor method
        with patch("batch_image_processor.factory.batch_processor_factory.ImageProcessorFactory") as mock_factory:
            mock_processor = MagicMock()
            mock_factory.create_processor.return_value = mock_processor
            
            # Act
            processor = BatchProcessorFactory.create_processor_from_config(config)
            
            # Assert
            self.assertIsInstance(processor, BatchProcessor)
            self.assertEqual(processor.input_dir, "/path/to/input")
            self.assertEqual(processor.output_dir, "/path/to/output")
            self.assertEqual(processor.deleted_dir, "/path/to/deleted")
            
            # Check that ImageProcessorFactory.create_processor was called with correct config
            mock_factory.create_processor.assert_called_once_with({"type": "ImageRotator", "angle": 90})
    
    def test_create_processor_from_config_dual_page(self):
        # Test the backward compatibility for DualPage type
        config = {
            "type": "DualPage",
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "processors": [
                {"type": "ImageRotator", "angle": 90}
            ]
        }
        
        with patch("batch_image_processor.factory.batch_processor_factory.ImageProcessorFactory") as mock_factory:
            mock_processor = MagicMock()
            mock_factory.create_processor.return_value = mock_processor
            
            processor = BatchProcessorFactory.create_processor_from_config(config)
            
            self.assertIsInstance(processor, BatchProcessor)
            self.assertEqual(processor.deleted_dir, None)  # Default value
            self.assertEqual(processor.input_dir, "/path/to/input")
    
    def test_create_processor_from_config_image_batch(self):
        config = {
            "type": "ImageBatch",
            "input_dir": "/path/to/input",
            "output_dir": "/path/to/output",
            "processors": [
                {"type": "ImageRotator", "angle": 90}
            ]
        }
        
        with patch("batch_image_processor.factory.batch_processor_factory.ImageProcessorFactory") as mock_factory:
            mock_processor = MagicMock()
            mock_factory.create_processor.return_value = mock_processor
            
            processor = BatchProcessorFactory.create_processor_from_config(config)
            
            self.assertIsInstance(processor, BatchProcessor)
            self.assertEqual(processor.deleted_dir, None)  # Default value
            self.assertEqual(processor.input_dir, "/path/to/input")
    
    def test_create_batch_processor_valid_type(self):
        input_dir = "/path/to/input"
        output_dir = "/path/to/output"
        deleted_dir = "/path/to/deleted"
        processors = [MagicMock()]
        
        # Test with SinglePage type
        processor = BatchProcessorFactory.create_batch_processor(
            "SinglePage", input_dir, output_dir, processors, deleted_dir
        )
        
        self.assertIsInstance(processor, BatchProcessor)
        self.assertEqual(processor.input_dir, input_dir)
        self.assertEqual(processor.output_dir, output_dir)
        self.assertEqual(processor.deleted_dir, deleted_dir)
        self.assertEqual(processor.processors, processors)
    
    def test_create_batch_processor_invalid_type(self):
        input_dir = "/path/to/input"
        output_dir = "/path/to/output"
        processors = [MagicMock()]
        
        with self.assertRaises(ValueError) as context:
            BatchProcessorFactory.create_batch_processor(
                "InvalidType", input_dir, output_dir, processors
            )
        
        self.assertIn("Invalid processor type", str(context.exception))


if __name__ == "__main__":
    unittest.main()