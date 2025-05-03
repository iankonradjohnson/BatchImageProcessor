"""
Video clip interface and FFmpeg implementation.

This module defines a common interface for video clips and an implementation
using FFmpeg that properly handles video rotation metadata.
"""

import os
import json
import subprocess
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any


class VideoClip(ABC):
    """
    Abstract base class defining the interface for video clips.
    """
    
    @property
    @abstractmethod
    def width(self) -> int:
        """Get the width of the video."""
        pass
    
    @property
    @abstractmethod
    def height(self) -> int:
        """Get the height of the video."""
        pass
    
    @property
    @abstractmethod
    def duration(self) -> float:
        """Get the duration of the video in seconds."""
        pass
    
    @property
    @abstractmethod
    def fps(self) -> float:
        """Get the frames per second of the video."""
        pass
    
    @property
    @abstractmethod
    def rotation(self) -> Optional[int]:
        """Get the rotation angle from metadata, if available."""
        pass
    
    @property
    def is_horizontal(self) -> bool:
        """
        Check if the video is effectively in horizontal orientation.
        
        This considers both the raw dimensions and any rotation metadata.
        """
        # Basic orientation check
        is_horizontal = self.width > self.height
        
        # If rotation is 90 or 270 degrees, flip the orientation
        if self.rotation in [90, -90, 270, -270]:
            is_horizontal = not is_horizontal
            
        return is_horizontal
    
    @abstractmethod
    def close(self) -> None:
        """Close the video clip and release any resources."""
        pass
    
    @abstractmethod
    def rotate(self, angle: int) -> 'VideoClip':
        """
        Rotate the video by the specified angle.
        
        Args:
            angle: Rotation angle in degrees
            
        Returns:
            A new rotated video clip
        """
        pass
    
    @abstractmethod
    def save(self, output_path: str) -> None:
        """
        Save the video to the specified path.
        
        Args:
            output_path: Path to save the video to
        """
        pass
    
    @classmethod
    @abstractmethod
    def load(cls, file_path: str) -> 'VideoClip':
        """
        Load a video from a file.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            A new video clip object
        """
        pass


class FFmpegVideoClip(VideoClip):
    """
    Implementation of VideoClip using FFmpeg directly.
    
    This implementation uses FFmpeg for all operations and properly handles
    video rotation metadata.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize with a video file path.
        
        Args:
            file_path: Path to the video file
        """
        self.file_path = file_path
        self.temp_files = []
        
        # Get video info
        info = self._get_video_info(file_path)
        
        # Extract video properties
        video_stream = None
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
                
        if not video_stream:
            raise ValueError(f"No video stream found in {file_path}")
        
        self._width = int(video_stream.get('width', 0))
        self._height = int(video_stream.get('height', 0))
        
        # Extract rotation metadata
        self._rotation = None
        
        # Check for rotation in side_data
        if 'side_data_list' in video_stream:
            for side_data in video_stream['side_data_list']:
                if 'rotation' in side_data:
                    self._rotation = int(side_data['rotation'])
                    break
        
        # Check for rotation in tags
        if self._rotation is None and 'tags' in video_stream and 'rotate' in video_stream['tags']:
            self._rotation = int(video_stream['tags']['rotate'])
        
        # Extract duration and fps
        self._duration = float(info.get('format', {}).get('duration', 0))
        
        # Parse frame rate fraction (e.g., "30000/1001")
        frame_rate = video_stream.get('r_frame_rate', '0/0')
        if '/' in frame_rate:
            num, denom = map(int, frame_rate.split('/'))
            self._fps = num / denom if denom else 0
        else:
            self._fps = float(frame_rate)
    
    def _get_video_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed video information using ffprobe.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Dictionary with video information
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_streams',
            '-show_format',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def duration(self) -> float:
        return self._duration
    
    @property
    def fps(self) -> float:
        return self._fps
    
    @property
    def rotation(self) -> Optional[int]:
        return self._rotation
    
    def close(self) -> None:
        """Clean up any temporary files."""
        for file_path in self.temp_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        self.temp_files = []
    
    def rotate(self, angle: int) -> 'FFmpegVideoClip':
        """
        Rotate the video using FFmpeg.
        
        This sets the rotation metadata without re-encoding the video.
        
        Args:
            angle: Rotation angle in degrees
            
        Returns:
            A new rotated video clip
        """

        self.cl

        temp_file = tempfile.mktemp(suffix='.mp4')
        self.temp_files.append(temp_file)
        
        # Use FFmpeg to create a new video with the rotation metadata
        cmd = [
            'ffmpeg',
            '-i', self.file_path,
            '-metadata:s:v:0', f'rotate={angle}',
            '-c', 'copy',
            '-y',
            temp_file
        ]
        
        subprocess.run(cmd, check=True)
        return FFmpegVideoClip(temp_file)
    
    def save(self, output_path: str) -> None:
        """
        Save the video to the specified path.
        
        Args:
            output_path: Path to save the video to
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Use FFmpeg to copy the file
        cmd = [
            'ffmpeg',
            '-i', self.file_path,
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True)
    
    @classmethod
    def load(cls, file_path: str) -> 'FFmpegVideoClip':
        """
        Load a video from a file.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            A new FFmpegVideoClip object
        """
        return cls(file_path)