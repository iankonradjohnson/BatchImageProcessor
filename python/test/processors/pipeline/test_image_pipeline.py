import unittest
from unittest.mock import MagicMock, patch, call
from batch_image_processor.processors.image.image_processor import ImageProcessor
from PIL import Image, UnidentifiedImageError

from batch_image_processor.processors.pipeline.image_pipeline import ImagePipeline


class TestImagePipeline(unittest.TestCase):
    def setUp(self):
        self.mock_processor = MagicMock(spec=ImageProcessor)
        self.test_image = Image.new("RGB", (10, 10), "white")
        self.test_image.save = MagicMock()
        self.mock_processor.process.return_value = self.test_image
        self.mock_img_filename = "mock_img.jpg"
        self.input_dir = "/path/to/input_dir"
        self.save_dir = "/path/to/save_dir"
        self.deleted_dir = "/path/to/deleted_dir"

    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    @patch.object(ImagePipeline, "is_image", return_value=True)
    def test_process_and_save_image(
        self, mock_is_image, mock_mkdir, mock_exists, mock_open
    ):
        mock_open.return_value.__enter__.return_value = self.test_image
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )

        pipeline.process_and_save(self.mock_img_filename)

        mock_open.assert_called_once_with(f"{self.input_dir}/{self.mock_img_filename}")
        self.mock_processor.process.assert_called_once_with(self.test_image)
        self.test_image.save.assert_called_with(
            f"{self.save_dir}/{self.mock_img_filename.split('.')[0]}.png"
        )
        mock_mkdir.assert_called_once_with(self.save_dir)

    @patch("PIL.Image.open")
    def test_unidentified_image_error(self, mock_open):
        mock_open.side_effect = UnidentifiedImageError
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )

        pipeline.process_and_save(self.mock_img_filename)

        self.mock_processor.process.assert_not_called()

    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    @patch.object(ImagePipeline, "is_image", return_value=True)
    def test_process_and_save_none_image_does_not_save(
        self, mock_is_image, mock_mkdir, mock_exists, mock_open
    ):
        mock_open.return_value.__enter__.return_value = self.test_image
        self.mock_processor.process.return_value = None
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, None
        )  # No deleted_dir

        pipeline.process_and_save(self.mock_img_filename)

        # Check that save to output directory was not called
        self.assertEqual(self.test_image.save.call_count, 0)
    
    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    @patch.object(ImagePipeline, "is_image", return_value=True)
    def test_process_and_save_with_deleted_dir(
        self, mock_is_image, mock_mkdir, mock_exists, mock_open
    ):
        mock_open.return_value.__enter__.return_value = self.test_image
        self.mock_processor.process.return_value = None  # Processor filters out the image
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )

        pipeline.process_and_save(self.mock_img_filename)

        # Check that directories were created as needed
        mock_mkdir.assert_called_with(self.deleted_dir)
        
        # Check that the original image was saved to deleted_dir
        self.test_image.save.assert_called_once_with(
            f"{self.deleted_dir}/{self.mock_img_filename}"
        )
    
    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=True)  # Directories already exist
    @patch("os.mkdir")
    @patch.object(ImagePipeline, "is_image", return_value=True)
    def test_process_and_save_existing_directories(
        self, mock_is_image, mock_mkdir, mock_exists, mock_open
    ):
        mock_open.return_value.__enter__.return_value = self.test_image
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )

        pipeline.process_and_save(self.mock_img_filename)

        # Check that mkdir was not called since directories exist
        mock_mkdir.assert_not_called()
        
        # Check that the image was processed and saved
        self.mock_processor.process.assert_called_once_with(self.test_image)
        self.test_image.save.assert_called_once()
    
    @patch("PIL.Image.open")
    @patch.object(ImagePipeline, "is_image", return_value=False)
    def test_skip_non_image_file(self, mock_is_image, mock_open):
        mock_open.return_value.__enter__.return_value = self.test_image
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )

        pipeline.process_and_save(self.mock_img_filename)

        # Check that the processor was not called for a non-image file
        self.mock_processor.process.assert_not_called()
        self.test_image.save.assert_not_called()
    
    @patch("PIL.Image.open")
    def test_is_image_valid(self, mock_open):
        # Set up a valid image
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img
        
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )
        
        result = pipeline.is_image("valid_image.jpg")
        
        self.assertTrue(result)
        mock_img.verify.assert_called_once()
    
    @patch("PIL.Image.open")
    def test_is_image_invalid(self, mock_open):
        # Set up an invalid image that raises an exception on verify
        mock_img = MagicMock()
        mock_img.verify.side_effect = IOError("Invalid image")
        mock_open.return_value.__enter__.return_value = mock_img
        
        pipeline = ImagePipeline(
            [self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir
        )
        
        result = pipeline.is_image("invalid_image.jpg")
        
        self.assertFalse(result)
    
    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    @patch.object(ImagePipeline, "is_image", return_value=True)
    def test_multiple_processors(self, mock_is_image, mock_mkdir, mock_exists, mock_open):
        # Set up multiple processors in a chain
        mock_processor1 = MagicMock(spec=ImageProcessor)
        mock_processor2 = MagicMock(spec=ImageProcessor)
        
        # First processor transforms the image
        intermediate_image = Image.new("RGB", (20, 20), "black")
        intermediate_image.save = MagicMock()
        mock_processor1.process.return_value = intermediate_image
        
        # Second processor transforms it again
        final_image = Image.new("RGB", (30, 30), "blue")
        final_image.save = MagicMock()
        mock_processor2.process.return_value = final_image
        
        # Set up the test
        mock_open.return_value.__enter__.return_value = self.test_image
        pipeline = ImagePipeline(
            [mock_processor1, mock_processor2], self.input_dir, self.save_dir, self.deleted_dir
        )
        
        # Act
        pipeline.process_and_save(self.mock_img_filename)
        
        # Assert
        mock_processor1.process.assert_called_once_with(self.test_image)
        mock_processor2.process.assert_called_once_with(intermediate_image)
        
        # Final image should be saved
        final_image.save.assert_called_once_with(
            f"{self.save_dir}/{self.mock_img_filename.split('.')[0]}.png"
        )
