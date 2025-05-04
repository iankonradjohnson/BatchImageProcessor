from abc import ABC, abstractmethod
from typing import Optional, Any, Union, List
import numpy as np


class VideoClip(ABC):
    @property
    @abstractmethod
    def width(self) -> int:
        pass
    
    @property
    @abstractmethod
    def height(self) -> int:
        pass
    
    @property
    @abstractmethod
    def duration(self) -> float:
        pass
    
    @property
    @abstractmethod
    def fps(self) -> float:
        pass
    
    @property
    @abstractmethod
    def rotation(self) -> Optional[int]:
        pass

    @property
    def orientation(self) -> str:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
    
    @abstractmethod
    def rotate(self, angle: int) -> 'VideoClip':
        pass
    
    @abstractmethod
    def save(self, output_path: str) -> None:
        pass
    
    @abstractmethod
    def get_frame(self, t: float) -> Union[np.ndarray, Any]:
        pass
    
    @abstractmethod
    def subclip(self, start_time: float, end_time: float) -> 'VideoClip':
        pass
    
    @classmethod
    @abstractmethod
    def load(cls, file_path: str) -> 'VideoClip':
        pass