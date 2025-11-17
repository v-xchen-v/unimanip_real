"""
image_resize_utils.py
---------------------

Flexible image resizing utility for ACT / VLA / robot vision.

Features
--------
- Accepts:
    * Single np.ndarray (H, W, C)
    * Single PIL.Image.Image
    * Batch np.ndarray (N, H, W, C)
    * List[np.ndarray]
    * List[PIL.Image.Image]
- Returns the same "container type" as input:
    * np.ndarray -> np.ndarray
    * PIL.Image.Image -> PIL.Image.Image
    * list[...] -> list[...]

Resize modes
------------
- "direct":       simple direct resize (may distort aspect ratio)
- "center_crop":  keep aspect ratio, resize shorter side, then center crop
- "pad_square":   pad to square (no FOV loss), then resize

Usage
-----
    from image_resize_utils import resize_image, resize_batch

    img_resized = resize_image(img, resize=(224, 224), mode="center_crop")
    batch_resized = resize_batch(batch_imgs, resize=(128, 128), mode="pad_square")
"""

from typing import Tuple, Union, List

import numpy as np
import cv2
from PIL import Image


# =========================
# ---- Helper functions ----
# =========================

def _is_pil_image(x) -> bool:
    return isinstance(x, Image.Image)


def _pil_to_np(img: Image.Image) -> np.ndarray:
    """Convert PIL.Image to RGB NumPy array (H, W, 3), uint8."""
    return np.array(img.convert("RGB"))


def _np_to_pil(img: np.ndarray) -> Image.Image:
    """Convert NumPy array (H, W, 3) to PIL.Image."""
    img_uint8 = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img_uint8)


def _pad_to_square(img: np.ndarray) -> np.ndarray:
    """Pad image to a square with black pixels."""
    h, w = img.shape[:2]
    if h == w:
        return img

    diff = abs(h - w)
    if h < w:
        pad_top = diff // 2
        pad_bottom = diff - pad_top
        pad_left = pad_right = 0
    else:
        pad_left = diff // 2
        pad_right = diff - pad_left
        pad_top = pad_bottom = 0

    return cv2.copyMakeBorder(
        img,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0),
    )


