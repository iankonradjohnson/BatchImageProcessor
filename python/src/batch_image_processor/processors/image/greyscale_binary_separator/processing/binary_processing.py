"""
Binary region processing strategy.
"""

from typing import Dict, Any

import numpy as np
from skimage.filters import threshold_otsu

from .processing_strategy import BaseProcessingStrategy


class BinaryProcessingStrategy(BaseProcessingStrategy):
    """
    Strategy for processing binary regions with threshold and no dithering.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the binary processing strategy.

        Args:
            config: Configuration dictionary with parameters:
                - threshold: Threshold value (default: auto)
                - invert: Whether to invert the result (default: False)
        """
        super().__init__(config)
        self.threshold_value = self.config.get("threshold", None)
        self.invert = self.config.get("invert", False)

    def process(self, image: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
        """
        Process binary regions of an image.

        Args:
            image: The input image to process.
            region_mask: Mask indicating the binary regions to process.

        Returns:
            The processed binary regions.
        """
        # Ensure image is grayscale
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray_img = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray_img = image.copy()

        # Create output image (initially zeros)
        result = np.zeros_like(gray_img)

        # Skip processing if no regions to process
        if not np.any(region_mask):
            return result

        # Extract region to process
        region = gray_img[region_mask]

        # Determine threshold value
        if self.threshold_value is None:
            try:
                # Auto threshold using Otsu's method
                threshold = threshold_otsu(region)
            except ValueError:
                # Fallback if Otsu's method fails
                threshold = 128
        else:
            threshold = self.threshold_value

        # Apply threshold
        binary = region > threshold

        # Invert if needed
        if self.invert:
            binary = ~binary

        # Convert to output format
        binary_result = binary.astype(np.uint8) * 255

        # Place processed region back into result
        result[region_mask] = binary_result

        return result
