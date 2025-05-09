import os
import subprocess
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import moviepy
from moviepy import VideoFileClip, concatenate_videoclips, CompositeVideoClip

from batch_image_processor.processors.video.video_clip import VideoClipInterface
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Rotate import Rotate
from moviepy.video.VideoClip import VideoClip


class MoviePyVideoClipInterface(VideoClipInterface):

    def __init__(self,
                 file_path: Optional[str] = None,
                 clip: Optional[VideoClip] = None):

        self._clip: VideoClip

        if file_path:
            self.file_path = file_path
            self._clip = VideoFileClip(file_path)
        elif clip:
            self._clip = clip

        self._rotation = None
        self._metadata = {}

        if hasattr(self._clip, 'rotation') and self._clip.rotation is not None:
            self._rotation = self._clip.rotation

        if hasattr(self._clip, 'reader') and hasattr(self._clip.reader, 'infos'):
            for stream in self._clip.reader.infos.get('inputs', [{}])[0].get('streams', []):
                if stream.get('stream_type') == 'video' and 'metadata' in stream:
                    metadata = stream['metadata']
                    if 'displaymatrix' in metadata:
                        display_matrix = metadata['displaymatrix']
                        if 'rotation of 90.00 degrees' in display_matrix:
                            self._rotation = 90
                        elif 'rotation of 270.00 degrees' in display_matrix:
                            self._rotation = 270
                        elif 'rotation of 180.00 degrees' in display_matrix:
                            self._rotation = 180
                        print(f"Detected rotation from metadata: {self._rotation} degrees")

        self._clip = self._clip.without_audio()

    def rotate(self, angle: int) -> VideoClipInterface:
        self._clip = Rotate(angle, unit='deg').apply(self._clip)

        current_rotation = self._rotation or 0
        self._rotation = (current_rotation + angle) % 360

        print(f"Rotated by {angle} degrees, new rotation metadata: {self._rotation}")
        return self

    def resize(self, width: Optional[int] = None, height: Optional[int] = None) -> VideoClipInterface:

        from moviepy.video.fx.Resize import Resize

        new_size = None
        if width is not None and height is not None:
            new_size = (width, height)
        elif width is not None:
            new_size = width
        elif height is not None:
            new_size = height

        self._clip = Resize(new_size=new_size).apply(self._clip)
        return self

    def save(self, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        w, h = self._clip.size
        print(
            f"Saving: current size = ({w}, {h}), orientation = {self.orientation}, rotation = {self._rotation}")

        if self.orientation == "portrait" and w > h:
            print("Fixing: clip is portrait, but dimensions are landscape. Swapping dimensions.")
            self._clip = Resize(new_size=(h, w)).apply(self._clip)
            print(f"After dimension swap: size = {self._clip.size}")

        print(f"Writing video to {output_path} with size {self._clip.size}")
        self._clip.write_videofile(output_path)

    def close(self) -> None:
        if hasattr(self, '_clip') and self._clip is not None:
            self._clip.close()
            self._clip = None

    @property
    def width(self) -> int:
        return int(self._clip.w)

    @property
    def height(self) -> int:
        return int(self._clip.h)

    @property
    def fps(self) -> float:
        return self._clip.fps

    @property
    def duration(self) -> float:
        return self._clip.duration

    @property
    def rotation(self) -> Optional[int]:
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
        if not self._metadata and hasattr(self._clip, 'reader') and hasattr(self._clip.reader,
                                                                            'infos'):
            self._metadata = dict(self._clip.reader.infos)
        return self._metadata

    def get_frame(self, t: float) -> np.ndarray:
        # Get the original frame
        frame = self._clip.get_frame(t)
        
        # Simple fix for portrait videos - just swap height and width
        if self.orientation == "portrait" and frame.shape[1] > frame.shape[0]:
            # Import here to avoid circular imports
            from PIL import Image
            
            # Convert to PIL, resize to swapped dimensions, and convert back
            img = Image.fromarray(frame.astype('uint8'), 'RGB')
            # Just swap height and width (h,w instead of w,h)
            h, w = frame.shape[0], frame.shape[1]
            img = img.resize((h, w))
            frame = np.array(img)
            
        return frame

    @classmethod
    def load(cls, file_path: str) -> VideoClipInterface:
        return cls(file_path=file_path)

    @staticmethod
    def concatenate(clips: List["MoviePyVideoClipInterface"], output_path: str) -> None:
        moviepy_clips = [clip._clip for clip in clips]
        final_clip = concatenate_videoclips(moviepy_clips)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_clip.write_videofile(output_path)
        final_clip.close()

    def subclipped(self, start_time: float, end_time: float) -> VideoClipInterface:
        return MoviePyVideoClipInterface(
            clip=self._clip.subclipped(start_time, end_time)
        )