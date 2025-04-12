"""
Greyscale Binary Separator processor.

This processor automatically detects and separately processes grayscale and binary
regions in document images.
"""

from typing import Dict, Any, List, Tuple, Optional, Union

import numpy as np
from PIL import Image

from ..image_processor import ImageProcessor
from .detection_engine import RegionDetectionEngine
from .processing_engine import RegionProcessingEngine
from .region import Region
from .exceptions import GreyscaleBinarySeparatorError


class GreyscaleBinarySeparator(ImageProcessor):
    """
    Processor for detecting and separately processing grayscale and binary regions in images.
    
    This processor automatically identifies grayscale regions (photographs, lithographs)
    and binary regions (text, engravings) in an image and applies appropriate processing
    to each region type:
    - Binary regions: Threshold without dithering
    - Grayscale regions: Brightness/contrast adjustment and threshold with dithering
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the processor with configuration.
        
        Args:
            config: Configuration dictionary with parameters:
                - detection: Configuration for the detection engine
                - processing: Configuration for the processing engine
                - save_visualization: Whether to save visualization images (default: False)
                - visualization_path: Directory to save visualizations (default: '.')
        """
        super().__init__()
        self.config = config or {}
        
        # Extract configuration parts
        detection_config = self.config.get('detection', {})
        processing_config = self.config.get('processing', {})
        
        # Initialize engines
        self.detection_engine = RegionDetectionEngine(detection_config)
        self.processing_engine = RegionProcessingEngine(processing_config)
        
        # Visualization settings
        self.save_visualization = self.config.get('save_visualization', False)
        self.visualization_path = self.config.get('visualization_path', '.')
        
    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Process an image, detecting and separately processing grayscale and binary regions.
        
        Args:
            img: The input PIL image to process.
            is_left: Flag indicating if this is a left page (not used in this processor).
            
        Returns:
            The processed PIL image.
            
        Raises:
            GreyscaleBinarySeparatorError: If processing fails.
        """
        try:
            # Convert PIL image to numpy array for processing
            image = np.array(img)
            
            # Detect regions
            regions, probability_map = self.detection_engine.detect_regions(image)
            
            # Process regions
            processed_image = self.processing_engine.process_regions(image, regions)
            
            # Save visualization if enabled
            if self.save_visualization:
                self._save_visualizations(image, regions, probability_map, processed_image)
                
            # Convert back to PIL image and return
            return Image.fromarray(processed_image)
            
        except Exception as e:
            raise GreyscaleBinarySeparatorError(f"Error processing image: {str(e)}") from e
            
    def _save_visualizations(
            self, 
            image: np.ndarray, 
            regions: List[Region], 
            probability_map: np.ndarray,
            processed_image: np.ndarray,
            output_prefix: str = 'visualization'
        ) -> None:
        """
        Save visualization images.
        
        Args:
            image: The original input image.
            regions: The detected regions.
            probability_map: The probability map.
            processed_image: The processed image.
            output_prefix: Prefix for output files.
        """
        import os
        from datetime import datetime
        
        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate detection visualization
        detection_viz = self.detection_engine.visualize_regions(image, regions, probability_map)
        
        # Generate processing visualization
        processing_viz = self.processing_engine.visualize_processing(image, regions, processed_image)
        
        # Convert to PIL images for saving
        detection_pil = Image.fromarray(detection_viz)
        processing_pil = Image.fromarray(processing_viz)
        
        # Save images
        detection_path = os.path.join(self.visualization_path, f'{output_prefix}_detection_{timestamp}.png')
        processing_path = os.path.join(self.visualization_path, f'{output_prefix}_processing_{timestamp}.png')
        
        detection_pil.save(detection_path)
        processing_pil.save(processing_path)