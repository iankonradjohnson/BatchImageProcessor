import unittest
from unittest import TestCase

from PIL import Image, ImageDraw
from python.src.processors.dual_page_cropper import DualPageCropper


class TestDualPageCropper(TestCase):
    def setUp(self):
        # Create a 200x200 white image
        self.img = Image.new("RGB", (200, 200), color="white")

        # Add distinct color rectangles to differentiate left and right
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([10, 10, 90, 190], fill="blue")  # Left rect
        draw.rectangle([110, 10, 190, 190], fill="red")  # Right rect

    def test_process(self):
        config = {
            "left": {"x0": 0, "y0": 0, "x1": 100, "y1": 200},
            "right": {"x0": 100, "y0": 0, "x1": 200, "y1": 200},
        }

        cropper = DualPageCropper(config)

        # Test left crop
        cropped_left = cropper.process(self.img)
        self.assertEqual(
            cropped_left.getpixel((40, 100)), (0, 0, 255)
        )  # Check for blue pixel in the middle

        # Test right crop
        cropped_right = cropper.process(self.img)
        self.assertEqual(
            cropped_right.getpixel((60, 100)), (255, 0, 0)
        )  # Check for red pixel in the middle

        # Test toggling back to left
        cropped_left_again = cropper.process(self.img)
        self.assertEqual(
            cropped_left_again.getpixel((40, 100)), (0, 0, 255)
        )  # Check for blue pixel again


if __name__ == "__main__":
    unittest.main()
