import unittest
from unittest.mock import MagicMock, patch
from python.src.processors.image.image_processor import ImageProcessor
from PIL import Image, UnidentifiedImageError

from python.src.processors.pipeline.image_pipeline import ImagePipeline


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
    def test_process_and_save_image(self, mock_mkdir, mock_exists, mock_open):
        mock_open.return_value.__enter__.return_value = self.test_image
        pipeline = ImagePipeline([self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir)

        pipeline.process_and_save_image(self.mock_img_filename, True)

        mock_open.assert_called_once_with(f"{self.input_dir}/{self.mock_img_filename}")
        self.mock_processor.process.assert_called_once_with(self.test_image, True)
        self.test_image.save.assert_called_with(
            f"{self.save_dir}/{self.mock_img_filename}"
        )
        mock_mkdir.assert_called_once_with(self.save_dir)

    @patch("PIL.Image.open")
    def test_unidentified_image_error(self, mock_open):
        mock_open.side_effect = UnidentifiedImageError
        pipeline = ImagePipeline([self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir)

        pipeline.process_and_save_image(self.mock_img_filename, True)

        self.mock_processor.process.assert_not_called()

    @patch("PIL.Image.open")
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    def test_process_and_save_none_image_does_not_save(
        self, mock_mkdir, mock_exists, mock_open
    ):
        mock_open.return_value.__enter__.return_value = self.test_image
        self.mock_processor.process.return_value = None
        pipeline = ImagePipeline([self.mock_processor], self.input_dir, self.save_dir, self.deleted_dir)

        pipeline.process_and_save_image(self.mock_img_filename, True)

        self.test_image.save.assert_not_called()
