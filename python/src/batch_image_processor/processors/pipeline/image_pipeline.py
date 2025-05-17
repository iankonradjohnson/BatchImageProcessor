import os.path
from typing import List, TypeVar, Generic, Protocol, runtime_checkable, Optional

import PIL
from PIL import Image, UnidentifiedImageError

from batch_image_processor.processors.media_processor import MediaProcessor

Image.MAX_IMAGE_PIXELS = None

T = TypeVar('T')  # Generic type for the media being processed


@runtime_checkable
class MediaPipeline(Protocol[T]):
    """
    A protocol for media processing pipelines.
    
    This interface defines the methods required for media processing pipelines.
    Implementations handle the workflow of loading media, applying a series of
    processors, and saving the result. It is parameterized by the media type.
    """
    
    def __init__(
        self, processors: List[MediaProcessor[T]], input_dir: str, output_dir: str, deleted_dir: str = None
    ):
        """
        Initialize the media pipeline.
        
        Args:
            processors: List of media processors to apply
            input_dir: Directory containing input files
            output_dir: Directory to save processed files
            deleted_dir: Directory to save filtered files (optional)
        """
        self.processors = processors
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.deleted_dir = deleted_dir
        
    def process_and_save(self, filepath: str) -> None:
        """
        Process a media file and save the result.
        
        This method should be implemented to handle specific media types.
        
        Args:
            filepath: Path to the media file relative to input_dir
        """
        ...


class ImagePipeline(MediaPipeline[Image.Image]):
    """
    A pipeline for processing image files using PIL.
    
    This class implements the MediaPipeline protocol for PIL Image objects.
    """
    
    def __init__(self, processors: List[MediaProcessor[Image.Image]], input_dir: str,
                 output_dir: str, deleted_dir: Optional[str] = None):
        """
        Initialize the image pipeline.
        
        Args:
            processors: List of image processors to apply
            input_dir: Directory containing input images
            output_dir: Directory to save processed images
            deleted_dir: Directory to save filtered images (optional)
        """
        super().__init__(processors, input_dir, output_dir, deleted_dir)

    def process_and_save(self, filepath: str) -> None:
        """
        Process an image file and save the result.
        
        Args:
            filepath: Path to the image file relative to input_dir
        """
        try:
            split = os.path.basename(filepath).split(".")
            basename, ext = ".".join(split[:-1]), split[-1]
            image_path = os.path.join(self.input_dir, filepath)
            save_path = os.path.join(self.output_dir, f"{basename}.png")

            with Image.open(image_path) as img:
                if not self.is_image(image_path):
                    return
                for processor in self.processors:
                    original_img = img
                    img = processor.process(img)

                    # If image is none, this is a result of a filter and image should not be saved
                    if img is None:
                        if self.deleted_dir:  # Check if deleted_dir is not None
                            if not os.path.exists(self.deleted_dir):
                                os.mkdir(self.deleted_dir)

                            filename = os.path.basename(filepath)
                            original_img.save(os.path.join(self.deleted_dir, filename))
                        return

                if not os.path.exists(self.output_dir):
                    os.mkdir(self.output_dir)

                img.save(save_path)

        except UnidentifiedImageError as error:
            print(error)

    def is_image(self, file_path: str) -> bool:
        """
        Check if a file is a valid image.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file is a valid image, False otherwise
        """
        try:
            with Image.open(file_path) as img:
                # Attempt to load the image to ensure it's valid
                img.verify()
            return True
        except (IOError, FileNotFoundError, Exception):
            # If an error occurs, it's likely not an image file that PIL can recognize
            return False
