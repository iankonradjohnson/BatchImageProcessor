"""
Processing strategy interfaces and base implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

import numpy as np


class ProcessingStrategy(ABC):
    """
    Interface for all region processing strategies.
    """
    
    @abstractmethod
    def process(self, image: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
        """
        Process regions of an image according to the strategy.
        
        Args:
            image: The input image to process.
            region_mask: Mask indicating the regions to process (1 = process, 0 = ignore).
            
        Returns:
            The processed image regions.
        """
        pass
    
    @abstractmethod
    def configure(self, parameters: Dict[str, Any]) -> None:
        """
        Configure the processing strategy with specific parameters.
        
        Args:
            parameters: Dictionary of configuration parameters.
        """
        pass


class BaseProcessingStrategy(ProcessingStrategy):
    """
    Base implementation for processing strategies with common functionality.
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