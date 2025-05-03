"""
Detection strategy interfaces and base implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

import numpy as np


class DetectionStrategy(ABC):
    """
    Interface for all region detection strategies.
    """

    @abstractmethod
    def analyze(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the image to identify binary and grayscale regions.

        Args:
            image: The input image to analyze (numpy array).

        Returns:
            A probability map where each pixel's value represents the likelihood
            of belonging to a grayscale region (0 = binary, 1 = grayscale).
        """
        pass

    @abstractmethod
    def configure(self, parameters: Dict[str, Any]) -> None:
        """
        Configure the detection strategy with specific parameters.

        Args:
            parameters: Dictionary of configuration parameters.
        """
        pass


class BaseDetectionStrategy(DetectionStrategy):
    """
    Base implementation for detection strategies with common functionality.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the strategy with optional configuration.

        Args:
            config: Configuration dictionary.
        """
        self.config = config or {}

    def configure(self, parameters: Dict[str, Any]) -> None:
        """
        Configure the strategy with specific parameters.

        Args:
            parameters: Dictionary of configuration parameters.
        """
        self.config.update(parameters)
