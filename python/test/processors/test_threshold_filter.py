import unittest
from unittest.mock import patch, MagicMock
from PIL import Image

from batch_image_processor.processors.image.threshold_filter import ThresholdFilter


class TestThresholdFilter(unittest.TestCase):
    def setUp(self):
        self.min_thresh = 50
        self.max_thresh = 150
        self.save_path = "/path/to/save"
        self.filter = ThresholdFilter(
            min_thresh=self.min_thresh,
            max_thresh=self.max_thresh,
            blank_dir=self.save_path,
        )
        self.test_image = Image.new("RGB", (10, 10), "white")
        self.test_image.save = MagicMock()
        self.mock_img_path = "/path/to/mock_img.jpg"

    @patch(
        "cv2.mean", return_value=(100, 0, 0, 0)
    )  # Mock to return an average within the range
    def test_process_within_threshold(self, mock_mean):
        result = self.filter.process(self.test_image)
        self.assertIsNotNone(result)

    @patch(
        "cv2.mean", return_value=(40, 0, 0, 0)
    )  # Mock to return an average below the range
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    def test_process_below_threshold(self, mock_mkdir, mock_exists, mock_mean):
        result = self.filter.process(self.test_image)
        self.assertIsNone(result)
        self.test_image.save.assert_called_with(self.save_path)

    @patch(
        "cv2.mean", return_value=(160, 0, 0, 0)
    )  # Mock to return an average above the range
    @patch("os.path.exists", return_value=False)
    @patch("os.mkdir")
    def test_process_above_threshold(self, mock_mkdir, mock_exists, mock_mean):
        result = self.filter.process(self.test_image)
        self.assertIsNone(result)
        self.test_image.save.assert_called_with(self.save_path)


if __name__ == "__main__":
    unittest.main()