def _center_crop(img: np.ndarray, crop_size: Tuple[int, int]) -> np.ndarray:
    """Center crop image to (crop_h, crop_w)."""
    h, w = img.shape[:2]
    ch, cw = crop_size
    start_h = max(0, (h - ch) // 4)
    start_w = max(0, (w - cw) // 2)
    return img[start_h:start_h + ch, start_w:start_w + cw]


def _resize_np_image(
    img: np.ndarray,
    resize: Tuple[int, int],
    mode: str,
    resize_shorter: int,
    normalize: bool,
) -> np.ndarray:
    """
    Core resizing for a single NumPy image (H, W, C).
    """
    assert img.ndim == 3, f"Expected 3D image (H, W, C), got {img.shape}"

    h, w = img.shape[:2]

    # Ensure 3 channels (drop alpha if RGBA)
    if img.shape[2] == 4:
        img = img[:, :, :3]

    # --- Apply mode ---
    if mode == "direct":
        img_resized = cv2.resize(
            img, (resize[1], resize[0]), interpolation=cv2.INTER_AREA
        )

    elif mode == "center_crop":
        # Maintain aspect ratio: scale shorter side to resize_shorter
        if h < w:
            new_h = resize_shorter
            new_w = int(w * (resize_shorter / h))
        else:
            new_w = resize_shorter
            new_h = int(h * (resize_shorter / w))
        img_scaled = cv2.resize(
            img, (new_w, new_h), interpolation=cv2.INTER_AREA
        )
        img_resized = _center_crop(img_scaled, resize)

    elif mode == "pad_square":
        img_square = _pad_to_square(img)
        img_resized = cv2.resize(
            img_square, (resize[1], resize[0]), interpolation=cv2.INTER_AREA
        )

    else:
        raise ValueError(
            f"Unknown mode '{mode}'. Must be one of ['direct', 'center_crop', 'pad_square']."
        )

    # Normalize (optional)
    if normalize:
        img_resized = img_resized.astype(np.float32) / 255.0
        img_resized = (img_resized - 0.5) / 0.5  # [-1, 1]
    elif img_resized.dtype != np.uint8:
        img_resized = np.clip(img_resized, 0, 255).astype(np.uint8)

    return img_resized


# =========================
# ---- Public functions ----
# =========================

def resize_image(
    img: Union[np.ndarray, Image.Image],
    resize: Tuple[int, int] = (224, 224),
    mode: str = "center_crop",
    resize_shorter: int = None,
    normalize: bool = False,
) -> Union[np.ndarray, Image.Image]:
    """
    Resize a single image (NumPy or PIL).

    Args:
        img: np.ndarray (H, W, C) or PIL.Image
        resize: final size (H, W)
        mode: "direct", "center_crop", or "pad_square"
        resize_shorter: used for "center_crop" (default=resize[0] + 32)
        normalize: if True, output is float32 in [-1, 1];
                   if False, dtype is uint8.

    Returns:
        Same type as input (np.ndarray or PIL.Image).
    """
    if resize_shorter is None:
        resize_shorter = resize[0] + 32

    input_is_pil = _is_pil_image(img)
    if input_is_pil:
        img_np = _pil_to_np(img)
    else:
        img_np = img
        assert isinstance(img_np, np.ndarray), \
            f"Expected np.ndarray or PIL.Image, got {type(img)}"
        if img_np.ndim == 4:
            # User passed a batch to resize_image; forward to resize_batch
            return resize_batch(
                img_np,
                resize=resize,
                mode=mode,
                resize_shorter=resize_shorter,
                normalize=normalize,
            )

    img_resized = _resize_np_image(
        img_np, resize=resize, mode=mode,
        resize_shorter=resize_shorter, normalize=normalize
    )

    if input_is_pil:
        return _np_to_pil(img_resized)
    return img_resized


def resize_batch(
    imgs: Union[np.ndarray, List[np.ndarray], List[Image.Image]],
    resize: Tuple[int, int] = (224, 224),
    mode: str = "center_crop",
    resize_shorter: int = None,
    normalize: bool = False,
) -> Union[np.ndarray, List[np.ndarray], List[Image.Image]]:
    """
    Resize a batch of images.

    Args:
        imgs:
            - np.ndarray of shape (N, H, W, C)
            - list of np.ndarray with shape (H, W, C)
            - list of PIL.Image.Image
        resize: final size (H, W)
        mode: "direct", "center_crop", or "pad_square"
        resize_shorter: used for "center_crop" (default=resize[0] + 32)
        normalize: if True, output is float32 in [-1, 1].

    Returns:
        - If input is np.ndarray (N, H, W, C) -> np.ndarray (N, h, w, c)
        - If input is list[np.ndarray] -> list[np.ndarray]
        - If input is list[PIL.Image] -> list[PIL.Image]
    """
    if resize_shorter is None:
        resize_shorter = resize[0] + 32

    # Case 1: batch as a 4D NumPy array
    if isinstance(imgs, np.ndarray):
        if imgs.ndim == 3:
            # Single image, just call resize_image
            return resize_image(
                imgs,
                resize=resize,
                mode=mode,
                resize_shorter=resize_shorter,
                normalize=normalize,
            )
        assert imgs.ndim == 4, f"Expected (N, H, W, C), got {imgs.shape}"
        resized_list = [
            _resize_np_image(
                imgs[i], resize=resize, mode=mode,
                resize_shorter=resize_shorter, normalize=normalize
            )
            for i in range(imgs.shape[0])
        ]
        return np.stack(resized_list, axis=0)

    # Case 2: list of images
    assert isinstance(imgs, list) and len(imgs) > 0, \
        "Expected a non-empty list or a NumPy array for 'imgs'."

    first = imgs[0]

    # 2a: list of PIL.Image
    if _is_pil_image(first):
        out: List[Image.Image] = []
        for im in imgs:
            assert _is_pil_image(im), "Mixed types in list are not supported."
            im_np = _pil_to_np(im)
            im_resized = _resize_np_image(
                im_np, resize=resize, mode=mode,
                resize_shorter=resize_shorter, normalize=normalize
            )
            out.append(_np_to_pil(im_resized))
        return out

    # 2b: list of np.ndarray
    elif isinstance(first, np.ndarray):
        out_np: List[np.ndarray] = []
        for im in imgs:
            assert isinstance(im, np.ndarray), "Mixed types in list are not supported."
            out_np.append(
                _resize_np_image(
                    im, resize=resize, mode=mode,
                    resize_shorter=resize_shorter, normalize=normalize
                )
            )
        return out_np

    else:
        raise TypeError(
            f"Unsupported batch element type: {type(first)}. "
            f"Expected np.ndarray or PIL.Image.Image."
        )
