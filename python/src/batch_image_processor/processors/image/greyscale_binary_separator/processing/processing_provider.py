"""
Provider for processing strategies.
"""

from typing import Dict, Any, Type, Optional

from .processing_strategy import ProcessingStrategy
from .binary_processing import BinaryProcessingStrategy
from .grayscale_processing import GrayscaleProcessingStrategy


class ProcessingStrategyProvider:
    """
    Factory and provider for processing strategies.

    This class manages the creation and configuration of processing strategies,
    and provides access to them.
    """

    def __init__(self):
        """Initialize the provider with default strategies."""
        self._strategies = {}
        self._strategy_classes = {
            "binary": BinaryProcessingStrategy,
            "grayscale": GrayscaleProcessingStrategy,
        }

        # Register default strategies
        self.register_strategy("binary", BinaryProcessingStrategy)
        self.register_strategy("grayscale", GrayscaleProcessingStrategy)

    def register_strategy(
        self, region_type: str, strategy_class: Type[ProcessingStrategy]
    ) -> None:
        """
        Register a new processing strategy.

        Args:
            region_type: Type of region to process.
            strategy_class: Class for the strategy.
        """
        self._strategy_classes[region_type] = strategy_class

    def get_strategy(
        self, region_type: str, config: Dict[str, Any] = None
    ) -> ProcessingStrategy:
        """
        Get a processing strategy for a region type.

        Args:
            region_type: Type of region to process.
            config: Optional configuration for the strategy.

        Returns:
            The requested processing strategy.

        Raises:
            ValueError: If the region type is not registered.
        """
        if region_type not in self._strategy_classes:
            raise ValueError(f"Unknown region type: {region_type}")

        # Create strategy if it doesn't exist or if configuration is provided
        strategy_key = f"{region_type}_{hash(str(config)) if config else 'default'}"
        if strategy_key not in self._strategies or config is not None:
            self._strategies[strategy_key] = self._strategy_classes[region_type](config)

        return self._strategies[strategy_key]
