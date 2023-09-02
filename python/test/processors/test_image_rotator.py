from unittest import TestCase

from PIL import Image

from python.src.processors.image_rotator import ImageRotator


class TestImageRotator(TestCase):

    def setUp(self):
        self.image_rotator = ImageRotator(90)

    def test_process(self):
        img = Image.new('RGB', (100, 200), color='white')
        expected_img = Image.new('RGB', (200, 100), color='white')

        result = self.image_rotator.process(img)

        self.assertEqual(result, expected_img)
