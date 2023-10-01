from python.src.processors.image.dual_page_cropper import DualPageCropper
from python.src.processors.image.image_augmentor import ImageAugmentor
from python.src.processors.image.image_processor import ImageProcessor
from python.src.processors.image.image_rotator import ImageRotator
from python.src.processors.image.moire_processor import MoireProcessor
from python.src.processors.image.resize_processor import ResizeProcessor
from python.src.processors.image.threshold_filter import ThresholdFilter
from python.src.processors.image.threshold_processor import ThresholdProcessor


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

        if processor_type == "ImageAugmentor":
            return ImageAugmentor(config)

        if processor_type == "Moire":
            return MoireProcessor(config)

        if processor_type == "Resize":
            return ResizeProcessor(config)

        if processor_type == "Threshold":
            return ThresholdProcessor(config)

        raise ValueError("Processor invalid")
