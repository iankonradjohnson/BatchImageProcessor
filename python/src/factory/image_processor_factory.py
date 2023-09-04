from python.src.processors.dual_page_cropper import DualPageCropper
from python.src.processors.image_processor import ImageProcessor
from python.src.processors.image_rotator import ImageRotator
from python.src.processors.threshold_filter import ThresholdFilter


class ImageProcessorFactory:
    @staticmethod
    def create_processor(config) -> ImageProcessor:
        processor_type = config.get("type")

        if processor_type == "ImageRotator":
            return ImageRotator(config)

        if processor_type == "AutoPageCropper":
            return DualPageCropper(config)

        if processor_type == "ThresholdFilter":
            return ThresholdFilter(config)

        raise ValueError("Processor invalid")
