"""
Unit tests for the MoviePyVideoClip class.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from batch_image_processor.processors.video.moviepy_video_clip import MoviePyVideoClipInterface


class TestMoviePyVideoClip(unittest.TestCase):
    """Tests for the MoviePyVideoClip class."""
    
    @patch('batch_image_processor.processors.video.moviepy_video_clip.VideoFileClip')
    def setUp(self, mock_video_file_clip):
        """Set up a MoviePyVideoClip instance for testing."""
        # Configure the mock for VideoFileClip
        self.mock_clip = MagicMock()
        self.mock_clip.w = 1920
        self.mock_clip.h = 1080
        self.mock_clip.fps = 30.0
        self.mock_clip.duration = 10.0
        self.mock_clip.rotation = None
        
        mock_video_file_clip.return_value = self.mock_clip
        
        # Create a MoviePyVideoClip instance
        self.test_file_path = "/path/to/test/video.mp4"
        self.video_clip = MoviePyVideoClipInterface(self.test_file_path)
    
    def test_initialization(self):
        """Test that the MoviePyVideoClip is initialized properly."""
        self.assertEqual(self.video_clip.file_path, self.test_file_path)
        self.assertEqual(self.video_clip._clip, self.mock_clip)
        self.assertIsNone(self.video_clip._rotation)
    
    def test_properties(self):
        """Test that the properties return the expected values."""
        self.assertEqual(self.video_clip.width, 1920)
        self.assertEqual(self.video_clip.height, 1080)
        self.assertEqual(self.video_clip.fps, 30.0)
        self.assertEqual(self.video_clip.duration, 10.0)
        self.assertIsNone(self.video_clip.rotation)
        self.assertTrue(self.video_clip.is_horizontal)
        
        # Test with rotation
        self.video_clip._rotation = 90
        self.assertFalse(self.video_clip.is_horizontal)
    
    def test_rotate(self):
        """Test the rotate method."""
        with patch('batch_image_processor.processors.video.moviepy_video_clip.rotate') as mock_rotate:
            mock_rotate.return_value = self.mock_clip
            
            # Test rotating the clip
            result = self.video_clip.rotate(90)
            
            # Verify rotate was called with the correct parameters
            mock_rotate.assert_called_once_with(self.mock_clip, 90)
            
            # Verify the rotation was stored
            self.assertEqual(self.video_clip._rotation, 90)
            
            # Verify the result is self for method chaining
            self.assertEqual(result, self.video_clip)
    
    def test_crop(self):
        """Test the crop method."""
        with patch('batch_image_processor.processors.video.moviepy_video_clip.crop') as mock_crop:
            mock_crop.return_value = self.mock_clip
            
            # Test cropping the clip
            result = self.video_clip.crop(10, 20, 100, 200)
            
            # Verify crop was called with the correct parameters
            mock_crop.assert_called_once_with(self.mock_clip, x1=10, y1=20, x2=110, y2=220)
            
            # Verify the result is self for method chaining
            self.assertEqual(result, self.video_clip)
    
    def test_resize(self):
        """Test the resize method."""
        with patch('batch_image_processor.processors.video.moviepy_video_clip.resize') as mock_resize:
            mock_resize.return_value = self.mock_clip
            
            # Test resizing the clip
            result = self.video_clip.resize(width=800, height=600)
            
            # Verify resize was called with the correct parameters
            mock_resize.assert_called_once_with(self.mock_clip, width=800, height=600)
            
            # Verify the result is self for method chaining
            self.assertEqual(result, self.video_clip)
    
    @patch('os.makedirs')
    def test_save(self, mock_makedirs):
        """Test the save method."""
        output_path = "/path/to/output/video.mp4"
        
        # Test saving the clip
        self.video_clip.save(output_path)
        
        # Verify makedirs was called
        mock_makedirs.assert_called_once_with(os.path.dirname(output_path), exist_ok=True)
        
        # Verify write_videofile was called
        self.mock_clip.write_videofile.assert_called_once()
        
        # Verify the first argument was the output path
        self.assertEqual(self.mock_clip.write_videofile.call_args[0][0], output_path)
    
    def test_close(self):
        """Test the close method."""
        # Test closing the clip
        self.video_clip.close()
        
        # Verify close was called on the underlying clip
        self.mock_clip.close.assert_called_once()
        
        # Verify the clip was set to None
        self.assertIsNone(self.video_clip._clip)
    
    def test_load_class_method(self):
        """Test the load class method."""
        with patch('batch_image_processor.processors.video.moviepy_video_clip.MoviePyVideoClip.__init__') as mock_init:
            mock_init.return_value = None
            
            # Test the load class method
            clip = MoviePyVideoClipInterface.load(self.test_file_path)
            
            # Verify __init__ was called with the file path
            mock_init.assert_called_once_with(self.test_file_path)
            
            # Verify a MoviePyVideoClip instance was returned
            self.assertIsInstance(clip, MoviePyVideoClipInterface)
    
    @patch('moviepy.editor.concatenate_videoclips')
    @patch('os.makedirs')
    def test_concatenate(self, mock_makedirs, mock_concatenate):
        """Test the concatenate static method."""
        # Create test clips
        clip1 = MagicMock(spec=MoviePyVideoClipInterface)
        clip1._clip = MagicMock()
        clip2 = MagicMock(spec=MoviePyVideoClipInterface)
        clip2._clip = MagicMock()
        
        # Configure mock for concatenate_videoclips
        final_clip = MagicMock()
        mock_concatenate.return_value = final_clip
        
        # Test concatenating clips
        output_path = "/path/to/output/concatenated.mp4"
        MoviePyVideoClipInterface.concatenate([clip1, clip2], output_path)
        
        # Verify concatenate_videoclips was called with the right clips
        mock_concatenate.assert_called_once()
        self.assertEqual(mock_concatenate.call_args[0][0], [clip1._clip, clip2._clip])
        
        # Verify makedirs was called
        mock_makedirs.assert_called_once_with(os.path.dirname(output_path), exist_ok=True)
        
        # Verify write_videofile was called on the final clip
        final_clip.write_videofile.assert_called_once()
        
        # Verify close was called on the final clip
        final_clip.close.assert_called_once()
    
    def test_overlay(self):
        """Test the overlay method."""
        with patch('moviepy.editor.CompositeVideoClip') as mock_composite:
            # Create a test overlay clip
            overlay_clip = MagicMock(spec=MoviePyVideoClipInterface)
            overlay_clip._clip = MagicMock()
            overlay_clip._clip.set_position.return_value = "positioned_clip"
            
            # Configure mock for CompositeVideoClip
            composite_clip = MagicMock()
            mock_composite.return_value = composite_clip
            
            # Test creating an overlay
            result = self.video_clip.overlay(overlay_clip, x=100, y=200, duration=5.0)
            
            # Verify set_position was called on the overlay clip
            overlay_clip._clip.set_position.assert_called_once_with((100, 200))
            
            # Verify set_duration was called on the positioned clip
            overlay_clip._clip.set_position().set_duration.assert_called_once_with(5.0)
            
            # Verify CompositeVideoClip was called with the base clip and positioned overlay
            mock_composite.assert_called_once()
            
            # Verify the result is a MoviePyVideoClip with the correct properties
            self.assertIsInstance(result, MoviePyVideoClipInterface)
            self.assertEqual(result._clip, composite_clip)
            self.assertEqual(result.file_path, self.video_clip.file_path)
            self.assertEqual(result._rotation, self.video_clip._rotation)


if __name__ == '__main__':
    unittest.main()