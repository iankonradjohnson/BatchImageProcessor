"""
Tests for the VideoPipeline.

This module contains unit tests for the VideoPipeline class.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline
from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_clip import VideoClip


class TestVideoPipeline(unittest.TestCase):
    """Test cases for the VideoPipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.temp_dir, "input")
        self.output_dir = os.path.join(self.temp_dir, "output")
        self.deleted_dir = os.path.join(self.temp_dir, "deleted")
        
        # Create directories
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.deleted_dir, exist_ok=True)
        
        # Touch a test video file
        self.test_filepath = "test_video.mp4"
        self.test_video_path = os.path.join(self.input_dir, self.test_filepath)
        with open(self.test_video_path, 'w') as f:
            f.write('dummy content')
        
        # Create mock processors
        self.mock_processor1 = MagicMock(spec=VideoProcessor)
        self.mock_processor2 = MagicMock(spec=VideoProcessor)
        
        # Create a pipeline with mock processors
        self.processors = [self.mock_processor1, self.mock_processor2]
        self.pipeline = VideoPipeline(
            processors=self.processors,
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            deleted_dir=self.deleted_dir
        )
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    @patch('batch_image_processor.processors.video.video_clip.FFmpegVideoClip.load')
    def test_process_and_save(self, mock_video_clip_load):
        """Test processing and saving a video."""
        # Create a mock VideoClip
        mock_clip = MagicMock(spec=VideoClip)
        mock_video_clip_load.return_value = mock_clip
        
        # Setup processor behavior - both processors return the clip unchanged
        self.mock_processor1.process.return_value = mock_clip
        self.mock_processor2.process.return_value = mock_clip
        
        # Process the video
        self.pipeline.process_and_save(self.test_filepath)
        
        # Check if FFmpegVideoClip.load was called with correct path
        mock_video_clip_load.assert_called_once_with(self.test_video_path)
        
        # Check if each processor was called
        self.mock_processor1.process.assert_called_once_with(mock_clip)
        self.mock_processor2.process.assert_called_once_with(mock_clip)
        
        # Check if the output video was saved
        mock_clip.save.assert_called_once()
        mock_clip.close.assert_called_once()
        
    @patch('batch_image_processor.processors.video.video_clip.FFmpegVideoClip.load')
    def test_filtered_video(self, mock_video_clip_load):
        """Test processing a video that gets filtered out."""
        # Create a mock VideoClip
        mock_clip = MagicMock(spec=VideoClip)
        mock_video_clip_load.return_value = mock_clip
        
        # Setup processor behavior - first processor returns None (filtering)
        self.mock_processor1.process.return_value = None
        
        # Process the video
        self.pipeline.process_and_save(self.test_filepath)
        
        # Check if first processor was called
        self.mock_processor1.process.assert_called_once_with(mock_clip)
        
        # Check second processor was not called (due to filtering)
        self.mock_processor2.process.assert_not_called()
        
        # Check if the clip was closed
        mock_clip.close.assert_called_once()
    
    @patch('batch_image_processor.processors.video.video_clip.FFmpegVideoClip.load')    
    def test_is_video(self, mock_video_clip_load):
        """Test checking if a file is a valid video."""
        # Create a mock VideoClip with valid duration
        mock_clip = MagicMock(spec=VideoClip)
        mock_clip.duration = 10  # Valid duration
        mock_video_clip_load.return_value = mock_clip
        
        # Check if it's a valid video
        result = self.pipeline.is_video(self.test_video_path)
        
        self.assertTrue(result)
        mock_clip.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()