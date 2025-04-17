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
        
        # We'll add some preprocessing to detect line/text features but with less sensitivity
        print("Preprocessing image to detect text and line elements...")
        
        # Import additional tools needed for line detection
        from skimage.feature import canny
        from skimage.morphology import skeletonize
        from scipy.ndimage import gaussian_filter
        
        # DIFFERENT APPROACH: Use local binary patterns to detect text
        from skimage.feature import local_binary_pattern
        
        # Calculate LBP
        radius = 2
        n_points = 8
        lbp = local_binary_pattern(gray_img, n_points, radius, 'uniform')
        
        # Create a binary mask of areas with high LBP variance (textured areas)
        from scipy.ndimage import uniform_filter
        
        # Calculate local variance of LBP
        window_size = 21
        lbp_mean = uniform_filter(lbp, size=window_size)
        lbp_sqr_mean = uniform_filter(lbp**2, size=window_size)
        lbp_variance = lbp_sqr_mean - lbp_mean**2
        
        # Threshold variance to find text-like texture
        text_line_threshold = 10
        text_line_mask = lbp_variance > text_line_threshold
        
        # Use moderate dilation to cover text areas properly
        from skimage.morphology import binary_dilation, disk
        text_line_mask = binary_dilation(text_line_mask, disk(2))
        
        # Create a visualization of detected text/lines if needed
        # plt.figure(figsize=(10, 10))
        # plt.imshow(text_line_mask, cmap='gray')
        # plt.title('Detected Text and Line Features')
        # plt.axis('off')
        # plt.savefig(os.path.join(self.config.get('visualization_path', '.'), 'text_line_mask.png'))
        # plt.close()
        
        print(f"Identified approximately {np.sum(text_line_mask) / (h * w) * 100:.2f}% of the image as text/line features")

        # For each window, we'll only calculate the most discriminative features
        for y in range(0, h - window_size + 1, stride):
            for x in range(0, w - window_size + 1, stride):
                window = gray_img[y:y+window_size, x:x+window_size]
                
                # Key metrics:
                # 1. Unique values count - high for grayscale, low for binary
                # 2. Standard deviation - high for grayscale, low for binary or flat areas
                # 3. Text/line density - high for text/line areas, low for photos
                
                unique_values = len(np.unique(window))
                std_dev = np.std(window)
                
                # NEW: Check if this window contains significant text/line features
                window_text_mask = text_line_mask[y:y+window_size, x:x+window_size]
                text_density = np.mean(window_text_mask) if window_text_mask.size > 0 else 0
                
                # Calculate probability based on all factors
                
                # If high text/line density, force this to be classified as binary
                # Using a higher threshold to be less aggressive
                if text_density > 0.4:  # More than 40% of window is text/lines
                    probability = 0.0  # Force to be considered binary
                # Otherwise use our standard rules
                elif std_dev > 35 and unique_values > 40:
                    # Definitely grayscale - high variance and many unique values
                    probability = very_high_prob
                elif std_dev > 25 and unique_values > 30:
                    # Likely grayscale
                    probability = high_prob
                elif std_dev > 20 and unique_values > 20:
                    # Possibly grayscale
                    probability = medium_prob
                elif std_dev > 15 and unique_values > 15:
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
        # Using much higher thresholds for even less sensitivity (only clear photos)
        if global_std > 80 and global_unique > 0.6:
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
    
    def visualize_regions(self, image: np.ndarray, regions: List[Region], probability_map: np.ndarray = None, shape_metrics: Dict = None) -> np.ndarray:
        """
        Visualize detected regions.
        
        Args:
            image: The input image.
            regions: List of detected regions.
            probability_map: Optional probability map to visualize.
            shape_metrics: Optional dictionary of shape metrics for regions.
            
        Returns:
            Visualization image.
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        
        # Create figure with 4 subplots to show text detection
        fig, axes = plt.subplots(1, 4, figsize=(20, 5))
        
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
        
        # If we have shape metrics, annotate the regions
        if shape_metrics:
            # Calculate region centroids for annotation placement
            for i, region in enumerate(regions):
                if region.region_type == 'grayscale' and i in shape_metrics:
                    # Find centroid of the region
                    y_indices, x_indices = np.where(region.mask)
                    if len(y_indices) > 0 and len(x_indices) > 0:
                        centroid_y = int(np.mean(y_indices))
                        centroid_x = int(np.mean(x_indices))
                        
                        # Create annotation text
                        metrics = shape_metrics[i]
                        area = metrics['area']
                        circularity = metrics['circularity']
                        ratio = metrics['perimeter_area_ratio']
                        
                        # Add annotation
                        axes[1].text(centroid_x, centroid_y, f"Area: {area}\nCirc: {circularity:.2f}\nP/A: {ratio:.3f}",
                                    color='white', fontsize=8, ha='center', va='center',
                                    bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        axes[1].set_title('Detected Regions (with Shape Metrics)')
        axes[1].axis('off')
        
        # Show probability map
        if probability_map is not None:
            # Create colormap: blue (low) to red (high)
            cmap = LinearSegmentedColormap.from_list('my_cmap', ['blue', 'lightblue', 'yellow', 'red'])
            
            im = axes[2].imshow(probability_map, cmap=cmap, vmin=0, vmax=1)
            axes[2].set_title('Grayscale Probability Map')
            axes[2].axis('off')
            plt.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
        
        # Show text/line detection mask
        try:
            # Recreate the text/line mask for visualization
            if len(image.shape) > 2 and image.shape[2] > 1:
                gray_img = np.mean(image, axis=2).astype(np.uint8)
            else:
                gray_img = image.copy()
                
            # Use local binary patterns to detect text
            from skimage.feature import local_binary_pattern
            from skimage.morphology import binary_dilation, disk
            from scipy.ndimage import uniform_filter
            
            # Calculate LBP
            radius = 2
            n_points = 8
            lbp = local_binary_pattern(gray_img, n_points, radius, 'uniform')
            
            # Calculate local variance of LBP
            window_size = 21
            lbp_mean = uniform_filter(lbp, size=window_size)
            lbp_sqr_mean = uniform_filter(lbp**2, size=window_size)
            lbp_variance = lbp_sqr_mean - lbp_mean**2
            
            # Threshold variance to find text-like texture
            text_line_threshold = 10
            text_line_mask = lbp_variance > text_line_threshold
            text_line_mask = binary_dilation(text_line_mask, disk(2))
            
            # Create text mask visualization (overlay on darkened image)
            text_viz = np.zeros((*image.shape[:2], 3), dtype=np.uint8)
            
            if len(image.shape) == 3 and image.shape[2] == 3:
                text_viz = image.copy() // 2
            else:
                text_viz = np.stack([gray_img // 2] * 3, axis=2)
                
            # Green overlay for text/line areas
            text_viz[text_line_mask] = np.array([50, 255, 50], dtype=np.uint8)
            
            axes[3].imshow(text_viz)
            axes[3].set_title('Detected Text & Lines')
            axes[3].axis('off')
        except Exception as e:
            # If text visualization fails, just show a blank image
            print(f"Warning: Text visualization failed - {e}")
            axes[3].imshow(np.zeros_like(region_viz))
            axes[3].set_title('Text Detection (Failed)')
            axes[3].axis('off')
        
        # Adjust layout and convert to image
        plt.tight_layout()
        
        # Convert figure to image
        fig.canvas.draw()
        viz_image = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close(fig)
        
        return viz_image