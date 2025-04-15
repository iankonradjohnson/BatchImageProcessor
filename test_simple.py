#!/usr/bin/env python3
"""
Simple test to verify the core functionality of the component.
"""

import os
import sys
import yaml
from PIL import Image
import numpy as np
from skimage.filters import threshold_otsu
from skimage.util import img_as_ubyte
from skimage.exposure import adjust_sigmoid
from skimage.measure import label
from skimage.morphology import binary_dilation, disk
from scipy.ndimage import binary_fill_holes

# Create output directory
os.makedirs('output', exist_ok=True)

# Load a test image
input_path = 'test/input/mma_beer_street_399845.png'
if not os.path.exists(input_path):
    print(f"Input file not found: {input_path}")
    sys.exit(1)

print(f"Loading image: {input_path}")
img = Image.open(input_path)
image = np.array(img)

# Convert to grayscale if needed
if len(image.shape) > 2 and image.shape[2] > 1:
    gray_img = np.mean(image, axis=2).astype(np.uint8)
else:
    gray_img = image.copy()

print("Image loaded and converted to grayscale")

# Simple variance-based detection of grayscale regions
print("Detecting grayscale regions...")
window_size = 16
stride = 8
h, w = gray_img.shape

# Create result map
result_map = np.zeros((h, w), dtype=np.float32)
count_map = np.zeros((h, w), dtype=np.float32)

# Process image in sliding windows
for y in range(0, h - window_size + 1, stride):
    for x in range(0, w - window_size + 1, stride):
        # Extract window
        window = gray_img[y:y+window_size, x:x+window_size]
        
        # Calculate variance (high variance = more likely grayscale)
        variance = np.var(window)
        normalized_variance = min(1.0, variance / 1000.0)  # Normalize to [0, 1]
        
        # Update result map
        result_map[y:y+window_size, x:x+window_size] += normalized_variance
        count_map[y:y+window_size, x:x+window_size] += 1.0

# Average overlapping windows
mask = count_map > 0
result_map[mask] /= count_map[mask]

print("Segmenting regions...")
# Threshold the probability map
binary_map = result_map > 0.2  # Lower threshold to detect more grayscale regions
binary_map = binary_fill_holes(binary_map)

# Extract regions
labeled_map, num_regions = label(binary_map, return_num=True)
print(f"Detected {num_regions} potential grayscale regions")

# Process each region type
print("Processing regions...")
processed_image = np.zeros_like(gray_img)

# Create a mask for all grayscale regions
grayscale_mask = binary_map

# Create a mask for binary regions (inverse of grayscale)
binary_mask = ~grayscale_mask

# Process binary regions (simple thresholding)
binary_thresh = threshold_otsu(gray_img[binary_mask]) if np.any(binary_mask) else 128
binary_processed = (gray_img > binary_thresh).astype(np.uint8) * 255
processed_image[binary_mask] = binary_processed[binary_mask]

# Process grayscale regions (adjust contrast and apply dithering)
if np.any(grayscale_mask):
    # Extract grayscale regions
    grayscale_region = np.zeros_like(gray_img)
    grayscale_region[grayscale_mask] = gray_img[grayscale_mask]
    
    # Adjust contrast
    float_img = grayscale_region.astype(np.float32) / 255.0
    adjusted = adjust_sigmoid(float_img, cutoff=0.5, gain=5.0)
    adjusted = np.clip(adjusted, 0.0, 1.0)
    
    # Create binary output with error diffusion dithering
    height, width = adjusted.shape
    dithered = np.copy(adjusted)
    threshold = 0.5
    
    # Apply Floyd-Steinberg dithering
    for y in range(height-1):
        for x in range(1, width-1):
            # Skip pixels outside the grayscale mask
            if not grayscale_mask[y, x]:
                continue
                
            old_pixel = dithered[y, x]
            new_pixel = 1 if old_pixel > threshold else 0
            error = old_pixel - new_pixel
            dithered[y, x] = new_pixel
            
            # Distribute error to neighboring pixels (only if they're in the mask)
            if grayscale_mask[y, x+1]:
                dithered[y, x+1] += error * 7/16
            if grayscale_mask[y+1, x-1]:
                dithered[y+1, x-1] += error * 3/16
            if grayscale_mask[y+1, x]:
                dithered[y+1, x] += error * 5/16
            if grayscale_mask[y+1, x+1]:
                dithered[y+1, x+1] += error * 1/16
    
    # Convert back to 8-bit and apply to output image
    processed_grayscale = (dithered * 255).astype(np.uint8)
    processed_image[grayscale_mask] = processed_grayscale[grayscale_mask]

# Save the result
output_path = 'output/simple_test_result.png'
Image.fromarray(processed_image).save(output_path)
print(f"Saved processed image to: {output_path}")

# Also save the detection mask for visualization
mask_image = np.zeros((*gray_img.shape, 3), dtype=np.uint8)
mask_image[binary_mask] = [0, 0, 255]  # Blue for binary
mask_image[grayscale_mask] = [255, 0, 0]  # Red for grayscale
Image.fromarray(mask_image).save('output/detection_mask.png')
print("Saved detection mask to: output/detection_mask.png")

print("Processing completed successfully!")