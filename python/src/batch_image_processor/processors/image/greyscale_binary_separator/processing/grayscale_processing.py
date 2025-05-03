"""
Grayscale region processing strategy.
"""

from typing import Dict, Any, Tuple

import numpy as np
from skimage.exposure import adjust_sigmoid
from skimage.filters import threshold_otsu
import scipy.ndimage as ndimage

from .processing_strategy import BaseProcessingStrategy


class GrayscaleProcessingStrategy(BaseProcessingStrategy):
    """
    Strategy for processing grayscale regions with adjustments and dithering.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the grayscale processing strategy.

        Args:
            config: Configuration dictionary with parameters:
                - brightness: Brightness adjustment (-1.0 to 1.0, default: 0.0)
                - contrast: Contrast adjustment (0.0 to 2.0, default: 1.0)
                - dpi: Target DPI for dithering (default: 300)
                - dither_type: Dithering algorithm (default: 'floyd-steinberg')
                - preserve_grayscale: Whether to preserve grayscale values (default: False)
                - threshold: Threshold value (default: auto)
        """
        super().__init__(config)
        self.brightness = self.config.get("brightness", 0.0)
        self.contrast = self.config.get("contrast", 1.0)
        self.dpi = self.config.get("dpi", 300)
        self.dither_type = self.config.get("dither_type", "floyd-steinberg")
        self.preserve_grayscale = self.config.get("preserve_grayscale", False)
        self.threshold_value = self.config.get("threshold", None)

    def process(self, image: np.ndarray, region_mask: np.ndarray) -> np.ndarray:
        """
        Process grayscale regions of an image.

        Args:
            image: The input image to process.
            region_mask: Mask indicating the grayscale regions to process.

        Returns:
            The processed grayscale regions.
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
            print("No grayscale regions to process")
            return result

        print(f"Processing grayscale region with {np.sum(region_mask)} pixels")

        # Make a copy of the mask to avoid modifying the original
        processing_mask = region_mask.copy()

        # Optional: Slightly erode the mask to prevent processing right at the boundary
        # This can help with artifacts at region boundaries
        from skimage.morphology import binary_erosion, disk

        # But only if the region is large enough to handle erosion
        if np.sum(processing_mask) > 1000:
            processing_mask = binary_erosion(processing_mask, disk(1))

        # Extract region to process
        region = gray_img[processing_mask].astype(np.float32) / 255.0

        # Apply brightness and contrast adjustments
        adjusted_region = self._adjust_brightness_contrast(region)

        if self.preserve_grayscale:
            # Preserve grayscale values without thresholding
            print("Preserving grayscale values for region")
            processed_region = adjusted_region

            # Optional: Apply edge enhancement to make details more visible
            # This can help with grayscale images that have low contrast
            from scipy.ndimage import gaussian_filter

            # Only apply edge enhancement if region is large enough
            if len(region) > 100:
                try:
                    # Create sharpened version using unsharp masking
                    blurred = gaussian_filter(adjusted_region, sigma=1.0)
                    edge_enhanced = adjusted_region + 0.5 * (adjusted_region - blurred)

                    # Blend with original (70% enhanced, 30% original)
                    processed_region = (
                        0.7 * np.clip(edge_enhanced, 0, 1) + 0.3 * adjusted_region
                    )
                    processed_region = np.clip(processed_region, 0, 1)
                    print("Applied edge enhancement to grayscale region")
                except Exception as e:
                    print(f"Edge enhancement failed: {e}, using adjusted region")
                    # Fall back to adjusted region if enhancement fails
                    processed_region = adjusted_region
            else:
                print("Region too small for edge enhancement")

        else:
            # Apply thresholding and dithering
            # Determine threshold value
            if self.threshold_value is None:
                try:
                    # Auto threshold using Otsu's method
                    threshold = threshold_otsu(adjusted_region)
                except ValueError:
                    # Fallback if Otsu's method fails
                    threshold = 0.5
            else:
                threshold = self.threshold_value / 255.0  # Convert 0-255 to 0-1 range

            # Apply dithering
            processed_region = self._apply_dithering(adjusted_region, threshold)

        # Convert to output format
        grayscale_result = (processed_region * 255).astype(np.uint8)

        # Place processed region back into result
        result[processing_mask] = grayscale_result

        return result

    def _adjust_brightness_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Adjust brightness and contrast of an image.

        Args:
            image: Input image (0-1 range).

        Returns:
            Adjusted image (0-1 range).
        """
        # Parameters for sigmoid adjustment
        cutoff = 0.5 - self.brightness / 2.0  # Brightness control
        gain = self.contrast * 5.0  # Contrast control

        # Apply sigmoid adjustment
        adjusted = adjust_sigmoid(image, cutoff=cutoff, gain=gain)

        # Ensure values stay in 0-1 range
        return np.clip(adjusted, 0.0, 1.0)

    def _apply_dithering(self, image: np.ndarray, threshold: float) -> np.ndarray:
        """
        Apply dithering to an image.

        Args:
            image: Input image (0-1 range).
            threshold: Threshold value for dithering.

        Returns:
            Dithered binary image.
        """
        if self.dither_type == "none":
            # Simple thresholding without dithering
            return image > threshold

        elif self.dither_type == "floyd-steinberg":
            # Floyd-Steinberg dithering
            return self._floyd_steinberg_dithering(image, threshold)

        elif self.dither_type == "ordered":
            # Ordered dithering
            return self._ordered_dithering(image, threshold)

        else:
            # Default to simple thresholding
            return image > threshold

    def _floyd_steinberg_dithering(
        self, image: np.ndarray, threshold: float
    ) -> np.ndarray:
        """
        Apply Floyd-Steinberg dithering.

        Args:
            image: Input image (0-1 range).
            threshold: Threshold value.

        Returns:
            Dithered binary image.
        """
        # Create a copy of the image to work with
        dithered = image.copy()

        # BUGFIX: Check if image is a 1D array and reshape if needed
        if len(dithered.shape) == 1:
            # 1D array handling
            print(f"WARNING: Received 1D array for dithering, shape: {dithered.shape}")
            # Just use simple thresholding for 1D arrays
            return dithered > threshold

        # Normal 2D image processing
        height, width = dithered.shape

        # Process each pixel
        for y in range(height):
            for x in range(width):
                old_pixel = dithered[y, x]
                new_pixel = 1 if old_pixel > threshold else 0
                error = old_pixel - new_pixel
                dithered[y, x] = new_pixel

                # Distribute error to neighboring pixels
                if x + 1 < width:
                    dithered[y, x + 1] += error * 7 / 16
                if y + 1 < height:
                    if x > 0:
                        dithered[y + 1, x - 1] += error * 3 / 16
                    dithered[y + 1, x] += error * 5 / 16
                    if x + 1 < width:
                        dithered[y + 1, x + 1] += error * 1 / 16

        return dithered > 0.5

    def _ordered_dithering(self, image: np.ndarray, threshold: float) -> np.ndarray:
        """
        Apply ordered dithering.

        Args:
            image: Input image (0-1 range).
            threshold: Base threshold value.

        Returns:
            Dithered binary image.
        """
        # BUGFIX: Check if image is a 1D array
        if len(image.shape) == 1:
            # 1D array handling
            print(
                f"WARNING: Received 1D array for ordered dithering, shape: {image.shape}"
            )
            # Just use simple thresholding for 1D arrays
            return image > threshold

        # Bayer matrix for ordered dithering
        bayer_matrix = (
            np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
            / 16.0
        )

        # Tile the Bayer matrix to match image size
        height, width = image.shape
        bayer_tiled = np.tile(bayer_matrix, ((height + 3) // 4, (width + 3) // 4))[
            :height, :width
        ]

        # Apply dithering
        return image > (threshold - 0.5 + bayer_tiled)
