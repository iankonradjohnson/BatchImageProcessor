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

    def test_crop_left_area(self):
        # Test cropping the left area of the image
        cropper = DualPageCropper(left=0, top=0, width=100, height=200)
        cropped_img = cropper.process(self.img)
        self.assertEqual(cropped_img.getpixel((40, 100)), (0, 0, 255))  # Blue pixel

    def test_crop_right_area(self):
        # Test cropping the right area of the image
        cropper = DualPageCropper(left=100, top=0, width=100, height=200)
        cropped_img = cropper.process(self.img)
        self.assertEqual(cropped_img.getpixel((40, 100)), (255, 0, 0))  # Red pixel

    def test_backward_compatibility(self):
        # Test backward compatibility with old parameter names
        cropper = DualPageCropper(
            left_left=0,  # Should be used as 'left'
            left_top=0,  # Should be used as 'top'
            width=100,
            height=200,
        )
        cropped_img = cropper.process(self.img)
        self.assertEqual(cropped_img.getpixel((40, 100)), (0, 0, 255))  # Blue pixel


if __name__ == "__main__":
    unittest.main()
