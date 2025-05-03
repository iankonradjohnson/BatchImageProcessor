from batch_image_processor.processors.image.border_processor import BorderProcessor
from batch_image_processor.processors.image.brightness_contrast import (
    BrightnessContrast,
)
from batch_image_processor.processors.image.color_balance import ColorBalance
from batch_image_processor.processors.image.color_inverter import ColorInverter
from batch_image_processor.processors.image.dither_greyscale import DitherGreyscale
from batch_image_processor.processors.image.dpi_metadata import DpiMetadata
from batch_image_processor.processors.image.dual_page_cropper import DualPageCropper
from batch_image_processor.processors.image.gaussian_blur import GaussianBlur
from batch_image_processor.processors.image.greyscale import Greyscale
from batch_image_processor.processors.image.greyscale_binary_separator import (
    GreyscaleBinarySeparator,
)
from batch_image_processor.processors.image.image_augmentor import ImageAugmentor
from batch_image_processor.processors.image.image_mode_converter import (
    ImageModeConverter,
)
from batch_image_processor.processors.image.image_processor import ImageProcessor
from batch_image_processor.processors.image.image_rotator import ImageRotator
from batch_image_processor.processors.image.levles_adjustment import LevelsAdjustment
from batch_image_processor.processors.image.red_blue_channel_swap import (
    RedBlueChannelSwap,
)
from batch_image_processor.processors.image.resize_processor import ResizeProcessor
from batch_image_processor.processors.image.deskew import Deskew
from batch_image_processor.processors.image.threshold_filter import ThresholdFilter
from batch_image_processor.processors.image.threshold_processor import (
    ThresholdProcessor,
)
from batch_image_processor.processors.image.vibrance_saturation import (
    VibranceSaturation,
)


class ImageProcessorFactory:
    @staticmethod
    def create_processor(config) -> ImageProcessor:
        processor_type = config.get("type")

        if processor_type == "ImageRotator":
            return ImageRotator(config)

        if processor_type == "AutoPageCropper":
            # Handle both dictionary and direct string/number values
            left = config.get("left", {})
            if isinstance(left, dict):
                left_val = left.get("x_start") or left.get("left")
                top_val = left.get("y_start") or left.get("top")
            else:
                left_val = left
                top_val = config.get("top")

            # Handle width and height directly from config
            width_val = config.get("width")
            height_val = config.get("height")

            # If width/height not in direct config, try to get from image_size
            if width_val is None or height_val is None:
                image_size = config.get("image_size", {})
                if isinstance(image_size, dict):
                    if width_val is None:
                        width_val = image_size.get("width")
                    if height_val is None:
                        height_val = image_size.get("height")

            return DualPageCropper(
                left=left_val, top=top_val, width=width_val, height=height_val
            )

        if processor_type == "ThresholdFilter":
            return ThresholdFilter(
                min_thresh=config.get("min_thresh", 0),
                max_thresh=config.get("max_thresh", 255),
                blank_dir=config.get("deleted_dir"),
            )

        if processor_type == "ImageAugmentor":
            return ImageAugmentor(config)

        if processor_type == "Resize":
            return ResizeProcessor(config)

        if processor_type == "Threshold":
            return ThresholdProcessor(
                threshold_value=config.get("threshold_value", 128)
            )

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
            return Deskew(
                enabled=config.get("enabled", True),
                threshold=config.get("threshold", "40%"),
                add_border=config.get("add_border", True),
                border_size=config.get("border_size", "5x5"),
                trim_borders=config.get("trim_borders", True),
                fuzz_value=config.get("fuzz_value", "1%"),
            )

        if processor_type == "BorderProcessor":
            return BorderProcessor(
                top=config.get("top", 0),
                bottom=config.get("bottom", 0),
                left=config.get("left", 0),
                right=config.get("right", 0),
            )

        raise ValueError("Processor invalid")
