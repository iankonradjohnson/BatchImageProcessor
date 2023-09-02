from unittest import TestCase, mock

from python.src.processors.book_processor import BookProcessor
from python.src.processors.pipeline.image_pipeline import ImagePipeline


class TestBookProcessor(TestCase):
    @mock.patch("os.listdir")
    @mock.patch.object(ImagePipeline, "process_and_save_image")
    def test_process(self, mock_process_and_save_image, mock_listdir):
        # Given
        book_config = {
            "image_directory": "/path/to/images",
            "save_directory": "/path/to/save",
            "processors": [{"type": "ImageRotator", "rotation_angle": 45}],
        }
        shared_processors = [{"type": "AutoPageCropper"}]
        processor = BookProcessor(book_config, shared_processors)

        mock_listdir.return_value = ["image1.jpg", "image2.jpg"]

        # When
        processor.process_book()

        # Then
        self.assertEqual(
            mock_process_and_save_image.call_count, 2
        )  # Should be called for each image
