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
        detection_config = self.config.get("detection", {})
        processing_config = self.config.get("processing", {})

        # Initialize engines
        self.detection_engine = RegionDetectionEngine(detection_config)
        self.processing_engine = RegionProcessingEngine(processing_config)

        # Visualization settings
        self.save_visualization = self.config.get("save_visualization", False)
        self.visualization_path = self.config.get("visualization_path", ".")

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

            # Generate and save detection report
            self._generate_detection_report(image, regions, probability_map)

            # Process regions
            processed_image = self.processing_engine.process_regions(image, regions)

            # Save visualization if enabled
            if self.save_visualization:
                # Calculate shape metrics for visualization
                shape_metrics = {}
                from skimage.measure import regionprops

                for i, region in enumerate(regions):
                    if region.region_type == "grayscale":
                        # Create a temporary mask just for shape analysis
                        tmp_mask = region.mask.astype(np.uint8)
                        props = regionprops(tmp_mask)
                        if props:
                            prop = props[0]
                            area = prop.area
                            perimeter = prop.perimeter
                            perimeter_area_ratio = perimeter / area if area > 0 else 0
                            circularity = (
                                (4 * np.pi * area) / (perimeter * perimeter)
                                if perimeter > 0
                                else 0
                            )
                            shape_metrics[i] = {
                                "area": area,
                                "perimeter": perimeter,
                                "perimeter_area_ratio": perimeter_area_ratio,
                                "circularity": circularity,
                            }

                self._save_visualizations(
                    image,
                    regions,
                    probability_map,
                    processed_image,
                    shape_metrics=shape_metrics,
                )

            # Convert back to PIL image and return
            return Image.fromarray(processed_image)

        except Exception as e:
            raise GreyscaleBinarySeparatorError(
                f"Error processing image: {str(e)}"
            ) from e

    def _generate_detection_report(
        self, image: np.ndarray, regions: List[Region], probability_map: np.ndarray
    ) -> None:
        """
        Generate a report on the detection results.

        Args:
            image: The input image.
            regions: List of detected regions.
            probability_map: The probability map.
        """
        import os
        import json
        from datetime import datetime

        # Create output directory if it doesn't exist
        report_dir = os.path.join(self.visualization_path, "reports")
        os.makedirs(report_dir, exist_ok=True)

        # Get image dimensions
        image_height, image_width = image.shape[:2]
        total_pixels = image_height * image_width

        # Calculate metrics
        grayscale_pixels = 0
        binary_pixels = 0
        grayscale_regions_count = 0
        binary_regions_count = 0

        for region in regions:
            region_pixels = np.sum(region.mask)
            if region.region_type == "grayscale":
                grayscale_pixels += region_pixels
                grayscale_regions_count += 1
            else:
                binary_pixels += region_pixels
                binary_regions_count += 1

        # Calculate percentages
        grayscale_percentage = (grayscale_pixels / total_pixels) * 100
        binary_percentage = (binary_pixels / total_pixels) * 100

        # Average probability across the map
        avg_probability = np.mean(probability_map)

        # Calculate histogram of probabilities
        hist, bins = np.histogram(probability_map, bins=10, range=(0, 1))
        hist_data = [int(count) for count in hist]
        bin_edges = [float(edge) for edge in bins[:-1]]

        # Create report data
        report = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "image_dimensions": {
                "width": int(image_width),
                "height": int(image_height),
                "total_pixels": int(total_pixels),
            },
            "detection_results": {
                "grayscale_regions_count": grayscale_regions_count,
                "binary_regions_count": binary_regions_count,
                "grayscale_pixels": int(grayscale_pixels),
                "binary_pixels": int(binary_pixels),
                "grayscale_percentage": float(grayscale_percentage),
                "binary_percentage": float(binary_percentage),
            },
            "probability_stats": {
                "average_probability": float(avg_probability),
                "probability_histogram": {"bins": bin_edges, "counts": hist_data},
            },
            "configuration": {
                "region_extraction": self.config.get("detection", {}).get(
                    "region_extraction", {}
                ),
                "strategy_weights": self.config.get("detection", {}).get(
                    "strategy_weights", {}
                ),
            },
        }

        # Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(report_dir, f"detection_report_{timestamp}.json")

        # Save the report as JSON
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Print a summary to console for immediate feedback
        print(f"\n==== Detection Report Summary ====")
        print(f"Image size: {image_width}x{image_height} ({total_pixels} pixels)")
        print(
            f"Grayscale regions: {grayscale_regions_count} regions, {grayscale_percentage:.2f}% of image"
        )
        print(
            f"Binary regions: {binary_regions_count} regions, {binary_percentage:.2f}% of image"
        )
        print(f"Average probability: {avg_probability:.4f}")
        print(f"Full report saved to: {report_path}")
        print(f"===================================\n")

    def _save_visualizations(
        self,
        image: np.ndarray,
        regions: List[Region],
        probability_map: np.ndarray,
        processed_image: np.ndarray,
        output_prefix: str = "visualization",
        shape_metrics: Dict = None,
    ) -> None:
        """
        Save visualization images.

        Args:
            image: The original input image.
            regions: The detected regions.
            probability_map: The probability map.
            processed_image: The processed image.
            output_prefix: Prefix for output files.
            shape_metrics: Optional dictionary of shape metrics for regions.
        """
        import os
        import matplotlib.pyplot as plt
        from datetime import datetime

        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate detection visualization with shape metrics
        detection_viz = self.detection_engine.visualize_regions(
            image, regions, probability_map, shape_metrics
        )

        # Generate processing visualization
        processing_viz = self.processing_engine.visualize_processing(
            image, regions, processed_image
        )

        # Convert to PIL images for saving
        detection_pil = Image.fromarray(detection_viz)
        processing_pil = Image.fromarray(processing_viz)

        # Save images
        detection_path = os.path.join(
            self.visualization_path, f"{output_prefix}_detection_{timestamp}.png"
        )
        processing_path = os.path.join(
            self.visualization_path, f"{output_prefix}_processing_{timestamp}.png"
        )

        detection_pil.save(detection_path)
        processing_pil.save(processing_path)

        # Generate and save additional diagnostic visualizations
        self._save_diagnostic_visualizations(image, regions, probability_map, timestamp)

    def _save_diagnostic_visualizations(
        self,
        image: np.ndarray,
        regions: List[Region],
        probability_map: np.ndarray,
        timestamp: str,
    ) -> None:
        """
        Generate and save diagnostic visualizations.

        Args:
            image: The original input image.
            regions: The detected regions.
            probability_map: The probability map.
            timestamp: Timestamp string for file naming.
        """
        import os
        import matplotlib.pyplot as plt
        import numpy as np

        diagnostics_dir = os.path.join(self.visualization_path, "diagnostics")
        os.makedirs(diagnostics_dir, exist_ok=True)

        # 1. Probability Histogram
        plt.figure(figsize=(10, 6))
        plt.hist(probability_map.flatten(), bins=50, range=(0, 1), alpha=0.7)
        plt.grid(True, alpha=0.3)
        plt.xlabel("Probability Value")
        plt.ylabel("Pixel Count")
        plt.title("Distribution of Grayscale Detection Probability")

        # Add vertical line at the threshold
        threshold = (
            self.config.get("detection", {})
            .get("region_extraction", {})
            .get("threshold", 0.5)
        )
        plt.axvline(
            x=threshold, color="r", linestyle="--", label=f"Threshold ({threshold})"
        )
        plt.legend()

        # Save histogram
        hist_path = os.path.join(
            diagnostics_dir, f"probability_histogram_{timestamp}.png"
        )
        plt.savefig(hist_path, dpi=150)
        plt.close()

        # 2. Grayscale Regions Mask
        plt.figure(figsize=(10, 10))

        # Create a mask of all grayscale regions
        grayscale_mask = np.zeros(image.shape[:2], dtype=bool)
        for region in regions:
            if region.region_type == "grayscale":
                grayscale_mask |= region.mask

        # Display the mask
        plt.imshow(grayscale_mask, cmap="gray")
        plt.title("Grayscale Regions Mask")
        plt.axis("off")

        # Save mask
        mask_path = os.path.join(diagnostics_dir, f"grayscale_mask_{timestamp}.png")
        plt.savefig(mask_path, dpi=150)
        plt.close()

        # 3. Probability Map Heatmap
        plt.figure(figsize=(10, 10))
        plt.imshow(probability_map, cmap="hot", vmin=0, vmax=1)
        plt.colorbar(label="Probability")
        plt.title("Grayscale Detection Probability Map")
        plt.axis("off")

        # Save heatmap
        heatmap_path = os.path.join(
            diagnostics_dir, f"probability_heatmap_{timestamp}.png"
        )
        plt.savefig(heatmap_path, dpi=150)
        plt.close()

        # 4. Region Size Distribution
        region_sizes = []
        region_types = []
        for region in regions:
            size = np.sum(region.mask)
            region_sizes.append(size)
            region_types.append(region.region_type)

        if region_sizes:
            plt.figure(figsize=(10, 6))

            # Create separate lists for grayscale and binary regions
            grayscale_sizes = [
                size
                for size, rtype in zip(region_sizes, region_types)
                if rtype == "grayscale"
            ]
            binary_sizes = [
                size
                for size, rtype in zip(region_sizes, region_types)
                if rtype == "binary"
            ]

            # Plot histograms
            if grayscale_sizes:
                plt.hist(grayscale_sizes, bins=20, alpha=0.7, label="Grayscale Regions")
            if binary_sizes:
                plt.hist(binary_sizes, bins=20, alpha=0.7, label="Binary Regions")

            plt.grid(True, alpha=0.3)
            plt.xlabel("Region Size (pixels)")
            plt.ylabel("Count")
            plt.title("Distribution of Region Sizes")
            plt.legend()

            # Save size distribution
            sizes_path = os.path.join(diagnostics_dir, f"region_sizes_{timestamp}.png")
            plt.savefig(sizes_path, dpi=150)
            plt.close()
