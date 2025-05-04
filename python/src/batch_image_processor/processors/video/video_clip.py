from abc import ABC, abstractmethod
from typing import Optional


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
    def orientation(self) -> str:
        pass
    
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