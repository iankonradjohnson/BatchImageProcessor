import os
import subprocess
import logging
import tempfile
from typing import Dict, Any
from PIL import Image

from python.src.processors.image.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class Deskew(ImageProcessor):
    """
    Processor responsible for deskewing images using ImageMagick.
    This class follows SRP by focusing solely on the deskew operation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the deskew processor with configuration.
        
        Args:
            config: Configuration for deskew operations
        """
        self.enabled = config.get('enabled', True)
        self.threshold = config.get('threshold', "40%")
        self.add_border = config.get('add_border', True)
        self.border_size = config.get('border_size', "5x5")
        self.trim_borders = config.get('trim_borders', True)
        self.fuzz_value = config.get('fuzz_value', "1%")
    
    def process(self, img: Image.Image, is_left: bool = None) -> Image.Image:
        """
        Process the input image by deskewing it.

        This method implements the ImageProcessor interface by deskewing the provided
        image using ImageMagick's convert command.

        Args:
            img (Image.Image): The input image to be deskewed.
            is_left (bool, optional): Indicates if the image is the left page. Not used in deskew.

        Returns:
            Image.Image: The deskewed image.
        """
        if not self.enabled:
            logger.debug("Deskew is disabled, returning original image")
            return img
            
        # Create temporary files for input and output
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as in_file, \
             tempfile.NamedTemporaryFile(suffix='.png', delete=False) as out_file:
            
            # Save input image to temporary file
            input_path = in_file.name
            output_path = out_file.name
            img.save(input_path)
            
            try:
                cmd = ["convert", input_path]
                
                # Add deskew operation
                cmd.extend(["-deskew", self.threshold])
                
                # Add border if enabled
                if self.add_border:
                    cmd.extend(["-bordercolor", "white", "-border", self.border_size])
                
                # Trim borders if enabled
                if self.trim_borders:
                    cmd.extend(["-fuzz", self.fuzz_value, "-trim", "+repage"])
                
                # Ensure no alpha channel
                cmd.extend(["-alpha", "off"])
                
                # Add output path
                cmd.append(output_path)
                
                logger.debug(f"Running deskew command: {' '.join(cmd)}")
                subprocess.run(cmd, check=True, capture_output=True)
                
                logger.debug("Successfully deskewed image")
                
                # Read the processed image
                processed_img = Image.open(output_path)
                return processed_img
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to deskew image: {e}")
                logger.error(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No stderr'}")
                return img  # Return original image on failure
            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_path)
                    os.unlink(output_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary files: {e}")