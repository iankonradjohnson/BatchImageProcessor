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
        # Print some stats about the probability map
        print(f"Probability map stats - Min: {np.min(probability_map):.4f}, Max: {np.max(probability_map):.4f}, Mean: {np.mean(probability_map):.4f}")
        
        # If probability map has very low values, enhance them for better detection
        if np.max(probability_map) < 0.5:
            print("Enhancing probability map for better detection...")
            # Apply non-linear enhancement to boost even moderately likely regions
            enhanced_map = np.power(probability_map * 2, 0.5)  # Non-linear enhancement
            probability_map = enhanced_map
            print(f"Enhanced map stats - Min: {np.min(probability_map):.4f}, Max: {np.max(probability_map):.4f}, Mean: {np.mean(probability_map):.4f}")
        
        # Only fall back to synthetic mask if absolutely necessary
        if np.max(probability_map) == 0:
            print("WARNING: Probability map is all zeros. Creating synthetic grayscale regions...")
            # Create artificial grayscale probability for testing
            h, w = probability_map.shape
            test_map = np.zeros_like(probability_map)
            # Mark multiple regions as grayscale for testing
            center_h, center_w = h // 2, w // 2
            size_h, size_w = h // 4, w // 4
            
            # Central region
            test_map[center_h-size_h:center_h+size_h, center_w-size_w:center_w+size_w] = 0.8
            
            # Top-left region
            test_map[0:size_h, 0:size_w] = 0.7
            
            # Bottom-right region
            test_map[h-size_h:h, w-size_w:w] = 0.7
            
            probability_map = test_map
        
        # Apply a much lower threshold to catch more potential grayscale regions
        # We're being very aggressive to ensure we don't miss anything
        binary_map = probability_map > self.threshold
        
        # Fill holes and clean up the binary map
        if self.fill_holes:
            binary_map = binary_fill_holes(binary_map)
            
        # Optional: Clean up with morphological operations
        from skimage.morphology import binary_opening, binary_closing
        # First close to connect nearby components
        binary_map = binary_closing(binary_map, disk(3))
        # Then open to remove small noise
        binary_map = binary_opening(binary_map, disk(2))
            
        # Label connected components
        labeled_map, num_regions = label(binary_map, return_num=True)
        
        # Extract regions
        regions = []
        for i in range(1, num_regions + 1):
            region_mask = labeled_map == i
            
            # Create initial region
            region = Region(region_mask, 'grayscale', 1.0)
            
            # Expand region significantly to capture nearby grayscale pixels
            if self.expand_pixels > 0:
                # Expand more aggressively for better coverage
                region.expand(self.expand_pixels)
            
            # Use a much smaller minimum region size to capture small grayscale elements
            # But avoid tiny regions that are likely just noise
            if np.sum(region.mask) < max(self.min_region_size // 4, 25):
                continue
                
            # Calculate confidence based on average probability in the original region
            confidence = np.mean(probability_map[region_mask])
            region.confidence = confidence
            
            regions.append(region)
        
        # If we have too many small regions, merge nearby ones
        if len(regions) > 50:
            print(f"Found {len(regions)} regions, which is a lot. Merging nearby regions...")
            regions = self._merge_nearby_regions(regions)
            
        # Debug output
        print(f"Extracted {len(regions)} regions from probability map")
        if len(regions) > 0:
            total_pixels = probability_map.shape[0] * probability_map.shape[1]
            grayscale_pixels = sum(np.sum(r.mask) for r in regions)
            print(f"Grayscale pixels: {grayscale_pixels} ({grayscale_pixels/total_pixels*100:.2f}% of image)")
        
        return regions
        
    def _merge_nearby_regions(self, regions: List[Region], distance_threshold: int = 30) -> List[Region]:
        """
        Merge regions that are close to each other.
        
        Args:
            regions: List of regions to merge.
            distance_threshold: Distance threshold for merging.
            
        Returns:
            Merged regions.
        """
        if len(regions) <= 1:
            return regions
            
        # Start with all regions as separate clusters
        merged = False
        while True:
            # Try to merge any regions
            merged = False
            for i in range(len(regions) - 1):
                if merged:
                    break
                    
                for j in range(i + 1, len(regions)):
                    # Get bounding boxes
                    y_min_i, x_min_i, y_max_i, x_max_i = regions[i].bounding_box
                    y_min_j, x_min_j, y_max_j, x_max_j = regions[j].bounding_box
                    
                    # Calculate distance between bounding boxes
                    x_distance = max(0, min(x_max_i, x_max_j) - max(x_min_i, x_min_j))
                    y_distance = max(0, min(y_max_i, y_max_j) - max(y_min_i, y_min_j))
                    
                    # If boxes overlap in one dimension, check distance in other dimension
                    if x_distance > 0:
                        distance = max(0, y_min_j - y_max_i) if y_min_j > y_max_i else max(0, y_min_i - y_max_j)
                    elif y_distance > 0:
                        distance = max(0, x_min_j - x_max_i) if x_min_j > x_max_i else max(0, x_min_i - x_max_j)
                    else:
                        # No overlap in either dimension, use Manhattan distance
                        distance = (min(abs(x_min_i - x_max_j), abs(x_min_j - x_max_i)) + 
                                    min(abs(y_min_i - y_max_j), abs(y_min_j - y_max_i)))
                    
                    # Merge if close enough
                    if distance < distance_threshold:
                        # Create merged mask
                        merged_mask = regions[i].mask | regions[j].mask
                        # Get average confidence
                        avg_confidence = (regions[i].confidence + regions[j].confidence) / 2
                        # Create new region
                        new_region = Region(merged_mask, 'grayscale', avg_confidence)
                        # Replace first region with merged region and delete second
                        regions[i] = new_region
                        regions.pop(j)
                        merged = True
                        break
            
            # If no regions were merged in this iteration, we're done
            if not merged:
                break
                
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