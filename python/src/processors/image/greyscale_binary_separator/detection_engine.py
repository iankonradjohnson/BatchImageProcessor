"""
Region detection engine for identifying grayscale and binary regions.
"""

from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .detection import DetectionStrategyProvider
from .region import Region, RegionExtractor


class RegionDetectionEngine:
    """
    Engine for detecting and segmenting grayscale and binary regions in images.
    
    This class coordinates the detection process, combining results from multiple
    detection strategies and extracting coherent regions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the detection engine.
        
        Args:
            config: Configuration dictionary with parameters:
                - strategy_weights: Dictionary of strategy weights (default: equal weights)
                - detection: Configuration for detection strategies
                - region_extraction: Configuration for region extraction
        """
        self.config = config or {}
        self.strategy_provider = DetectionStrategyProvider()
        
        # Extract configuration parts
        detection_config = self.config.get('detection', {})
        extraction_config = self.config.get('region_extraction', {})
        
        # Configure region extractor
        self.region_extractor = RegionExtractor(extraction_config)
        
        # Extract strategy weights
        self.strategy_weights = self.config.get('strategy_weights', {
            'histogram': 0.4,
            'texture': 0.4,
            'edge': 0.2
        })
        
    def detect_regions(self, image: np.ndarray) -> Tuple[List[Region], np.ndarray]:
        """
        Detect grayscale and binary regions in the image.
        
        Args:
            image: The input image to analyze.
            
        Returns:
            Tuple of (list of regions, probability map).
        """
        # Enhanced detection approach with multiple features
        
        print("USING ENHANCED DETECTION APPROACH")
        
        # Convert image to grayscale if needed
        if len(image.shape) > 2 and image.shape[2] > 1:
            gray_img = np.mean(image, axis=2).astype(np.uint8)
        else:
            gray_img = image.copy()
        
        h, w = gray_img.shape[:2]
        window_size = 32  # Smaller windows for finer detail
        stride = 16
        
        # Create a probability map
        probability_map = np.zeros((h, w), dtype=np.float32)
        
        # Import additional tools for better detection
        from skimage.feature import local_binary_pattern
        from skimage.filters import sobel
        from scipy.stats import entropy
        
        # Precompute edge map for speed
        edge_map = sobel(gray_img)
        
        # Values indicating more confidence in grayscale detection
        very_high_prob = 0.9
        high_prob = 0.7
        medium_prob = 0.5
        low_prob = 0.2
        
        print("Analyzing image regions...")
        
        # Simplified approach for speed - focus on the most important metrics
        print("Using fast detection algorithm...")
        
        # For each window, we'll only calculate the most discriminative features
        for y in range(0, h - window_size + 1, stride):
            for x in range(0, w - window_size + 1, stride):
                window = gray_img[y:y+window_size, x:x+window_size]
                
                # Just use these two key metrics:
                # 1. Unique values count - high for grayscale, low for binary
                # 2. Standard deviation - high for grayscale, low for binary or flat areas
                
                unique_values = len(np.unique(window))
                std_dev = np.std(window)
                
                # Simple decision rules for grayscale detection
                if std_dev > 25 and unique_values > 30:
                    # Definitely grayscale - high variance and many unique values
                    probability = very_high_prob
                elif std_dev > 15 and unique_values > 20:
                    # Likely grayscale
                    probability = high_prob
                elif std_dev > 10 and unique_values > 10:
                    # Possibly grayscale
                    probability = medium_prob
                elif std_dev > 5 and unique_values > 5:
                    # Slight chance of grayscale
                    probability = low_prob
                else:
                    # Likely binary
                    probability = 0.0
                
                # Set probability
                probability_map[y:y+window_size, x:x+window_size] = probability
                
        # IMPORTANT: Force grayscale for images that look like photographs
        # Calculate global metrics to detect photographic images
        global_std = np.std(gray_img)
        global_unique = len(np.unique(gray_img)) / 256.0  # Normalize by max possible
        
        print(f"Global image metrics - StdDev: {global_std:.2f}, Unique Values: {len(np.unique(gray_img))} ({global_unique:.2%})")
        
        # If the whole image looks like a photograph, force most areas to be grayscale
        if global_std > 40 and global_unique > 0.3:
            print("IMAGE APPEARS TO BE MOSTLY PHOTOGRAPHIC - Forcing grayscale detection")
            # Create a base probability for the entire image
            probability_map = np.clip(probability_map, 0.5, 1.0)
        
        # Smooth the probability map with a Gaussian filter
        from scipy.ndimage import gaussian_filter
        probability_map = gaussian_filter(probability_map, sigma=2.0)
        
        # Print stats about detection
        print(f"Enhanced detection - Min: {np.min(probability_map):.2f}, Max: {np.max(probability_map):.2f}, Mean: {np.mean(probability_map):.2f}")
        print(f"Non-zero probability pixels: {np.sum(probability_map > 0) / (h * w) * 100:.2f}%")
        
        # Extract regions
        grayscale_regions = self.region_extractor.extract_regions(probability_map)
        
        # Create binary region as inverse of grayscale regions
        if grayscale_regions:
            binary_region = self.region_extractor.invert_regions(grayscale_regions, image.shape[:2])
            regions = grayscale_regions + [binary_region]
        else:
            # If no grayscale regions, the entire image is binary
            binary_mask = np.ones(image.shape[:2], dtype=bool)
            binary_region = Region(binary_mask, 'binary', 1.0)
            regions = [binary_region]
        
        return regions, probability_map
    
    def visualize_regions(self, image: np.ndarray, regions: List[Region], probability_map: np.ndarray = None) -> np.ndarray:
        """
        Visualize detected regions.
        
        Args:
            image: The input image.
            regions: List of detected regions.
            probability_map: Optional probability map to visualize.
            
        Returns:
            Visualization image.
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        
        # Create figure
        fig, axes = plt.subplots(1, 3 if probability_map is not None else 2, figsize=(15, 5))
        
        # Show original image
        axes[0].imshow(image)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Show regions
        region_viz = np.zeros((*image.shape[:2], 3), dtype=np.uint8)
        
        # Add original image as background (darkened)
        if len(image.shape) == 3 and image.shape[2] == 3:
            region_viz = image.copy() // 2
        else:
            # Convert grayscale to RGB
            gray_img = image.copy() if len(image.shape) == 2 else np.mean(image, axis=2).astype(np.uint8)
            region_viz = np.stack([gray_img // 2] * 3, axis=2)
        
        # Add colored overlays for each region type
        for region in regions:
            if region.region_type == 'grayscale':
                # Red for grayscale regions
                region_viz[region.mask] = np.array([255, 100, 100], dtype=np.uint8)
            else:
                # Blue for binary regions
                region_viz[region.mask] = np.array([100, 100, 255], dtype=np.uint8)
        
        axes[1].imshow(region_viz)
        axes[1].set_title('Detected Regions')
        axes[1].axis('off')
        
        # Show probability map if provided
        if probability_map is not None:
            # Create colormap: blue (low) to red (high)
            cmap = LinearSegmentedColormap.from_list('my_cmap', ['blue', 'lightblue', 'yellow', 'red'])
            
            im = axes[2].imshow(probability_map, cmap=cmap, vmin=0, vmax=1)
            axes[2].set_title('Probability Map')
            axes[2].axis('off')
            plt.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
        
        # Adjust layout and convert to image
        plt.tight_layout()
        
        # Convert figure to image
        fig.canvas.draw()
        viz_image = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        
        return viz_image