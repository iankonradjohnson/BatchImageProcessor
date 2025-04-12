"""
Edge-based detection strategy for identifying grayscale regions.
"""

from typing import Dict, Any, Tuple, List, Union

import numpy as np
from skimage.filters import sobel
from skimage.transform import resize
from skimage.morphology import binary_dilation, disk

from .detection_strategy import BaseDetectionStrategy


class EdgeDetectionStrategy(BaseDetectionStrategy):
    """
    Strategy for detecting grayscale regions based on edge characteristics.
    
    This strategy analyzes edge patterns to identify regions with
    grayscale characteristics vs. binary characteristics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the edge detection strategy.
        
        Args:
            config: Configuration dictionary with parameters:
                - edge_threshold: Threshold for edge detection (default: 0.1)
                - min_edge_density: Minimum edge density for grayscale regions (default: 0.05)
                - max_edge_density: Maximum edge density for grayscale regions (default: 0.3)
                - smooth_radius: Radius for smoothing (default: 5)
                - scales: List of scales for multi-scale analysis (default: [1.0, 0.5])
        """
        super().__init__(config)
        self.edge_threshold = self.config.get('edge_threshold', 0.1)
        self.min_edge_density = self.config.get('min_edge_density', 0.05)
        self.max_edge_density = self.config.get('max_edge_density', 0.3)
        self.smooth_radius = self.config.get('smooth_radius', 5)
        self.scales = self.config.get('scales', [1.0, 0.5])
        
    def analyze(self, image: np.ndarray) -> np.ndarray:
        """
        Analyze the image to identify binary and grayscale regions using edge analysis.
        
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
                
            # Analyze edges at this scale
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
        # Compute edges
        edge_image = sobel(image)
        
        # Threshold edges
        edge_mask = edge_image > self.edge_threshold
        
        # Compute edge density using sliding window approach
        h, w = image.shape[:2]
        window_size = 32  # Size for edge density calculation
        stride = 16  # Stride for sliding window
        
        # Handle edge case where image is smaller than window
        if h < window_size or w < window_size:
            window_size = min(h, w, window_size)
            stride = max(1, window_size // 2)
            
        # Create result map
        result_map = np.zeros((h, w), dtype=np.float32)
        count_map = np.zeros((h, w), dtype=np.float32)
        
        # Calculate edge density in sliding windows
        for y in range(0, h - window_size + 1, stride):
            for x in range(0, w - window_size + 1, stride):
                window = edge_mask[y:y+window_size, x:x+window_size]
                
                # Calculate edge density
                edge_density = np.mean(window)
                
                # Convert to grayscale probability
                # - Low density: likely neither (text has some edges)
                # - Medium density: likely grayscale (photos have moderate edge density)
                # - High density: likely binary (dense text has high edge density)
                if edge_density < self.min_edge_density:
                    grayscale_prob = 0.2  # Low probability for very smooth regions
                elif edge_density > self.max_edge_density:
                    grayscale_prob = 0.3  # Low-medium probability for very dense edges (text)
                else:
                    # Scale linearly from 0.7 to 1.0 for mid-range edge densities
                    grayscale_prob = 0.7 + 0.3 * ((edge_density - self.min_edge_density) / 
                                                (self.max_edge_density - self.min_edge_density))
                
                # Update result map
                result_map[y:y+window_size, x:x+window_size] += grayscale_prob
                count_map[y:y+window_size, x:x+window_size] += 1.0
                
        # Fill in any uncovered areas
        if not np.all(count_map > 0):
            mask = count_map == 0
            nearest_indices = self._get_nearest_valid_indices(count_map > 0, mask)
            
            for y, x in zip(*np.where(mask)):
                nearest_y, nearest_x = nearest_indices[y, x]
                result_map[y, x] = result_map[nearest_y, nearest_x]
                count_map[y, x] = 1.0
                
        # Average overlapping windows
        mask = count_map > 0
        result_map[mask] /= count_map[mask]
        
        # Smooth result
        smoothed_result = self._smooth_result(result_map)
        
        return smoothed_result
    
    def _get_nearest_valid_indices(self, valid_mask: np.ndarray, query_mask: np.ndarray) -> np.ndarray:
        """
        For each point in query_mask, find the nearest point in valid_mask.
        
        Args:
            valid_mask: Boolean mask of valid points.
            query_mask: Boolean mask of query points.
            
        Returns:
            Array of indices to the nearest valid point for each query point.
        """
        valid_indices = np.array(np.where(valid_mask)).T
        nearest_indices = np.zeros((*query_mask.shape, 2), dtype=np.int32)
        
        for y, x in zip(*np.where(query_mask)):
            # Simple approach: find nearest valid point
            # For large images, a more efficient method would be needed
            min_dist = float('inf')
            nearest_y, nearest_x = 0, 0
            
            for vy, vx in valid_indices:
                dist = (y - vy) ** 2 + (x - vx) ** 2
                if dist < min_dist:
                    min_dist = dist
                    nearest_y, nearest_x = vy, vx
                    
            nearest_indices[y, x] = [nearest_y, nearest_x]
            
        return nearest_indices
    
    def _smooth_result(self, result: np.ndarray) -> np.ndarray:
        """
        Smooth the result map.
        
        Args:
            result: Result map to smooth.
            
        Returns:
            Smoothed result map.
        """
        from scipy.ndimage import gaussian_filter
        return gaussian_filter(result, sigma=self.smooth_radius / 2)
    
    def _resize_image(self, image: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """
        Resize an image to the given size.
        
        Args:
            image: Image to resize.
            size: Target size (height, width).
            
        Returns:
            Resized image.
        """
        return resize(image, size, preserve_range=True).astype(image.dtype)