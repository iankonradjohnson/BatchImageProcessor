"""
Provider for detection strategies.
"""

from typing import Dict, Any, List, Type, Optional

import numpy as np

from .detection_strategy import DetectionStrategy
from .histogram_analysis import HistogramAnalysisStrategy
from .texture_analysis import TextureAnalysisStrategy
from .edge_detection import EdgeDetectionStrategy


class DetectionStrategyProvider:
    """
    Factory and provider for detection strategies.
    
    This class manages the creation and configuration of detection strategies,
    and provides access to them.
    """
    
    def __init__(self):
        """Initialize the provider with default strategies."""
        self._strategies = {}
        self._strategy_classes = {
            'histogram': HistogramAnalysisStrategy,
            'texture': TextureAnalysisStrategy,
            'edge': EdgeDetectionStrategy
        }
        
        # Register default strategies
        self.register_strategy('histogram', HistogramAnalysisStrategy)
        self.register_strategy('texture', TextureAnalysisStrategy)
        self.register_strategy('edge', EdgeDetectionStrategy)
        
    def register_strategy(self, strategy_name: str, strategy_class: Type[DetectionStrategy]) -> None:
        """
        Register a new detection strategy.
        
        Args:
            strategy_name: Name for the strategy.
            strategy_class: Class for the strategy.
        """
        self._strategy_classes[strategy_name] = strategy_class
        
    def get_strategy(self, strategy_name: str, config: Dict[str, Any] = None) -> DetectionStrategy:
        """
        Get a detection strategy by name.
        
        Args:
            strategy_name: Name of the strategy to get.
            config: Optional configuration for the strategy.
            
        Returns:
            The requested detection strategy.
            
        Raises:
            ValueError: If the strategy name is not registered.
        """
        if strategy_name not in self._strategy_classes:
            raise ValueError(f"Unknown detection strategy: {strategy_name}")
            
        # Create strategy if it doesn't exist or if configuration is provided
        if strategy_name not in self._strategies or config is not None:
            self._strategies[strategy_name] = self._strategy_classes[strategy_name](config)
            
        return self._strategies[strategy_name]
    
    def get_all_strategies(self, config: Dict[str, Any] = None) -> List[DetectionStrategy]:
        """
        Get all registered detection strategies.
        
        Args:
            config: Optional global configuration to apply to all strategies.
            
        Returns:
            List of detection strategies.
        """
        strategies = []
        for name in self._strategy_classes:
            # Create strategy with strategy-specific config if available
            strategy_config = None
            if config is not None and name in config:
                strategy_config = config[name]
            strategies.append(self.get_strategy(name, strategy_config))
        return strategies
    
    def combine_results(self, results: List[np.ndarray], weights: List[float] = None) -> np.ndarray:
        """
        Combine results from multiple detection strategies.
        
        Args:
            results: List of probability maps from different strategies.
            weights: Optional weights for each strategy (defaults to equal weights).
            
        Returns:
            Combined probability map.
        """
        if not results:
            return np.array([])
            
        # Use equal weights if none provided
        if weights is None:
            weights = [1.0 / len(results)] * len(results)
            
        # Normalize weights
        weights = np.array(weights) / np.sum(weights)
        
        # Stack and combine with weights
        stacked_results = np.stack(results, axis=0)
        combined_result = np.sum(stacked_results * weights[:, np.newaxis, np.newaxis], axis=0)
        
        return combined_result