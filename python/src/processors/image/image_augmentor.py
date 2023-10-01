from PIL import Image
import numpy as np
import albumentations as A

from python.src.processors.image.image_processor import ImageProcessor


class ImageAugmentor(ImageProcessor):

    def __init__(self, config):
        pass

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Augment the input image.

        Args:
        - img (Image): The input image to be augmented.

        Returns:
        Image: The augmented image.
        """

        transforms = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=10, p=0.5),  # slight rotation
            A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=0.5),
            A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=0, p=0.5),  # slight shift and zoom
            A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.25),  # mild elastic transformations
            A.GridDistortion(p=0.5),  # distorts image locally using grid
            A.OpticalDistortion(p=0.5, distort_limit=0.05, shift_limit=0.1)  # mild optical distortion
        ])

        img_np = np.array(img)
        augmented = transforms(image=img_np)
        img_aug = Image.fromarray(augmented['image'])

        return img_aug
