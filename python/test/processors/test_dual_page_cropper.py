import unittest
from unittest import TestCase
from PIL import Image, ImageDraw
from batch_image_processor.processors.image import DualPageCropper


class TestDualPageCropper(TestCase):
    def setUp(self):
        # Create a 200x200 white image
        self.img = Image.new("RGB", (200, 200), color="white")

        # Add distinct color rectangles to differentiate left and right
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([10, 10, 90, 190], fill="blue")  # Left rect
        draw.rectangle([110, 10, 190, 190], fill="red")  # Right rect

    def test_left_crop(self):
        config = {
            "left": {"x_start": 0, "y_start": 0},
            "right": {"x_start": 100, "y_start": 0},
            "image_size": {"width": 100, "height": 200},
        }

        cropper = DualPageCropper(config)
        cropped_left = cropper.process(self.img, True)
        self.assertEqual(
            cropped_left.getpixel((40, 100)), (0, 0, 255)
        )  # Check for blue pixel in the middle

    def test_right_crop(self):
        config = {
            "left": {"x_start": 0, "y_start": 0},
            "right": {"x_start": 100, "y_start": 0},
            "image_size": {"width": 100, "height": 200},
        }

        cropper = DualPageCropper(config)
        cropped_right = cropper.process(self.img, False)
        self.assertEqual(
            cropped_right.getpixel((40, 100)), (255, 0, 0)
        )  # Check for red pixel in the middle

    def test_toggle_back_to_left(self):
        config = {
            "left": {"x_start": 0, "y_start": 0},
            "right": {"x_start": 100, "y_start": 0},
            "image_size": {"width": 100, "height": 200},
        }

        cropper = DualPageCropper(config)
        cropper.process(self.img, False)  # Crop right first
        cropped_left_again = cropper.process(self.img, True)
        self.assertEqual(
            cropped_left_again.getpixel((40, 100)), (0, 0, 255)
        )  # Check for blue pixel again


if __name__ == "__main__":
    unittest.main()
