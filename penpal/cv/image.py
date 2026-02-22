"""Image loading and preprocessing for the CV pipeline.

All images are numpy float64 arrays with values in [0, 255].
Grayscale = (H, W), color = (H, W, 3) RGB.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from penpal.core.paths import Paths


def load(path: str, grayscale: bool = True) -> np.ndarray:
    """Load an image as a numpy array.

    Parameters
    ----------
    path : str
        Image file path.
    grayscale : bool
        If True, convert to (H, W) grayscale.
        If False, return (H, W, 3) RGB.

    Returns
    -------
    np.ndarray, float64, values in [0, 255].
    """
    img = Image.open(path)
    if grayscale:
        img = img.convert('L')
    else:
        img = img.convert('RGB')
    return np.asarray(img, dtype=np.float64)


def gamma_correct(image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
    """Linear RGB → perceptual space (apply forward gamma)."""
    return 255.0 * (np.clip(image, 0, 255) / 255.0) ** (1.0 / gamma)


def inv_gamma_correct(image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
    """Perceptual space → linear RGB (apply inverse gamma)."""
    return 255.0 * (np.clip(image, 0, 255) / 255.0) ** gamma


def smooth(image: np.ndarray, sigma: float = 2.0) -> np.ndarray:
    """Gamma-aware Gaussian blur.

    Converts to perceptual space, blurs, converts back.
    This produces better results than blurring in linear space.
    """
    if sigma <= 0:
        return image.copy()
    perceptual = gamma_correct(image)
    blurred = gaussian_filter(perceptual, sigma=sigma)
    return inv_gamma_correct(blurred)


def resize(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
    """Resize image, preserving aspect ratio if only one dimension given.

    Parameters
    ----------
    width, height : int, optional
        Target dimensions. If only one is given, the other is computed
        to preserve aspect ratio.
    """
    h, w = image.shape[:2]
    if width is None and height is None:
        return image.copy()
    if width is not None and height is not None:
        target = (width, height)
    elif width is not None:
        target = (width, int(h * width / w))
    else:
        target = (int(w * height / h), height)

    # Use PIL for quality resampling
    if image.ndim == 2:
        pil = Image.fromarray(image.astype(np.uint8), mode='L')
    else:
        pil = Image.fromarray(image.astype(np.uint8), mode='RGB')
    pil = pil.resize(target, Image.LANCZOS)
    return np.asarray(pil, dtype=np.float64)


def map_to_drawing(paths: Paths, image_shape: tuple,
                   drawing, margin: float = 0.5) -> Paths:
    """Map Paths from pixel coordinates to drawing coordinates.

    Scales and translates so the image fits within the drawing's
    drawable area (minus margins), preserving aspect ratio and centering.

    Parameters
    ----------
    paths : Paths
        Lines in pixel coordinates (origin top-left, units = pixels).
    image_shape : (H, W)
        Image dimensions.
    drawing : Drawing
        Target drawing (provides width, height, center, x_range, y_range).
    margin : float
        Margin on each side of the drawing.

    Returns
    -------
    Paths in drawing coordinates.
    """
    img_h, img_w = image_shape[:2]

    x0, x1 = drawing.x_range
    y0, y1 = drawing.y_range
    draw_w = (x1 - x0) - 2 * margin
    draw_h = (y1 - y0) - 2 * margin

    # Scale to fit, preserving aspect ratio
    scale = min(draw_w / img_w, draw_h / img_h)

    # Centering offset
    mapped_w = img_w * scale
    mapped_h = img_h * scale
    offset_x = x0 + margin + (draw_w - mapped_w) / 2
    offset_y = y0 + margin + (draw_h - mapped_h) / 2

    # Transform: pixel (px, py) → drawing (offset_x + px*scale, offset_y + py*scale)
    new_lines = []
    for line in paths.lines:
        mapped = np.empty_like(line)
        mapped[:, 0] = offset_x + line[:, 0] * scale
        mapped[:, 1] = offset_y + line[:, 1] * scale
        new_lines.append(mapped)

    return Paths(new_lines)
