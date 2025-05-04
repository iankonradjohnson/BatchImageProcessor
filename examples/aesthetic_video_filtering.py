import os
from multiprocessing import freeze_support
from aesthetic_predictor.predictor import AestheticPredictor

from batch_image_processor.processors.batch.batch_processor import BatchProcessor
from batch_image_processor.processors.pipeline.video_pipeline import VideoPipeline
from batch_image_processor.processors.video.aesthetic_video_processor import AestheticVideoProcessor

# Input file and output directory
input_file = "/Users/iankonradjohnson/Library/CloudStorage/GoogleDrive-iankonradjohnson@gmail.com/My Drive/base/abacus/ContentLibrary/books/TheGeorgianPeriod/videos/rotated/C0252.mp4"
output_dir = "/Users/iankonradjohnson/Library/CloudStorage/GoogleDrive-iankonradjohnson@gmail.com/My Drive/base/abacus/ContentLibrary/books/TheGeorgianPeriod/videos/aesthetic_filtered"

def process_video():
    # Ensure input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    # Get the directory containing the input file
    input_dir = os.path.dirname(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the aesthetic predictor
    predictor = AestheticPredictor()
    
    # Run the batch processor
    BatchProcessor(
        input_dir=input_dir,
        output_dir=output_dir,
        processors=[
            AestheticVideoProcessor(
                aesthetic_predictor=predictor,
            )
        ],
        pipeline_class=VideoPipeline,
    ).batch_process()

if __name__ == "__main__":
    process_video()