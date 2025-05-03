"""
Tests for the BorderProcessor class.
"""

import unittest
from unittest import mock
from PIL import Image, ImageDraw

from batch_image_processor.processors.image.border_processor import BorderProcessor


class TestBorderProcessor(unittest.TestCase):
    """Tests for the BorderProcessor class."""

    def test_init(self):
        """Test initialization with default and custom values."""
        # Test with default values
        processor = BorderProcessor()
        self.assertEqual(processor.top, 0)
        self.assertEqual(processor.bottom, 0)
        self.assertEqual(processor.left, 0)
        self.assertEqual(processor.right, 0)

        # Test with custom values
        processor = BorderProcessor(top=10, bottom=20, left=30, right=40)
        self.assertEqual(processor.top, 10)
        self.assertEqual(processor.bottom, 20)
        self.assertEqual(processor.left, 30)
        self.assertEqual(processor.right, 40)

    def test_process_no_border(self):
        """Test processing an image with no border."""
        # Create a mock image with size 100x100
        mock_img = mock.MagicMock(spec=Image.Image)
        mock_img.size = (100, 100)
        mock_img.mode = "L"
        
        # Mock the copy method to return the same mock
        mock_img.copy.return_value = mock_img
        
        # Mock ImageDraw.Draw
        mock_draw = mock.MagicMock()
        
        # Set up mocks
        with mock.patch("PIL.ImageDraw.Draw", return_value=mock_draw):
            processor = BorderProcessor()
            result = processor.process(mock_img)
            
            # Verify no rectangles were drawn since all border widths are 0
            mock_draw.rectangle.assert_not_called()
            
            # Verify the result is our mock image
            self.assertEqual(result, mock_img)

    def test_process_with_border(self):
        """Test processing an image with border."""
        # Create a mock image with size 100x100
        mock_img = mock.MagicMock(spec=Image.Image)
        mock_img.size = (100, 100)
        mock_img.mode = "L"
        
        # Mock the copy method to return the same mock
        mock_img.copy.return_value = mock_img
        
        # Mock ImageDraw.Draw
        mock_draw = mock.MagicMock()
        
        # Set up mocks
        with mock.patch("PIL.ImageDraw.Draw", return_value=mock_draw):
            processor = BorderProcessor(top=10, bottom=20, left=30, right=40)
            result = processor.process(mock_img)
            
            # Verify rectangles were drawn for each border
            self.assertEqual(mock_draw.rectangle.call_count, 4)
            
            # Verify the specific rectangles for each border
            # Check top border
            mock_draw.rectangle.assert_any_call([(0, 0), (99, 9)], fill=255)
            
            # Check bottom border
            mock_draw.rectangle.assert_any_call([(0, 80), (99, 99)], fill=255)
            
            # Check left border
            mock_draw.rectangle.assert_any_call([(0, 0), (29, 99)], fill=255)
            
            # Check right border
            mock_draw.rectangle.assert_any_call([(60, 0), (99, 99)], fill=255)
            
            # Verify the result is our mock image
            self.assertEqual(result, mock_img)

    def test_different_image_modes(self):
        """Test with different image modes."""
        # Test with binary mode "1"
        mock_img = mock.MagicMock(spec=Image.Image)
        mock_img.size = (100, 100)
        mock_img.mode = "1"
        mock_img.copy.return_value = mock_img
        mock_draw = mock.MagicMock()
        
        with mock.patch("PIL.ImageDraw.Draw", return_value=mock_draw):
            processor = BorderProcessor(top=10)
            processor.process(mock_img)
            mock_draw.rectangle.assert_called_with([(0, 0), (99, 9)], fill=1)
        
        # Test with RGB mode
        mock_img.mode = "RGB"
        mock_draw = mock.MagicMock()
        
        with mock.patch("PIL.ImageDraw.Draw", return_value=mock_draw):
            processor = BorderProcessor(top=10)
            processor.process(mock_img)
            mock_draw.rectangle.assert_called_with([(0, 0), (99, 9)], fill="white")


if __name__ == "__main__":
    unittest.main()