import unittest
from unittest.mock import patch, MagicMock

from batch_image_processor.factory.batch_processor_factory import BatchProcessorFactory
from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline


class TestBatchProcessorFactory(unittest.TestCase):
    
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