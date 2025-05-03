"""
Region processing engine for applying different processing to regions.
"""

from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt

from .region import Region
from .processing import ProcessingStrategyProvider


class RegionProcessingEngine:
    """
    Engine for processing different types of regions in an image.

    This class coordinates the processing of regions, applying appropriate
    strategies based on region type and configuration.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the processing engine.

        Args:
            config: Configuration dictionary with parameters:
                - binary: Configuration for binary processing
                - grayscale: Configuration for grayscale processing
        """
        self.config = config or {}
        self.strategy_provider = ProcessingStrategyProvider()

    def process_regions(self, image: np.ndarray, regions: List[Region]) -> np.ndarray:
        """
        Process all regions in the image.

        Args:
            image: The input image to process.
            regions: List of regions to process.

        Returns:
            The processed image.
        """
        # Ensure image is grayscale
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray_img = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray_img = image.copy()

        # Create output image (initially zeros)
        result = np.zeros_like(gray_img)

        # Process each region
        for region in regions:
            # Get appropriate processing strategy
            strategy_config = self.config.get(region.region_type, {})
            strategy = self.strategy_provider.get_strategy(
                region.region_type, strategy_config
            )

            # Process region
            processed_region = strategy.process(gray_img, region.mask)

            # Add to result
            result[region.mask] = processed_region[region.mask]

        return result

    def visualize_processing(
        self, image: np.ndarray, regions: List[Region], processed_image: np.ndarray
    ) -> np.ndarray:
        """
        Visualize the processing results.

        Args:
            image: The original input image.
            regions: The detected regions.
            processed_image: The processed image.

        Returns:
            Visualization image.
        """
        import matplotlib.pyplot as plt

        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Show original image
        axes[0].imshow(image, cmap="gray")
        axes[0].set_title("Original Image")
        axes[0].axis("off")

        # Show regions
        region_viz = np.zeros((*image.shape[:2], 3), dtype=np.uint8)

        # Add original image as background (darkened)
        if len(image.shape) == 3 and image.shape[2] == 3:
            region_viz = image.copy() // 2
        else:
            # Convert grayscale to RGB
            gray_img = (
                image.copy()
                if len(image.shape) == 2
                else np.mean(image, axis=2).astype(np.uint8)
            )
            region_viz = np.stack([gray_img // 2] * 3, axis=2)

        # Add colored overlays for each region type
        for region in regions:
            if region.region_type == "grayscale":
                # Red for grayscale regions
                region_viz[region.mask] = np.array([255, 100, 100], dtype=np.uint8)
            else:
                # Blue for binary regions
                region_viz[region.mask] = np.array([100, 100, 255], dtype=np.uint8)

        axes[1].imshow(region_viz)
        axes[1].set_title("Detected Regions")
        axes[1].axis("off")

        # Show processed image
        axes[2].imshow(processed_image, cmap="gray")
        axes[2].set_title("Processed Image")
        axes[2].axis("off")

        # Adjust layout and convert to image
        plt.tight_layout()

        # Convert figure to image
        fig.canvas.draw()
        viz_image = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)

        return viz_image
