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
        # Get all strategies
        detection_config = self.config.get('detection', {})
        strategies = self.strategy_provider.get_all_strategies(detection_config)
        
        # Analyze image with each strategy
        results = []
        weights = []
        for strategy in strategies:
            strategy_name = strategy.__class__.__name__.replace('Strategy', '').lower()
            if strategy_name in self.strategy_weights:
                weight = self.strategy_weights[strategy_name]
                if weight > 0:
                    results.append(strategy.analyze(image))
                    weights.append(weight)
        
        # Combine results
        if not results:
            # Fallback: create empty probability map
            probability_map = np.zeros(image.shape[:2], dtype=np.float32)
        else:
            probability_map = self.strategy_provider.combine_results(results, weights)
        
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