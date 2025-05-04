"""
A pipeline for processing video files.

This module provides an implementation of the MediaPipeline protocol for
processing video files through a series of video processors.
"""

import os.path
from typing import List, Optional
import logging

from batch_image_processor.processors.media_processor import MediaProcessor
from batch_image_processor.processors.pipeline.image_pipeline import MediaPipeline
from batch_image_processor.processors.video.video_clip import VideoClip
from batch_image_processor.factory.video_processor_factory import VideoProcessorFactory


class VideoPipeline(MediaPipeline[VideoClip]):
    """
    A pipeline for processing video files.
    
    This class implements the MediaPipeline protocol for VideoClip objects.
    """
    
    def __init__(
        self, processors: List[MediaProcessor[VideoClip]], input_dir: str, output_dir: str, deleted_dir: Optional[str] = None
    ):
        """
        Initialize the video pipeline.
        
        Args:
            processors: List of video processors to apply
            input_dir: Directory containing input videos
            output_dir: Directory to save processed videos
            deleted_dir: Directory to save filtered videos (optional)
        """
        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.deleted_dir = deleted_dir
        self.logger = logging.getLogger(__name__)

    def process_and_save(self, filepath: str) -> None:
        """
        Process a video file and save the results.
        
        Args:
            filepath: Path to the video file relative to input_dir
        """
        try:
            split = os.path.basename(filepath).split(".")
            basename, ext = ".".join(split[:-1]), split[-1]
            video_path = os.path.join(self.input_dir, filepath)

            # Create output directory if it doesn't exist
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
                
            # Create deleted directory if specified and it doesn't exist
            if self.deleted_dir and not os.path.exists(self.deleted_dir):
                os.makedirs(self.deleted_dir, exist_ok=True)

            # Load the video using the VideoProcessorFactory
            clip = VideoProcessorFactory.create_video_clip(video_path)
            
            # Process the video through all processors
            clips = [clip]
            for processor in self.processors:
                new_clips = []
                for c in clips:
                    result = processor.process(c)
                    
                    # Handle None result (filtered out)
                    if result is None:
                        if self.deleted_dir:
                            deleted_path = os.path.join(self.deleted_dir, os.path.basename(filepath))
                            c.save(deleted_path)
                        c.close()
                        continue
                        
                    # Handle list result (splitting)
                    if isinstance(result, list):
                        new_clips.extend(result)
                    # Handle single clip result
                    else:
                        new_clips.append(result)
                        
                    # Close original clip if it's different from the result
                    if c != result and c not in (result if isinstance(result, list) else [result]):
                        c.close()
                        
                # Update clips for next processor
                clips = new_clips
                
                # If all clips were filtered out, stop processing
                if not clips:
                    return
            
            # Save all the processed clips with unique names
            for i, clip in enumerate(clips):
                if len(clips) == 1:
                    # If there's only one clip, use the original filename
                    save_path = os.path.join(self.output_dir, f"{basename}.mp4")
                else:
                    # If there are multiple clips, add an index to make filenames unique
                    save_path = os.path.join(self.output_dir, f"{basename}_{i+1}.mp4")
                    
                clip.save(save_path)
                clip.close()
            
        except Exception as e:
            self.logger.error(f"Error processing video {filepath}: {str(e)}")
            raise e
            
    def is_video(self, file_path: str) -> bool:
        """
        Check if a file is a valid video.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file is a valid video, False otherwise
        """
        try:
            clip = VideoProcessorFactory.create_video_clip(file_path)
            valid = clip.duration > 0
            clip.close()
            return valid
        except Exception:
            return False