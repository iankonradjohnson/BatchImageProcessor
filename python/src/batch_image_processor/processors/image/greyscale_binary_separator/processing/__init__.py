"""
Processing strategies for binary and grayscale regions.
"""

from .processing_strategy import ProcessingStrategy, BaseProcessingStrategy
from .binary_processing import BinaryProcessingStrategy
from .grayscale_processing import GrayscaleProcessingStrategy
from .processing_provider import ProcessingStrategyProvider

__all__ = [
    'ProcessingStrategy',
    'BaseProcessingStrategy',
    'BinaryProcessingStrategy',
    'GrayscaleProcessingStrategy',
    'ProcessingStrategyProvider'
]