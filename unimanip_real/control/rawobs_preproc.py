from ..utils.image_resize_utils import resize_image
import numpy as np
from PIL import Image

def resize_images(
    images: np.ndarray | list[np.ndarray] | list[Image.Image],
):
    """Resize images to the desired size.

    Args:
        images: Input images, can be in one of the following formats:
            - np.ndarray of shape (H, W, C) -> single image
            - np.ndarray of shape (N, H, W, C) -> batch of images
    """
    target_size = (520, 520)
    resized_images = []
    for image in images:
        resized_image = resize_image(
            image,
            resize=target_size,
            mode="center_crop",
            normalize=False,
        )
        resized_images.append(resized_image)

    return resized_images

def convert_images_to_pil(
    images: np.ndarray | list[np.ndarray] | list[Image.Image],
):
    """Convert images to PIL format.

    Args:
        images: Input images, can be in one of the following formats:
            - np.ndarray of shape (H, W, C) -> single image
            - np.ndarray of shape (N, H, W, C) -> batch of images
    """
    pil_images = []
    for image in images:
        if isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
        pil_images.append(pil_image)

    return pil_images
