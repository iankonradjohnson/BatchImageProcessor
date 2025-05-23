from unittest import TestCase

from PIL import Image, ImageDraw

from batch_image_processor.processors.image.image_rotator import ImageRotator


def create_initial_image():
    img = Image.new("RGB", (100, 200), color="white")
    draw = ImageDraw.Draw(img)
    # Draw a triangle pointing upwards
    draw.polygon([(40, 50), (60, 50), (50, 30)], fill="black")
    return img


class TestImageRotator(TestCase):
    def setUp(self):
        config = {
            "left": {"angle": 90},
            "right": {"angle": -90},
        }
        self.image_rotator = ImageRotator(config)

    def test_process_left(self):
        img = create_initial_image()

        # Set config to use left angle
        self.image_rotator.config = self.image_rotator.left

        # Expected: triangle pointing to the left
        expected_img = img.rotate(90, resample=Image.Resampling.BICUBIC, expand=True)

        result = self.image_rotator.process(img)

        # Compare properties of the resulting image and the expected image
        self.assertTrue(result == expected_img)

    def test_process_right(self):
        img = create_initial_image()

        # Set config to use right angle
        self.image_rotator.config = self.image_rotator.right

        # Expected: triangle pointing to the right
        expected_img = img.rotate(-90, resample=Image.Resampling.BICUBIC, expand=True)

        result = self.image_rotator.process(img)

        # Compare properties of the resulting image and the expected image
        self.assertTrue(result == expected_img)
