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
from batch_image_processor.processors.video.video_clip import VideoClipInterface
from batch_image_processor.factory.video_processor_factory import VideoProcessorFactory


class VideoPipeline(MediaPipeline[VideoClipInterface]):

    def __init__(
        self, processors: List[MediaProcessor[VideoClipInterface]], input_dir: str, output_dir: str, deleted_dir: Optional[str] = None
    ):

        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.deleted_dir = deleted_dir
        self.logger = logging.getLogger(__name__)

    def process_and_save(self, filepath: str) -> None:

        try:
            split = os.path.basename(filepath).split(".")
            basename, ext = ".".join(split[:-1]), split[-1]
            video_path = os.path.join(self.input_dir, filepath)

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)

            if self.deleted_dir and not os.path.exists(self.deleted_dir):
                os.makedirs(self.deleted_dir, exist_ok=True)

            clip = VideoProcessorFactory.create_video_clip(video_path)

            clips = [clip]
            for processor in self.processors:
                new_clips = []
                for c in clips:
                    result = processor.process(c)

                    if result is None:
                        if self.deleted_dir:
                            deleted_path = os.path.join(self.deleted_dir, os.path.basename(filepath))
                            c.save(deleted_path)
                        c.close()
                        continue

                    if isinstance(result, list):
                        new_clips.extend(result)
                    else:
                        new_clips.append(result)

                    if c != result and c not in (result if isinstance(result, list) else [result]):
                        c.close()

                clips = new_clips

                if not clips:
                    return

            for i, clip in enumerate(clips):
                if len(clips) == 1:
                    save_path = os.path.join(self.output_dir, f"{basename}.mp4")
                else:
                    save_path = os.path.join(self.output_dir, f"{basename}_{i+1}.mp4")
                    
                clip.save(save_path)
                clip.close()
            
        except Exception as e:
            self.logger.error(f"Error processing video {filepath}: {str(e)}")
            raise e
            
    def is_video(self, file_path: str) -> bool:

        try:
            clip = VideoProcessorFactory.create_video_clip(file_path)
            valid = clip.duration > 0
            clip.close()
            return valid
        except Exception:
            return False