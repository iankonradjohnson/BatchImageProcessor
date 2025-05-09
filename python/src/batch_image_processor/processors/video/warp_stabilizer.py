"""
Video processor for stabilizing shaky videos.

This module provides a warp stabilizer that uses FFmpeg's vidstab filter to smooth out
camera movements through motion estimation and compensating transformations.
"""

import logging
import os
import subprocess
import tempfile
from typing import Union, List, Dict, Any, Optional, Tuple

from batch_image_processor.processors.video.video_processor import VideoProcessor
from batch_image_processor.processors.video.video_clip import VideoClipInterface

logger = logging.getLogger(__name__)

class WarpStabilizer(VideoProcessor):
    def __init__(
        self,
        shakiness: int = 5,
        smoothing: int = 10,
        zoom: int = 0,
        optzoom: int = 1,
        sharpen: float = 0.8,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.shakiness = shakiness
        self.smoothing = smoothing
        self.zoom = zoom
        self.optzoom = optzoom
        self.sharpen = sharpen
        
    def process(self, clip: VideoClipInterface) -> Union[VideoClipInterface, List[VideoClipInterface], None]:
        logger.info("Starting video stabilization with FFmpeg...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.mp4")
            clip.save(input_path)
            
            output_path = os.path.join(temp_dir, "stabilized.mp4")
            transform_path = os.path.join(temp_dir, "transforms.trf")
            
            self._stabilize_video(input_path, output_path, transform_path)
            
            # Use the VideoClipInterface.load method to load the stabilized clip
            return type(clip).load(output_path)
            
    def _stabilize_video(self, input_path: str, output_path: str, transform_path: str) -> None:
        analyze_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"vidstabdetect=shakiness={self.shakiness}:accuracy=15:result={transform_path}",
            "-f", "null", "-"
        ]
        
        logger.info("Analyzing video motion...")
        try:
            subprocess.run(
                analyze_cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg analysis failed: {e.stderr.decode()}")
            raise RuntimeError("Video stabilization analysis failed") from e
            
        filter_string = (
            f"vidstabtransform=input={transform_path}:zoom={self.zoom}:"
            f"smoothing={self.smoothing}:optzoom={self.optzoom},"
            f"unsharp=5:5:{self.sharpen}"
        )
        
        stabilize_cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", filter_string,
            "-c:v", "libx264",
            "-preset", "slow", 
            "-tune", "film",
            "-c:a", "copy", 
            "-y", 
            output_path
        ]
        
        logger.info("Applying stabilization...")
        try:
            subprocess.run(
                stabilize_cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg stabilization failed: {e.stderr.decode()}")
            raise RuntimeError("Video stabilization failed") from e
            
        logger.info("Video stabilization complete")
