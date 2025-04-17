from processors.image.image_processor import ImageProcessor
from PIL import Image, ImageOps, ImageEnhance


from PIL import Image, ImageOps

class DitherGreyscale(ImageProcessor):
    def __init__(self, config):
        """
        Initializes the dithering processor with a config dictionary.

        Config options:
        - "dither_type": str, one of ["floyd-steinberg", "ordered", "none"]
        """
        self.dither_type = config.get("dither_type", "floyd-steinberg").lower()

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Converts an image to greyscale and applies dithering based on the selected type.

        Args:
        - img (Image): The input PIL image.
        - is_left (bool, optional): Unused, but kept for API consistency.

        Returns:
        - Image: Processed image with dithering applied.
        """
        img = img.convert("L")  # Convert to greyscale

        if self.dither_type == "floyd-steinberg":
            # Floyd-Steinberg dithering (Pillow's default mode)
            return img.convert("1", dither=Image.FLOYDSTEINBERG)

        elif self.dither_type == "ordered":
            # Ordered dithering (Pattern-based, smoother than Floyd-Steinberg)
            return img.convert("1", dither=Image.ORDERED)

        elif self.dither_type == "none":
            # No dithering, just grayscale
            return img

        else:
            raise ValueError(f"Unsupported dither type: {self.dither_type}")



