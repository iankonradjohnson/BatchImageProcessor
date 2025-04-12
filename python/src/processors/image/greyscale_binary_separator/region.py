"""
Region representation and processing utilities.
"""

from typing import Dict, Any, Tuple, List, Optional, Set

import numpy as np
from skimage.measure import label, regionprops
from skimage.morphology import binary_dilation, disk
from scipy.ndimage import binary_fill_holes


class Region:
    """
    Represents a detected region in an image.
    """
    
    def __init__(self, mask: np.ndarray, region_type: str, confidence: float = 1.0):
        """
        Initialize a region.
        
        Args:
            mask: Binary mask representing the region.
            region_type: Type of region ('binary' or 'grayscale').
            confidence: Confidence score for the detection (0-1).
        """
        self.mask = mask.astype(bool)
        self.region_type = region_type
        self.confidence = confidence
        self._bounding_box = None
        
    @property
    def bounding_box(self) -> Tuple[int, int, int, int]:
        """
        Get the bounding box of the region (y_min, x_min, y_max, x_max).
        
        Returns:
            Tuple of (y_min, x_min, y_max, x_max).
        """
        if self._bounding_box is None:
            rows, cols = np.where(self.mask)
            if len(rows) == 0 or len(cols) == 0:
                self._bounding_box = (0, 0, 0, 0)
            else:
                y_min, y_max = np.min(rows), np.max(rows)
                x_min, x_max = np.min(cols), np.max(cols)
                self._bounding_box = (y_min, x_min, y_max, x_max)
        return self._bounding_box
    
    def expand(self, pixels: int) -> None:
        """
        Expand the region by a specified number of pixels.
        
        Args:
            pixels: Number of pixels to expand the region by.
        """
        if pixels <= 0:
            return
            
        # Create a structuring element (disk) for dilation
        selem = disk(pixels)
        
        # Dilate the mask
        self.mask = binary_dilation(self.mask, selem)
        
        # Invalidate cached bounding box
        self._bounding_box = None


class RegionExtractor:
    """
    Utility for extracting regions from a probability map.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the region extractor.
        
        Args:
            config: Configuration dictionary with parameters:
                - threshold: Probability threshold for region detection (default: 0.5)
                - min_region_size: Minimum region size in pixels (default: 1000)
                - expand_pixels: Pixels to expand regions by (default: 5)
                - fill_holes: Whether to fill holes in regions (default: True)
        """
        self.config = config or {}
        self.threshold = self.config.get('threshold', 0.5)
        self.min_region_size = self.config.get('min_region_size', 1000)
        self.expand_pixels = self.config.get('expand_pixels', 5)
        self.fill_holes = self.config.get('fill_holes', True)
        
    def extract_regions(self, probability_map: np.ndarray) -> List[Region]:
        """
        Extract regions from a probability map.
        
        Args:
            probability_map: Probability map where each pixel's value represents the likelihood
                of belonging to a grayscale region.
                
        Returns:
            List of Region objects.
        """
        # Threshold the probability map
        binary_map = probability_map > self.threshold
        
        # Fill holes if enabled
        if self.fill_holes:
            binary_map = binary_fill_holes(binary_map)
            
        # Label connected components
        labeled_map, num_regions = label(binary_map, return_num=True)
        
        # Extract regions
        regions = []
        for i in range(1, num_regions + 1):
            region_mask = labeled_map == i
            
            # Skip small regions
            if np.sum(region_mask) < self.min_region_size:
                continue
                
            # Calculate confidence based on average probability
            confidence = np.mean(probability_map[region_mask])
            
            # Create region
            region = Region(region_mask, 'grayscale', confidence)
            
            # Expand region if needed
            if self.expand_pixels > 0:
                region.expand(self.expand_pixels)
                
            regions.append(region)
            
        return regions
    
    def create_region_mask(self, regions: List[Region], shape: Tuple[int, int]) -> np.ndarray:
        """
        Create a binary mask from a list of regions.
        
        Args:
            regions: List of Region objects.
            shape: Shape of the output mask (height, width).
            
        Returns:
            Binary mask where 1 indicates regions.
        """
        mask = np.zeros(shape, dtype=bool)
        for region in regions:
            mask |= region.mask
        return mask
    
    def invert_regions(self, regions: List[Region], shape: Tuple[int, int]) -> Region:
        """
        Create a region representing the inverse of the given regions.
        
        Args:
            regions: List of Region objects.
            shape: Shape of the image (height, width).
            
        Returns:
            Region object representing everything not in the input regions.
        """
        # Create mask of all regions
        all_regions_mask = self.create_region_mask(regions, shape)
        
        # Invert the mask
        inverse_mask = ~all_regions_mask
        
        # Create inverse region
        inverse_region = Region(inverse_mask, 'binary', 1.0)
        
        return inverse_region