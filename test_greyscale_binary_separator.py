#!/usr/bin/env python3
"""
Test script for the Greyscale Binary Separator processor.
"""

import os
import sys
import yaml
import numpy as np
from PIL import Image

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from python.src.processors.image.greyscale_binary_separator.greyscale_binary_separator import GreyscaleBinarySeparator


def main():
    """
    Test the Greyscale Binary Separator processor.
    """
    # Load configuration
    with open('config/greyscale_binary_separator.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Create processor
    processor = GreyscaleBinarySeparator(config)
    
    # Load image
    input_path = 'test/input/mma_beer_street_399845.png'
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return
    
    image = np.array(Image.open(input_path))
    
    # Process image
    try:
        print(f"Processing image: {input_path}")
        processed_image = processor.process_image(image)
        
        # Save processed image
        output_path = 'output/processed_image.png'
        Image.fromarray(processed_image).save(output_path)
        print(f"Saved processed image to: {output_path}")
        print("Processing completed successfully.")
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()