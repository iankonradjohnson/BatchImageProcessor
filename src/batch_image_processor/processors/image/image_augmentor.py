from PIL import Image
import numpy as np
import albumentations as A

from batch_image_processor.processors.image.image_processor import ImageProcessor

class ImageAugmentor(ImageProcessor):

    def __init__(self, config):
        self.config = config

    def process(self, img: Image, is_left: bool = None) -> Image:
        """
        Augment the input image.

        Args:
        - img (Image): The input image to be augmented.

        Returns:
        Image: The augmented image.
        """

        transform_mappings = {
            'horizontal_flip': A.HorizontalFlip,
            'rotation': A.Rotate,
            'brightness_contrast': A.RandomBrightnessContrast,
            'shift_scale_rotate': A.ShiftScaleRotate,
            'elastic_transform': A.ElasticTransform,
            'grid_distortion': A.GridDistortion,
            'optical_distortion': A.OpticalDistortion
        }

        transforms_list = []

        for key, transform in transform_mappings.items():
            if key in self.config:
                args = {param: value for param, value in self.config[key].items()}
                transforms_list.append(transform(**args))

        transforms = A.Compose(transforms_list)

        img_np = np.array(img)
        augmented = transforms(image=img_np)
        img_aug = Image.fromarray(augmented['image'])

        return img_aug
