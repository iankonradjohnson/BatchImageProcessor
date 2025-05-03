"""
A concrete factory implementation for creating image processors.

This module implements the MediaProcessorFactory abstract class for PIL Image
processors. It provides a registry-based approach to creating ImageProcessor
instances based on configuration.
"""

from typing import Dict, Any, Type
from PIL import Image

from batch_image_processor.factory.media_processor_factory import MediaProcessorFactory
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


class ImageProcessorFactory(MediaProcessorFactory[Image.Image]):
    """
    Factory for creating image processors.
    
    This factory implements the MediaProcessorFactory abstract class
    for PIL Image processors. It maintains a registry of processor types
    and their corresponding classes.
    """
    
    # Registry of processor types and their classes
    _processor_registry: Dict[str, Type[ImageProcessor]] = {}
    
    @classmethod
    def create_processor(cls, config: Dict[str, Any]) -> ImageProcessor:
        """
        Create an image processor based on the provided configuration.
        
        Args:
            config: Configuration dictionary with processor parameters
                   including the 'type' key to determine which processor to create.
                   
        Returns:
            An ImageProcessor instance.
            
        Raises:
            ValueError: If the processor type is invalid or not supported.
        """
        processor_type = config.get("type")
        
        # Special case for AutoPageCropper due to complex initialization
        if processor_type == "AutoPageCropper":
            return cls._create_dual_page_cropper(config)
            
        # Use the registry for all other processor types
        if processor_type in cls._processor_registry:
            processor_class = cls._processor_registry[processor_type]
            
            # Special cases that need custom initialization
            if processor_type == "ThresholdFilter":
                return ThresholdFilter(
                    min_thresh=config.get("min_thresh", 0),
                    max_thresh=config.get("max_thresh", 255),
                    blank_dir=config.get("deleted_dir"),
                )
            elif processor_type == "Threshold":
                return ThresholdProcessor(
                    threshold_value=config.get("threshold_value", 128)
                )
            elif processor_type == "Deskew":
                return Deskew(
                    enabled=config.get("enabled", True),
                    threshold=config.get("threshold", "40%"),
                    add_border=config.get("add_border", True),
                    border_size=config.get("border_size", "5x5"),
                    trim_borders=config.get("trim_borders", True),
                    fuzz_value=config.get("fuzz_value", "1%"),
                )
            elif processor_type == "BorderProcessor":
                return BorderProcessor(
                    top=config.get("top", 0),
                    bottom=config.get("bottom", 0),
                    left=config.get("left", 0),
                    right=config.get("right", 0),
                )
            else:
                # General case - pass the entire config to the constructor
                return processor_class(config)
                
        raise ValueError(f"Invalid processor type: {processor_type}")
    
    @classmethod
    def register_processor(cls, processor_type: str, processor_class: Type[ImageProcessor]):
        """
        Register a new processor type with the factory.
        
        Args:
            processor_type: The name/type of the processor to register.
            processor_class: The ImageProcessor class to instantiate for this type.
        """
        cls._processor_registry[processor_type] = processor_class
    
    @classmethod
    def _create_dual_page_cropper(cls, config: Dict[str, Any]) -> DualPageCropper:
        """
        Helper method to create a DualPageCropper with proper parameter handling.
        
        Args:
            config: Configuration dictionary for the DualPageCropper.
            
        Returns:
            Configured DualPageCropper instance.
        """
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


# Register all known processor types
ImageProcessorFactory.register_processor("ImageRotator", ImageRotator)
ImageProcessorFactory.register_processor("ImageAugmentor", ImageAugmentor)
ImageProcessorFactory.register_processor("Resize", ResizeProcessor)
ImageProcessorFactory.register_processor("Threshold", ThresholdProcessor)
ImageProcessorFactory.register_processor("ThresholdFilter", ThresholdFilter)
ImageProcessorFactory.register_processor("GaussianBlur", GaussianBlur)
ImageProcessorFactory.register_processor("ColorInverter", ColorInverter)
ImageProcessorFactory.register_processor("Greyscale", Greyscale)
ImageProcessorFactory.register_processor("RedBlueChannelSwap", RedBlueChannelSwap)
ImageProcessorFactory.register_processor("ImageModeConverter", ImageModeConverter)
ImageProcessorFactory.register_processor("ColorBalance", ColorBalance)
ImageProcessorFactory.register_processor("VibranceSaturation", VibranceSaturation)
ImageProcessorFactory.register_processor("DitherGreyscale", DitherGreyscale)
ImageProcessorFactory.register_processor("BrightnessContrast", BrightnessContrast)
ImageProcessorFactory.register_processor("DpiMetadata", DpiMetadata)
ImageProcessorFactory.register_processor("LevelsAdjustment", LevelsAdjustment)
ImageProcessorFactory.register_processor("GreyscaleBinarySeparator", GreyscaleBinarySeparator)
ImageProcessorFactory.register_processor("Deskew", Deskew)
ImageProcessorFactory.register_processor("BorderProcessor", BorderProcessor)
ImageProcessorFactory.register_processor("AutoPageCropper", DualPageCropper)
