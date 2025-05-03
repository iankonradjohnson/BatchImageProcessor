"""
Detection strategies for identifying grayscale and binary regions.
"""

from .detection_strategy import DetectionStrategy, BaseDetectionStrategy
from .histogram_analysis import HistogramAnalysisStrategy
from .texture_analysis import TextureAnalysisStrategy
from .edge_detection import EdgeDetectionStrategy
from .detection_provider import DetectionStrategyProvider

__all__ = [
    "DetectionStrategy",
    "BaseDetectionStrategy",
    "HistogramAnalysisStrategy",
    "TextureAnalysisStrategy",
    "EdgeDetectionStrategy",
    "DetectionStrategyProvider",
]
