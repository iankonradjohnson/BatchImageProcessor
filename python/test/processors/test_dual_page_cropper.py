import unittest
from unittest import TestCase
from PIL import Image, ImageDraw
from batch_image_processor.processors.image.dual_page_cropper import DualPageCropper


class TestDualPageCropper(TestCase):
    def setUp(self):
        # Create a 200x200 white image
        self.img = Image.new("RGB", (200, 200), color="white")

        # Add distinct color rectangles to differentiate left and right
        draw = ImageDraw.Draw(self.img)
        draw.rectangle([10, 10, 90, 190], fill="blue")  # Left rect
        draw.rectangle([110, 10, 190, 190], fill="red")  # Right rect

    def test_left_crop(self):
        cropper = DualPageCropper(
            left_left=0,
            left_top=0,
            right_left=100,
            right_top=0,
            width=100,
            height=200
        )
        cropped_left = cropper.process(self.img, True)
        self.assertEqual(
            cropped_left.getpixel((40, 100)), (0, 0, 255)
        )

    def test_right_crop(self):
        cropper = DualPageCropper(
            left_left=0,
            left_top=0,
            right_left=100,
            right_top=0,
            width=100,
            height=200
        )
        cropped_right = cropper.process(self.img, False)
        self.assertEqual(
            cropped_right.getpixel((40, 100)), (255, 0, 0)
        )

    def test_toggle_back_to_left(self):
        cropper = DualPageCropper(
            left_left=0,
            left_top=0,
            right_left=100,
            right_top=0,
            width=100,
            height=200
        )
        cropper.process(self.img, False)
        cropped_left_again = cropper.process(self.img, True)
        self.assertEqual(
            cropped_left_again.getpixel((40, 100)), (0, 0, 255)
        )


if __name__ == "__main__":
    unittest.main()
