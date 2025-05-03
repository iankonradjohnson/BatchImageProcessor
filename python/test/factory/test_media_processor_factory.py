import unittest
from typing import Dict, Any, Type
from unittest.mock import MagicMock

from PIL import Image

from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
from batch_image_processor.processors.media_processor import MediaProcessor


class ConcreteMediaProcessorFactory:
    """Concrete implementation of MediaProcessorFactory for testing."""
    
    _processor_registry: Dict[str, Type] = {}
    
    @classmethod
    def create_processor(cls, config: Dict[str, Any]) -> MediaProcessor:
        processor_type = config.get("type")
        if not processor_type:
            raise ValueError("Processor type not specified")
        
        processor_class = cls._processor_registry.get(processor_type)
        if not processor_class:
            raise ValueError(f"Invalid processor type: {processor_type}")
        
        return processor_class(**{k: v for k, v in config.items() if k != "type"})
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type) -> None:
        cls._processor_registry[processor_type] = processor_class


class TestMediaProcessorFactory(unittest.TestCase):
    def test_protocol_compliance(self):
        # Test that our concrete implementation satisfies the protocol
        self.assertTrue(isinstance(ConcreteMediaProcessorFactory, MediaProcessorFactory))
    
    def test_register_and_create_processor(self):
        # Create a mock processor class
        mock_processor_class = MagicMock()
        mock_processor = MagicMock(spec=MediaProcessor)
        mock_processor_class.return_value = mock_processor
        
        # Register the processor
        ConcreteMediaProcessorFactory.register_processor("MockProcessor", mock_processor_class)
        
        # Create a processor using the factory
        config = {"type": "MockProcessor", "param1": "value1", "param2": "value2"}
        processor = ConcreteMediaProcessorFactory.create_processor(config)
        
        # Check that the processor was created correctly
        self.assertEqual(processor, mock_processor)
        mock_processor_class.assert_called_once_with(param1="value1", param2="value2")
    
    def test_create_processor_missing_type(self):
        # Test creating a processor with missing type
        with self.assertRaises(ValueError) as context:
            ConcreteMediaProcessorFactory.create_processor({})
        
        self.assertIn("Processor type not specified", str(context.exception))
    
    def test_create_processor_invalid_type(self):
        # Test creating a processor with an invalid type
        with self.assertRaises(ValueError) as context:
            ConcreteMediaProcessorFactory.create_processor({"type": "InvalidType"})
        
        self.assertIn("Invalid processor type", str(context.exception))


if __name__ == "__main__":
    unittest.main()