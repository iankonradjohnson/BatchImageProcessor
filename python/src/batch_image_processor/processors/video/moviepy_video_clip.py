"""
Implementation of VideoClip interface using MoviePy.
MoviePy is a Python library for video editing: cutting, concatenations, title insertions,
video compositing, video processing, and creation.
"""

import os
import subprocess
from typing import Optional, List, Dict, Any, Tuple
import moviepy
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip

from batch_image_processor.processors.video.video_clip import VideoClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Rotate import Rotate


class MoviePyVideoClip(VideoClip):
    """Implementation of VideoClip interface using MoviePy."""

    def __init__(self, file_path: str):
        """
        Initialize the VideoClip with the path to a video file.

        Args:
            file_path: The path to the video file
        """
        self.file_path = file_path
        self._clip = VideoFileClip(file_path)
        self._rotation = None  # Store rotation metadata
        self._metadata = {}    # Additional metadata
        
        # Try to extract rotation from source metadata if available
        if hasattr(self._clip, 'rotation') and self._clip.rotation is not None:
            self._rotation = self._clip.rotation
            
        # Try to detect rotation from ffmpeg metadata (displaymatrix)
        if hasattr(self._clip, 'reader') and hasattr(self._clip.reader, 'infos'):
            for stream in self._clip.reader.infos.get('inputs', [{}])[0].get('streams', []):
                if stream.get('stream_type') == 'video' and 'metadata' in stream:
                    metadata = stream['metadata']
                    # Look for rotation information in displaymatrix
                    if 'displaymatrix' in metadata:
                        display_matrix = metadata['displaymatrix']
                        if 'rotation of 90.00 degrees' in display_matrix:
                            self._rotation = 90
                        elif 'rotation of 270.00 degrees' in display_matrix:
                            self._rotation = 270
                        elif 'rotation of 180.00 degrees' in display_matrix:
                            self._rotation = 180
                        print(f"Detected rotation from metadata: {self._rotation} degrees")

    def rotate(self, angle: int) -> 'VideoClip':
        """
        Rotate the video by the specified angle.
        
        Args:
            angle: Rotation angle in degrees
            
        Returns:
            The rotated video clip (self)
        """
        # Apply the rotation effect correctly
        self._clip = Rotate(angle, unit='deg').apply(self._clip)
        
        # Update rotation metadata - add new angle to existing rotation
        current_rotation = self._rotation or 0
        self._rotation = (current_rotation + angle) % 360
        
        print(f"Rotated by {angle} degrees, new rotation metadata: {self._rotation}")
        return self
        
    def resize(self, width: Optional[int] = None, height: Optional[int] = None) -> 'VideoClip':
        """
        Resize the video to the specified dimensions.

        Args:
            width: The new width of the video
            height: The new height of the video
            
        Returns:
            The resized video clip (self)
        """
        # Import and use the Resize FX class
        # In MoviePy 2.1.1, we need to use the Effect class pattern
        from moviepy.video.fx.Resize import Resize
        
        # Determine the new size - either (width, height) or just width/height
        new_size = None
        if width is not None and height is not None:
            new_size = (width, height)
        elif width is not None:
            new_size = width
        elif height is not None:
            new_size = height
            
        # Apply the resize effect
        self._clip = Resize(new_size=new_size).apply(self._clip)
        return self

    def save(self, output_path: str) -> None:
        """
        Save the video to the specified path.

        Args:
            output_path: The path to save the video to
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        w, h = self._clip.size
        print(f"Saving: current size = ({w}, {h}), orientation = {self.orientation}, rotation = {self._rotation}")

        # If MoviePy shows it as landscape, but our metadata says it's portrait, fix dimensions
        if self.orientation == "portrait" and w > h:
            print("Fixing: clip is portrait, but dimensions are landscape. Swapping dimensions.")
            self._clip = Resize(new_size=(h, w)).apply(self._clip)
            print(f"After dimension swap: size = {self._clip.size}")

        # Save the video
        print(f"Writing video to {output_path} with size {self._clip.size}")
        self._clip.write_videofile(output_path)

    def close(self) -> None:
        """Close the video clip and release resources."""
        if hasattr(self, '_clip') and self._clip is not None:
            self._clip.close()
            self._clip = None
        
    @property
    def width(self) -> int:
        """Get the width of the video."""
        return int(self._clip.w)
    
    @property
    def height(self) -> int:
        """Get the height of the video."""
        return int(self._clip.h)
    
    @property
    def fps(self) -> float:
        """Get the frames per second of the video."""
        return self._clip.fps
    
    @property
    def duration(self) -> float:
        """Get the duration of the video in seconds."""
        return self._clip.duration
        
    @property
    def rotation(self) -> Optional[int]:
        """Get the rotation angle from metadata, if available."""
        return self._rotation

    @property
    def orientation(self) -> str:
        if self._rotation in (90, 270, -90):
            return "portrait"
        elif self._clip.h > self._clip.w:
            return "portrait"
        else:
            return "landscape"
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get additional metadata about the video clip."""
        if not self._metadata and hasattr(self._clip, 'reader') and hasattr(self._clip.reader, 'infos'):
            # Extract available metadata from the reader
            self._metadata = dict(self._clip.reader.infos)
        return self._metadata
    
    @classmethod
    def load(cls, file_path: str) -> 'VideoClip':
        """
        Load a video from a file.
        
        Args:
            file_path: Path to the video file
            
        Returns:
            A new video clip object
        """
        return cls(file_path)
    
    @staticmethod
    def concatenate(clips: List["MoviePyVideoClip"], output_path: str) -> None:
        """
        Concatenate multiple video clips and save to a file.

        Args:
            clips: List of MoviePyVideoClip objects to concatenate
            output_path: Path to save the concatenated video
        """
        moviepy_clips = [clip._clip for clip in clips]
        
        # Use concatenate_videoclips
        final_clip = concatenate_videoclips(moviepy_clips)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write with optimal settings
        final_clip.write_videofile(output_path)
        final_clip.close()