from python.src.processors.image_processor import ImageProcessor
from python.src.processors.image_rotator import ImageRotator
from python.src.processors.dual_page_cropper import DualPageCropper


class ImageProcessorFactory:
    @staticmethod
    def create_processor(config) -> ImageProcessor:
        processor_type = config.get("type")

        if processor_type == "ImageRotator":
            return ImageRotator(config.get("rotation_angle", 0))

        if processor_type == "AutoPageCropper":
            return DualPageCropper(config)

        raise ValueError("Processor invalid")
