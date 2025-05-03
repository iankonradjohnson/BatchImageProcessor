"""
Tests for the VideoProcessorFactory.

This module contains unit tests for the VideoProcessorFactory class.
"""

import unittest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from moviepy.editor import VideoFileClip

from batch_image_processor.factory.video_processor_factory import VideoProcessorFactory
from batch_image_processor.processors.video.video_processor import VideoProcessor


# Create a mock video processor for testing
class MockVideoProcessor(VideoProcessor):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def process(self, clip: VideoFileClip) -> VideoFileClip:
        return clip


class TestVideoProcessorFactory(unittest.TestCase):
    """Test cases for the VideoProcessorFactory."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear the registry before each test
        VideoProcessorFactory._processor_registry = {}
        
    def test_register_processor(self):
        """Test registering a processor."""
        # Register a mock processor
        VideoProcessorFactory.register_processor("MockProcessor", MockVideoProcessor)
        
        # Check if it was registered correctly
        self.assertIn("MockProcessor", VideoProcessorFactory._processor_registry)
        self.assertEqual(MockVideoProcessor, VideoProcessorFactory._processor_registry["MockProcessor"])
        
    def test_create_processor(self):
        """Test creating a processor."""
        # Register a mock processor
        VideoProcessorFactory.register_processor("MockProcessor", MockVideoProcessor)
        
        # Create a processor instance
        config = {"type": "MockProcessor", "param1": "value1"}
        processor = VideoProcessorFactory.create_processor(config)
        
        # Check if the correct type was created
        self.assertIsInstance(processor, MockVideoProcessor)
        self.assertEqual(processor.config, config)
        
    def test_create_invalid_processor(self):
        """Test creating a processor with an invalid type."""
        config = {"type": "InvalidProcessor"}
        
        # Should raise ValueError for invalid processor type
        with self.assertRaises(ValueError):
            VideoProcessorFactory.create_processor(config)
            
    def test_factory_implements_protocol(self):
        """Test that VideoProcessorFactory implements MediaProcessorFactory protocol."""
        from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
        
        # Check if VideoProcessorFactory is an instance of MediaProcessorFactory
        self.assertTrue(issubclass(VideoProcessorFactory, MediaProcessorFactory))


if __name__ == "__main__":
    unittest.main()