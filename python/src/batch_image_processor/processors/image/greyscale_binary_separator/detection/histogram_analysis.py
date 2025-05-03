"""
Histogram-based detection strategy for identifying grayscale regions.
"""

from typing import Dict, Any, Tuple, List

import numpy as np
from skimage.util import view_as_windows
from skimage.exposure import histogram

from .detection_strategy import BaseDetectionStrategy


class HistogramAnalysisStrategy(BaseDetectionStrategy):
    """
    Strategy for detecting grayscale regions based on histogram analysis.

    This strategy analyzes local histograms to identify regions with
    grayscale characteristics (distributed histogram) vs. binary
    characteristics (bimodal histogram).
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the histogram analysis strategy.

        Args:
            config: Configuration dictionary with parameters:
                - window_size: Size of sliding window (default: 32)
                - stride: Stride for window sliding (default: 16)
                - bimodality_threshold: Threshold for bimodality detection (default: 0.5)
                - scales: List of scales for multi-scale analysis (default: [1.0, 0.5, 0.25])
        """
        super().__init__(config)
        self.window_size = self.config.get("window_size", 32)
        self.stride = self.config.get("stride", 16)
        self.bimodality_threshold = self.config.get("bimodality_threshold", 0.5)
        self.scales = self.config.get("scales", [1.0, 0.5, 0.25])

    def analyze(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the image to identify binary and grayscale regions using histogram analysis.

        Args:
            image: The input image to analyze.

        Returns:
            A probability map where each pixel's value represents the likelihood
            of belonging to a grayscale region (0 = binary, 1 = grayscale).
        """
        # Ensure image is grayscale
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray_img = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray_img = image.copy()

        # Multi-scale analysis
        scale_results = []
        for scale in self.scales:
            # Resize image based on scale
            if scale != 1.0:
                h, w = gray_img.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                scaled_img = self._resize_image(gray_img, (new_h, new_w))
            else:
                scaled_img = gray_img

            # Analyze histograms at this scale
            result = self._analyze_scale(scaled_img)

            # Resize result back to original size if needed
            if scale != 1.0:
                result = self._resize_image(result, gray_img.shape[:2])

            scale_results.append(result)

        # Combine results from different scales
        combined_result = np.mean(np.stack(scale_results, axis=0), axis=0)

        return combined_result

    def _analyze_scale(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze image at a specific scale.

        Args:
            image: Image to analyze at this scale.

        Returns:
            Probability map for grayscale regions at this scale.
        """
        h, w = image.shape[:2]

        # Handle edge case where image is smaller than window
        if h < self.window_size or w < self.window_size:
            window_size = min(h, w, self.window_size)
            stride = max(1, window_size // 2)
        else:
            window_size = self.window_size
            stride = self.stride

        # Create result map (initialized to zeros)
        result_map = np.zeros((h, w), dtype=np.float32)
        count_map = np.zeros((h, w), dtype=np.float32)

        # Process sliding windows
        try:
            windows = view_as_windows(image, (window_size, window_size), stride)
            for i in range(windows.shape[0]):
                for j in range(windows.shape[1]):
                    window = windows[i, j]

                    # Calculate bimodality value for this window
                    bimodality = self._calculate_bimodality(window)

                    # DEBUG
                    if i == 0 and j == 0:
                        pixel_values, counts = np.unique(window, return_counts=True)
                        print(
                            f"Window 0,0 - Unique values: {len(pixel_values)}, Bimodality: {bimodality}"
                        )
                        print(f"Sample values: {pixel_values[:10]}")

                    # Convert to grayscale probability (higher bimodality = lower grayscale probability)
                    # Increase the probability by applying a more aggressive formula
                    # The original formula: grayscale_prob = 1.0 - min(1.0, bimodality / self.bimodality_threshold)
                    # was 0 when bimodality >= threshold. We want to be more lenient.
                    grayscale_prob = max(
                        0.2, 1.0 - min(0.8, bimodality / self.bimodality_threshold)
                    )

                    # Update result map
                    y_start = i * stride
                    x_start = j * stride
                    y_end = min(y_start + window_size, h)
                    x_end = min(x_start + window_size, w)

                    result_map[y_start:y_end, x_start:x_end] += grayscale_prob
                    count_map[y_start:y_end, x_start:x_end] += 1.0
        except ValueError:
            # Fallback for small images or edge cases
            bimodality = self._calculate_bimodality(image)
            grayscale_prob = 1.0 - min(1.0, bimodality / self.bimodality_threshold)
            result_map.fill(grayscale_prob)
            count_map.fill(1.0)

        # Average overlapping windows
        mask = count_map > 0
        result_map[mask] /= count_map[mask]

        return result_map

    def _calculate_bimodality(self, window: np.ndarray) -> float:
        """
        Calculate bimodality measure of histogram.

        Args:
            window: Image patch to analyze.

        Returns:
            Bimodality measure (higher values = more bimodal).
        """
        # Get histogram
        hist, bin_centers = histogram(window, nbins=64)
        hist = hist.astype(np.float32)

        # Normalize histogram
        hist_sum = np.sum(hist)
        if hist_sum > 0:
            hist /= hist_sum

        # Calculate variance and kurtosis
        if np.sum(hist) == 0:
            return 0.0

        # Calculate mean
        mean = np.sum(bin_centers * hist)

        # Calculate variance
        variance = np.sum(((bin_centers - mean) ** 2) * hist)
        if variance == 0:
            return 0.0

        # Calculate third and fourth moments
        m3 = np.sum(((bin_centers - mean) ** 3) * hist)
        m4 = np.sum(((bin_centers - mean) ** 4) * hist)

        # Calculate skewness and kurtosis
        skewness = m3 / (variance**1.5) if variance > 0 else 0
        kurtosis = m4 / (variance**2) if variance > 0 else 0

        # Bimodality coefficient
        bimodality = (skewness**2 + 1) / kurtosis if kurtosis > 0 else 0

        return bimodality

    def _resize_image(self, image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """
        Resize an image to the given size.

        Args:
            image: Image to resize.
            size: Target size (height, width).

        Returns:
            Resized image.
        """
        from skimage.transform import resize

        return resize(image, size, preserve_range=True).astype(image.dtype)
