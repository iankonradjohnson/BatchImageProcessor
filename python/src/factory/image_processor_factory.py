from python.src.processors.image.brightness_contrast import BrightnessContrast
from python.src.processors.image.color_balance import ColorBalance
from python.src.processors.image.color_inverter import ColorInverter
from python.src.processors.image.dither_greyscale import DitherGreyscale
from python.src.processors.image.dpi_metadata import DpiMetadata
from python.src.processors.image.dual_page_cropper import DualPageCropper
from python.src.processors.image.gaussian_blur import GaussianBlur
from python.src.processors.image.greyscale import Greyscale
from python.src.processors.image.greyscale_binary_separator import GreyscaleBinarySeparator
from python.src.processors.image.image_augmentor import ImageAugmentor
from python.src.processors.image.image_mode_converter import ImageModeConverter
from python.src.processors.image.image_processor import ImageProcessor
from python.src.processors.image.image_rotator import ImageRotator
from python.src.processors.image.levles_adjustment import LevelsAdjustment
from python.src.processors.image.moire_processor import MoireProcessor
from python.src.processors.image.red_blue_channel_swap import RedBlueChannelSwap
from python.src.processors.image.resize_processor import ResizeProcessor
from python.src.processors.image.deskew import Deskew
from python.src.processors.image.threshold_filter import ThresholdFilter
from python.src.processors.image.threshold_processor import ThresholdProcessor
from python.src.processors.image.vibrance_saturation import VibranceSaturation


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

        if processor_type == "GaussianBlur":
            return GaussianBlur(config)

        if processor_type == "ColorInverter":
            return ColorInverter(config)

        if processor_type == "Greyscale":
            return Greyscale(config)

        if processor_type == "RedBlueChannelSwap":
            return RedBlueChannelSwap(config)

        if processor_type == "ImageModeConverter":
            return ImageModeConverter(config)

        if processor_type == "ColorBalance":
            return ColorBalance(config)

        if processor_type == "VibranceSaturation":
            return VibranceSaturation(config)

        if processor_type == "DitherGreyscale":
            return DitherGreyscale(config)

        if processor_type == "BrightnessContrast":
            return BrightnessContrast(config)

        if processor_type == "DpiMetadata":
            return DpiMetadata(config)

        if processor_type == "LevelsAdjustment":
            return LevelsAdjustment(config)
            
        if processor_type == "GreyscaleBinarySeparator":
            return GreyscaleBinarySeparator(config)
            
        if processor_type == "Deskew":
            return Deskew(config)


        raise ValueError("Processor invalid")
