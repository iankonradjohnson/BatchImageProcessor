"""
A module defining an interface for media processing.

This module introduces a `MediaProcessor` interface intended to be 
implemented by different types of media processing operations (images, video, audio, etc).
Implementations should provide the `process` method to handle 
the actual media processing logic.
"""

from typing import Generic, TypeVar, Dict, Any, Protocol, runtime_checkable, Union, List

T = TypeVar('T')  # Generic type for input/output media


@runtime_checkable
class MediaProcessor(Protocol[T]):
    """
    An interface for media processing operations.

    This interface should be implemented by classes intended for specific
    media types (image, video, audio, etc). Implementations should provide
    the `process` method to handle the specific media type.
    """

    def process(self, media: T) -> Union[T, List[T], None]:
        """
        Process the input media.

        This method must be implemented to provide specific media processing logic.

        Args:
            media: The input media to be processed.

        Returns:
            - A single processed media object
            - A list of processed media objects (for splitting operations)
            - None if the media should be filtered out
        """
        ...