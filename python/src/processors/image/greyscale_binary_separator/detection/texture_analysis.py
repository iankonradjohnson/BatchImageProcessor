"""
Texture-based detection strategy for identifying grayscale regions.
"""

from typing import Dict, Any, Tuple, List, Union

import numpy as np
from skimage.util import view_as_windows
from skimage.feature import local_binary_pattern
from skimage.transform import resize

from .detection_strategy import BaseDetectionStrategy


class TextureAnalysisStrategy(BaseDetectionStrategy):
    """
    Strategy for detecting grayscale regions based on texture analysis.
    
    This strategy uses texture features (LBP) to identify regions with
    grayscale characteristics vs. binary characteristics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the texture analysis strategy.
        
        Args:
            config: Configuration dictionary with parameters:
                - window_size: Size of sliding window (default: 32)
                - stride: Stride for window sliding (default: 16)
                - lbp_radius: Radius for local binary pattern (default: 3)
                - lbp_points: Number of points for LBP (default: 24)
                - texture_threshold: Threshold for texture detection (default: 0.3)
        """
        super().__init__(config)
        self.window_size = self.config.get('window_size', 32)
        self.stride = self.config.get('stride', 16)
        self.lbp_radius = self.config.get('lbp_radius', 3)
        self.lbp_points = self.config.get('lbp_points', 24)
        self.texture_threshold = self.config.get('texture_threshold', 0.3)
        
    def analyze(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the image to identify binary and grayscale regions using texture analysis.
        
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
            
        # Compute LBP feature image
        lbp_image = self._compute_lbp(gray_img)
        
        # Analyze texture using sliding windows
        h, w = gray_img.shape[:2]
        
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
            windows_lbp = view_as_windows(lbp_image, (window_size, window_size), stride)
            windows_gray = view_as_windows(gray_img, (window_size, window_size), stride)
            
            for i in range(windows_lbp.shape[0]):
                for j in range(windows_lbp.shape[1]):
                    window_lbp = windows_lbp[i, j]
                    window_gray = windows_gray[i, j]
                    
                    # Calculate texture measure for this window
                    texture_measure = self._calculate_texture_measure(window_lbp, window_gray)
                    
                    # Convert to grayscale probability
                    grayscale_prob = min(1.0, texture_measure / self.texture_threshold)
                    
                    # Update result map
                    y_start = i * stride
                    x_start = j * stride
                    y_end = min(y_start + window_size, h)
                    x_end = min(x_start + window_size, w)
                    
                    result_map[y_start:y_end, x_start:x_end] += grayscale_prob
                    count_map[y_start:y_end, x_start:x_end] += 1.0
        except ValueError:
            # Fallback for small images or edge cases
            texture_measure = self._calculate_texture_measure(lbp_image, gray_img)
            grayscale_prob = min(1.0, texture_measure / self.texture_threshold)
            result_map.fill(grayscale_prob)
            count_map.fill(1.0)
            
        # Average overlapping windows
        mask = count_map > 0
        result_map[mask] /= count_map[mask]
        
        return result_map
    
    def _compute_lbp(self, image: np.ndarray) -> np.ndarray:
        """
        Compute Local Binary Pattern features for the image.
        
        Args:
            image: Grayscale image to analyze.
            
        Returns:
            LBP feature image.
        """
        # Compute LBP
        lbp = local_binary_pattern(image, self.lbp_points, self.lbp_radius, method='uniform')
        return lbp
    
    def _calculate_texture_measure(self, lbp_window: np.ndarray, gray_window: np.ndarray) -> float:
        """
        Calculate texture measure for a window.
        
        Args:
            lbp_window: LBP features for window.
            gray_window: Grayscale intensities for window.
            
        Returns:
            Texture measure (higher values = more texture = more likely grayscale).
        """
        # Compute LBP histogram
        max_lbp_val = self.lbp_points + 2
        hist, _ = np.histogram(lbp_window, bins=max_lbp_val, range=(0, max_lbp_val))
        hist = hist.astype(np.float32)
        
        # Normalize histogram
        hist_sum = np.sum(hist)
        if hist_sum > 0:
            hist /= hist_sum
            
        # Calculate entropy of histogram (higher entropy = more texture = more likely grayscale)
        non_zero_mask = hist > 0
        if np.any(non_zero_mask):
            entropy = -np.sum(hist[non_zero_mask] * np.log2(hist[non_zero_mask]))
        else:
            entropy = 0
            
        # Calculate variance of grayscale intensities (higher variance = more likely grayscale)
        variance = np.var(gray_window)
        normalized_variance = min(1.0, variance / 2500.0)  # Normalize to [0, 1] range
        
        # Combine entropy and variance as texture measure
        texture_measure = 0.5 * entropy / np.log2(max_lbp_val) + 0.5 * normalized_variance
        
        return texture_measure