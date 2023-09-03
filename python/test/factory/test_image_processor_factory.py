import unittest

from python.src.factory.image_processor_factory import ImageProcessorFactory
from python.src.processors.dual_page_cropper import DualPageCropper
from python.src.processors.image_rotator import ImageRotator


class TestImageProcessorFactory(unittest.TestCase):
    def test_create_image_rotator(self):
        config = {"type": "ImageRotator", "left": "left", "right": "right"}

        processor = ImageProcessorFactory.create_processor(config)

        self.assertIsInstance(processor, ImageRotator)
        self.assertEqual(processor.left, config.get("left"))
        self.assertEqual(processor.right, config.get("right"))

    def test_create_image_rotator_default_angle(self):
        config = {"type": "ImageRotator"}

        processor = ImageProcessorFactory.create_processor(config)

        self.assertIsInstance(processor, ImageRotator)
        self.assertEqual(processor.left, None)
        self.assertEqual(processor.right, None)

    def test_create_dual_page_cropper(self):
        config = {"type": "AutoPageCropper", "left": "left", "right": "right"}

        processor = ImageProcessorFactory.create_processor(config)

        self.assertIsInstance(processor, DualPageCropper)
        self.assertEqual(processor.left, config.get("left"))
        self.assertEqual(processor.right, config.get("right"))

    def test_unknown_processor_type(self):
        config = {"type": "UnknownType"}

        with self.assertRaises(ValueError):
            processor = ImageProcessorFactory.create_processor(config)

    def test_missing_processor_type(self):
        config = {}

        with self.assertRaises(ValueError):
            processor = ImageProcessorFactory.create_processor(config)


if __name__ == "__main__":
    unittest.main()
