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


def normalize_depth(depth_uint16, depth_scale=0.001, max_depth=5.0):
    """
    Convert uint16 depth to 0–255 grayscale image.
    
    Args:
        depth_uint16 (np.ndarray): Depth image (uint16).
        depth_scale (float): Scale factor to convert raw depth to meters (e.g., 0.001 for RealSense).
        max_depth (float): Maximum depth in meters to clip at.
    Returns:
        np.ndarray: Normalized uint8 depth image (0–255).
    """
    # Convert to meters
    depth_m = depth_uint16.astype(np.float32) * depth_scale

    # Clip range (0, max_depth)
    depth_m = np.clip(depth_m, 0, max_depth)

    # Normalize to 0–255 (invert so near = bright if desired)
    depth_norm = (depth_m / max_depth) * 255.0
    depth_norm = depth_norm.astype(np.uint8)

    return depth_norm

def duplicate_depth_channel(depth_image):
    """
    Duplicate single-channel depth image to 3 channels.
    
    Args:
        depth_image (np.ndarray): Single-channel depth image (H, W).
    Returns:
        np.ndarray: 3-channel depth image (H, W, 3).
    """
    if len(depth_image.shape) == 2:
        depth_3ch = np.stack([depth_image]*3, axis=-1)
    elif len(depth_image.shape) == 3 and depth_image.shape[2] == 1:
        depth_3ch = np.concatenate([depth_image]*3, axis=-1)
    else:
        raise ValueError("Input depth_image must be single-channel.")
    return depth_3ch