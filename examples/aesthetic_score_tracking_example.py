"""
Example script demonstrating how to use the AestheticVideoProcessor with score tracking.

This script processes videos and saves aesthetic scores to a JSON file.
"""

import os
import sys
import json
from aesthetic_predictor import AestheticPredictor

# Add the project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from batch_image_processor.processors.video.aesthetic_video_processor import AestheticVideoProcessor
from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline
from batch_image_processor.factory.video_processor_factory import VideoProcessorFactory

def main():
    # Set up directories
    input_dir = "input"
    output_dir = "output"
    scores_output_path = os.path.join(output_dir, "aesthetic_scores.json")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the aesthetic predictor
    predictor = AestheticPredictor()
    
    # Create the AestheticVideoProcessor with score tracking
    aesthetic_processor = AestheticVideoProcessor(
        aesthetic_predictor=predictor,
        threshold=5.0,  # Minimum aesthetic score to keep
        sample_rate=1.0,  # Sample 1 frame per second
        min_segment_duration=2.0,  # Minimum segment duration in seconds
        combine_adjacent_segments=True,  # Combine adjacent good segments
        scores_output_path=scores_output_path  # Where to save the scores
    )
    
    # Create a batch processor with our aesthetic processor
    batch_processor = BatchProcessor(
        input_dir=input_dir,
        output_dir=output_dir,
        processors=[aesthetic_processor],
        pipeline_class=VideoPipeline
    )
    
    # Process all videos
    print(f"Processing videos in {input_dir}")
    batch_processor.batch_process()
    
    # Print the scores
    if os.path.exists(scores_output_path):
        with open(scores_output_path, 'r') as f:
            scores = json.load(f)
        
        print("\nAesthetic Scores:")
        for path, score in scores.items():
            print(f"  {path}: {score:.2f}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()