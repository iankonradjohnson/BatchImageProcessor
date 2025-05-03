"""
Implementation of VideoClip interface using MoviePy.
MoviePy is a Python library for video editing: cutting, concatenations, title insertions,
video compositing, video processing, and creation.
"""

import os
from typing import Optional, List, Dict, Any
import moviepy
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip

from batch_image_processor.processors.video.video_clip import VideoClip
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
        # Import and use the Rotate FX class
        # Use the Rotate effect from moviepy
        from moviepy.video.fx.Rotate import Rotate
        
        # Apply the rotation effect
        self._clip = Rotate(angle, unit='deg').apply(self._clip)
        
        # Update the rotation metadata
        if self._rotation is None:
            self._rotation = angle
        else:
            self._rotation = (self._rotation + angle) % 360
            
        return self
        
    def crop(self, x: int, y: int, width: int, height: int) -> 'VideoClip':
        """
        Crop the video to the specified region.

        Args:
            x: The x-coordinate of the top-left corner of the region
            y: The y-coordinate of the top-left corner of the region
            width: The width of the region
            height: The height of the region
            
        Returns:
            The cropped video clip (self)
        """
        # Import and use the Crop FX class
        # In MoviePy 2.1.1, we need to use the Effect class pattern
        from moviepy.video.fx.Crop import Crop
        
        # Apply the crop effect
        self._clip = Crop(x1=x, y1=y, x2=x+width, y2=y+height).apply(self._clip)
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
        
        # Print dimensions before saving
        original_width = self.width
        original_height = self.height
        print(f"Saving video with dimensions: width={original_width}, height={original_height}, size={self._clip.size}")
        
        # MoviePy automatically passes parameters to ffmpeg under the hood
        # Using resize with original dimensions ensures we maintain aspect ratio
        from moviepy.video.fx.Resize import Resize
        clip_to_save = Resize(new_size=(original_width, original_height)).apply(self._clip)
        
        # Save the video with proper codec settings
        clip_to_save.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            preset='medium',  # Balance between encoding speed and quality
        )
        
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
    
    def overlay(self, clip: "MoviePyVideoClip", x: int, y: int, 
                duration: Optional[float] = None) -> "MoviePyVideoClip":
        """
        Overlay another clip on top of this clip at the specified position.

        Args:
            clip: The clip to overlay
            x: X-coordinate of the overlay position
            y: Y-coordinate of the overlay position
            duration: Optional duration to limit the overlay
            
        Returns:
            A new composite clip
        """
        # Create a clip with the overlay positioned at (x,y)
        overlay_clip = clip._clip.set_position((x, y))
        
        # Limit the duration if specified
        if duration is not None:
            overlay_clip = overlay_clip.set_duration(min(duration, clip._clip.duration))
        
        # Create a composite clip with both clips
        composite = CompositeVideoClip([self._clip, overlay_clip])
        
        # Create a new MoviePyVideoClip from the composite
        result = MoviePyVideoClip.__new__(MoviePyVideoClip)
        result.file_path = self.file_path  # Use the same file path
        result._clip = composite
        result._rotation = self._rotation
        result._metadata = self._metadata.copy()
        
        return result