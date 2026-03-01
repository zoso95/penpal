"""Image-driven texture generation — gradient warped grids and tonal masking.

Port of plotterart/pieces/sourcery/image_magic.py and the death_textures /
Bradway portrait techniques. Takes photos and produces organic plotter-ready
line art by displacing regular grids along image gradient fields.

All generators return Paths in pixel coordinates. Use cv.image.map_to_drawing()
to fit into a Drawing.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
from scipy import ndimage

from penpal.core.paths import Paths
from penpal.cv.image import smooth


# ---------------------------------------------------------------------------
# Gradient field estimation (core of image_magic.py)
# ---------------------------------------------------------------------------

def fft_smooth(image: np.ndarray, sigma: float) -> np.ndarray:
    """Frequency-domain Gaussian smoothing via FFT.

    Smoother than spatial convolution — no ringing at edges.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    sigma : float
        FFT-domain smoothing width. Larger = smoother.

    Returns
    -------
    (H, W) smoothed image.
    """
    fft = np.fft.fftn(image)
    smoothed_fft = ndimage.fourier_gaussian(fft, sigma=sigma)
    return np.abs(np.fft.ifftn(smoothed_fft))


def estimate_gradient(
    image: np.ndarray,
    grad_smooth: float = 1.0,
    grad_speed: float = 7.0,
    scales: list[float] | None = None,
    weights: list[float] | None = None,
    postprocessing: str | None = "scale",
) -> np.ndarray:
    """Compute a multi-scale gradient field from an image.

    Estimates image gradients at multiple FFT smoothing scales, weights
    them (heavier on coarse scales for large-feature warping), then
    post-smoothes spatially.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    grad_smooth : float
        Spatial Gaussian smoothing of the final gradient field.
    grad_speed : float
        Overall gradient magnitude multiplier.
    scales : list of float, optional
        FFT smoothing scales. Default: [1, 2, 5, 10].
    weights : list of float, optional
        Per-scale weights. Default: [0.12, 0.08, 0.4, 1.5].
    postprocessing : str, optional
        'scale' (normalize max to 10), 'clip' (clip at -7),
        'norm' (0-1 normalize), or None.

    Returns
    -------
    (H, W, 2) gradient field [dy, dx].
    """
    if scales is None:
        scales = [1, 2, 5, 10]
    if weights is None:
        weights = [0.12, 0.08, 0.4, 1.5]

    d1 = np.zeros_like(image, dtype=float)
    d2 = np.zeros_like(image, dtype=float)

    for fft_s, w in zip(scales, weights):
        z = fft_smooth(image, fft_s)
        dx = ndimage.sobel(z, axis=0)
        dy = ndimage.sobel(z, axis=1)
        d1 += grad_speed * w * (2 / 255) * dx
        d2 += grad_speed * w * (2 / 255) * dy

    d1 = ndimage.gaussian_filter(d1, sigma=grad_smooth)
    d2 = ndimage.gaussian_filter(d2, sigma=grad_smooth)

    if postprocessing == "clip":
        d1 = np.clip(d1, -7, None)
        d2 = np.clip(d2, -7, None)
    elif postprocessing == "norm":
        d1 = (d1 - d1.min()) / (d1.max() - d1.min() + 1e-10)
        d2 = (d2 - d2.min()) / (d2.max() - d2.min() + 1e-10)
    elif postprocessing == "scale":
        max_val = max(np.abs(d1).max(), np.abs(d2).max(), 1e-10)
        scale_f = 10 / max_val
        d1 *= scale_f
        d2 *= scale_f

    return np.dstack([d1, d2])


# ---------------------------------------------------------------------------
# Mesh construction and evaluation
# ---------------------------------------------------------------------------

def make_mesh(
    shape: tuple[int, int],
    n_lines: int | tuple[int, int] = 500,
) -> np.ndarray:
    """Create a regular grid mesh over an image.

    Parameters
    ----------
    shape : (H, W)
        Image dimensions.
    n_lines : int or (n_rows, n_cols)
        Number of grid lines in each direction.

    Returns
    -------
    (n_rows, n_cols, 2) mesh of [row, col] coordinates.
    """
    if isinstance(n_lines, int):
        n_lines = (n_lines, n_lines)

    mx, my = np.meshgrid(
        np.linspace(0, shape[0] - 1, n_lines[0]),
        np.linspace(0, shape[1] - 1, n_lines[1]),
        indexing="ij",
    )
    return np.dstack([mx, my])


def warp_mesh(
    mesh: np.ndarray,
    gradient: np.ndarray,
    strength: float = 1.0,
) -> np.ndarray:
    """Displace mesh points along a gradient field.

    Samples the gradient at each mesh position and displaces by
    `strength * gradient(position)`.

    Parameters
    ----------
    mesh : (N, M, 2) mesh coordinates.
    gradient : (H, W, 2) gradient field.
    strength : float
        Displacement multiplier. Negative = toward dark regions.

    Returns
    -------
    (N, M, 2) warped mesh.
    """
    d1 = ndimage.map_coordinates(
        gradient[:, :, 0], [mesh[:, :, 0], mesh[:, :, 1]], order=1
    )
    d2 = ndimage.map_coordinates(
        gradient[:, :, 1], [mesh[:, :, 0], mesh[:, :, 1]], order=1
    )
    displacement = np.dstack([d1, d2])
    return mesh + strength * displacement


def mesh_to_paths(
    mesh: np.ndarray,
    horizontal: bool = True,
    vertical: bool = True,
    stride: int = 1,
) -> Paths:
    """Extract polylines from a mesh grid.

    Parameters
    ----------
    mesh : (N, M, 2) mesh coordinates.
    horizontal : bool
        Include horizontal scanlines (rows).
    vertical : bool
        Include vertical scanlines (columns).
    stride : int
        Draw every Nth line.

    Returns
    -------
    Paths in pixel coordinates [row, col].
    """
    lines = []

    if horizontal:
        for i in range(0, mesh.shape[0], stride):
            row = mesh[i, :, :]  # (M, 2)
            # Convert [row, col] -> [col, row] for x,y convention
            lines.append(np.column_stack([row[:, 1], row[:, 0]]))

    if vertical:
        for j in range(0, mesh.shape[1], stride):
            col = mesh[:, j, :]  # (N, 2)
            lines.append(np.column_stack([col[:, 1], col[:, 0]]))

    return Paths(lines)


# ---------------------------------------------------------------------------
# Death textures — gradient-displaced scanlines
# ---------------------------------------------------------------------------

def gradient_warp(
    image: np.ndarray,
    alpha: float = -5.0,
    gamma: float = 3.0,
    fft_sigma: float = 4.0,
    grad_smooth: float = 1.0,
    grad_weight: float = 1.0,
    h_stride: int = 1,
    v_stride: int = 1,
    density: float = 1.0,
    sigma: float = 0.0,
) -> Paths:
    """Displace a pixel grid along image gradients — the "death texture" technique.

    Every row and column of a regular pixel grid is independently displaced
    by the image's gradient field. Where gradients are strong (edges, texture),
    lines warp and bunch together. Where the image is flat, lines stay parallel.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    alpha : float
        Displacement strength. Negative = lines pulled toward dark regions.
        Typical range: -3 to -15.
    gamma : float
        Gamma correction before gradient computation. Higher = more extreme contrast.
    fft_sigma : float
        FFT smoothing scale for the gradient. Larger = broader, smoother warps.
    grad_smooth : float
        Spatial smoothing of the gradient field.
    grad_weight : float
        Gradient magnitude multiplier (applied after normalization).
    h_stride : int
        Horizontal line spacing. 1 = every pixel row, 2 = every other, 0 = skip.
    v_stride : int
        Vertical line spacing. 1 = every pixel column, 2 = every other, 0 = skip.
    density : float
        Line density multiplier. 1.0 = one line per stride pixels (default).
        2.0 = twice as many lines. Values > 1.0 interpolate between pixel rows.
        Combined with stride: total horizontal lines = image_height * density / h_stride.
    sigma : float
        Pre-blur the image before gradient computation.

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = image.copy()
    if sigma > 0:
        img = ndimage.gaussian_filter(img, sigma=sigma)

    # Gamma correction
    img_g = np.clip(img / 255, 0, 1) ** gamma * 255

    # FFT-smoothed gradient
    z = fft_smooth(img_g, fft_sigma)
    dx = ndimage.sobel(z, axis=0)
    dy = ndimage.sobel(z, axis=1)

    d1 = grad_weight * ndimage.gaussian_filter(dx / (255 / 2), sigma=grad_smooth)
    d2 = grad_weight * ndimage.gaussian_filter(dy / (255 / 2), sigma=grad_smooth)

    h, w = image.shape
    lines = []
    cols_f = np.arange(w, dtype=float)
    rows_f = np.arange(h, dtype=float)

    # Horizontal scanlines
    if h_stride > 0:
        n_h = max(1, int(h * density / h_stride))
        h_positions = np.linspace(0, h - 1, n_h)
        for r_pos in h_positions:
            r_arr = np.full(w, r_pos)
            d1_row = ndimage.map_coordinates(d1, [r_arr, cols_f], order=1)
            d2_row = ndimage.map_coordinates(d2, [r_arr, cols_f], order=1)
            s_r = r_arr + alpha * d1_row
            s_c = cols_f + alpha * d2_row
            lines.append(np.column_stack([s_c, s_r]))

    # Vertical scanlines
    if v_stride > 0:
        n_v = max(1, int(w * density / v_stride))
        v_positions = np.linspace(0, w - 1, n_v)
        for c_pos in v_positions:
            c_arr = np.full(h, c_pos)
            d1_col = ndimage.map_coordinates(d1, [rows_f, c_arr], order=1)
            d2_col = ndimage.map_coordinates(d2, [rows_f, c_arr], order=1)
            s_r = rows_f + alpha * d1_col
            s_c = c_arr + alpha * d2_col
            lines.append(np.column_stack([s_c, s_r]))

    return Paths(lines)


def gradient_warp_layered(
    image: np.ndarray,
    params: list[dict],
) -> list[Paths]:
    """Generate multiple gradient warp layers with different parameters.

    Each param dict is passed to gradient_warp(). Useful for multi-pen
    pieces with different warp intensities or line densities per layer.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    params : list of dict
        Each dict contains keyword args for gradient_warp().

    Returns
    -------
    list of Paths, one per parameter set.
    """
    return [gradient_warp(image, **p) for p in params]


# ---------------------------------------------------------------------------
# Bradway portrait — gradient mesh warp + fraction-based tonal masking
# ---------------------------------------------------------------------------

def portrait_warp(
    image: np.ndarray,
    n_lines: int | tuple[int, int] = 500,
    grad_smooth: float = 1.5,
    warp_strength: float = -1.0,
    detail_image: np.ndarray | None = None,
    detail_strength: float = 1.0,
    detail_smooth: float = 1.0,
    tonal_denom: int = 4,
    tonal_levels: int = 101,
    tonal_gamma: float = 0.7,
    horizontal: bool = True,
    vertical: bool = True,
    stride: int = 1,
    morph_clean: int = 0,
) -> Paths:
    """Image-to-lines via gradient mesh warp and tonal line masking.

    Two-pass technique: (1) warp a regular mesh toward dark regions using
    multi-scale gradient, (2) mask which lines/segments are drawn based
    on local brightness using fraction-quantized density.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_lines : int or (rows, cols)
        Grid resolution.
    grad_smooth : float
        Gradient field smoothness.
    warp_strength : float
        Mesh warp magnitude. Negative = pull toward dark.
    detail_image : (H, W), optional
        Second image for detail pass (e.g. concavity map).
        If None, uses minimum_filter - gaussian_filter of main image.
    detail_strength : float
        Detail pass warp strength.
    detail_smooth : float
        Detail gradient smoothness.
    tonal_denom : int
        Maximum fraction denominator for tonal masking.
        2 = binary (on/off), 4 = quarter-steps, etc.
    tonal_levels : int
        Number of tonal quantization levels.
    tonal_gamma : float
        Gamma on tonal curve. < 1 expands highlights, > 1 expands shadows.
    horizontal : bool
        Include horizontal lines.
    vertical : bool
        Include vertical lines.
    stride : int
        Draw every Nth mesh line.
    morph_clean : int
        Morphological erosion+dilation kernel size to clean up the mask.
        0 = no cleanup.

    Returns
    -------
    Paths in pixel coordinates.
    """
    h, w = image.shape
    if isinstance(n_lines, int):
        n_lines = (n_lines, n_lines)

    # Build mesh
    mesh = make_mesh(image.shape, n_lines)

    # Pass 1: main gradient warp
    grad = estimate_gradient(image, grad_smooth=grad_smooth, postprocessing="scale")
    mesh = warp_mesh(mesh, grad, strength=warp_strength)

    # Pass 2: detail warp
    if detail_image is None:
        detail_image = (
            ndimage.minimum_filter(image, size=5)
            - ndimage.gaussian_filter(image, sigma=1)
        )
    detail_grad = estimate_gradient(
        detail_image, grad_smooth=detail_smooth, postprocessing="scale"
    )
    mesh = warp_mesh(mesh, detail_grad, strength=detail_strength)

    # Build tonal mask lookup table
    percents = np.linspace(0, 1, tonal_levels)
    max_idx = max(n_lines[0], n_lines[1])
    mat_ind = np.arange(max_idx)

    entries = np.zeros((tonal_levels, max_idx), dtype=bool)
    for k, p in enumerate(percents):
        f = Fraction(p).limit_denominator(tonal_denom)
        if f.numerator > 0:
            entries[k] = (mat_ind % f.denominator) < f.numerator

    # Quantize image into tonal levels
    rescaled = percents ** tonal_gamma
    img_percents = np.percentile(image, (1 - rescaled) * 100)
    img_quantized = np.digitize(image, img_percents).astype(int) - 1
    img_quantized = np.clip(img_quantized, 0, tonal_levels - 1)

    # Sample quantized image at mesh positions
    def _sample_at_mesh(m):
        return ndimage.map_coordinates(
            img_quantized.astype(float),
            [m[:, :, 0], m[:, :, 1]],
            order=0,
        ).astype(int)

    tonal_at_mesh = _sample_at_mesh(mesh)

    lines = []

    def _extract_masked_lines(m, tonal, axis_lines, n_axis):
        for i in range(0, n_axis, stride):
            if axis_lines == "h":
                line = np.column_stack([m[i, :, 1], m[i, :, 0]])
                tonal_row = tonal[i, :]
            else:
                line = np.column_stack([m[:, i, 1], m[:, i, 0]])
                tonal_row = tonal[:, i]

            # Build mask: is this line index active at this tonal level?
            mask = np.array([entries[t, i] if t < tonal_levels else False
                             for t in tonal_row])

            if morph_clean > 0:
                kernel = np.ones(morph_clean, dtype=bool)
                mask = ndimage.binary_erosion(mask, structure=kernel)
                mask = ndimage.binary_dilation(mask, structure=kernel)

            # Split into contiguous True segments
            _extract_segments(line, mask, lines)

    if horizontal:
        _extract_masked_lines(mesh, tonal_at_mesh, "h", n_lines[0])
    if vertical:
        _extract_masked_lines(mesh, tonal_at_mesh, "v", n_lines[1])

    return Paths(lines)


def integral_warp(
    image: np.ndarray,
    h_stride: int = 4,
    v_stride: int = 4,
    sigma: float = 2.0,
) -> Paths:
    """Warp a grid using 1D marginal CDFs of image brightness.

    Lines are redistributed so that dark regions get denser line spacing.
    Uses separate 1D CDFs per axis: the column-wise CDF remaps row
    positions (vertical compression), and the row-wise CDF remaps column
    positions (horizontal compression).

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    h_stride : int
        Draw every Nth horizontal line.
    v_stride : int
        Draw every Nth vertical line.
    sigma : float
        Pre-blur the image.

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = ndimage.gaussian_filter(image, sigma=sigma) if sigma > 0 else image.copy()

    # Invert so dark = high value (more mass = denser lines)
    img = 255.0 - img.astype(float)
    img = np.clip(img, 1, 255)

    h, w = img.shape

    # 1D column-wise CDF: for each column, cumsum along rows → remaps row positions
    col_cdf = np.cumsum(img, axis=0)  # (H, W)
    col_totals = col_cdf[-1, :]  # (W,) total per column
    col_totals = np.maximum(col_totals, 1e-10)
    col_cdf = col_cdf / col_totals[np.newaxis, :] * (h - 1)

    # 1D row-wise CDF: for each row, cumsum along cols → remaps col positions
    row_cdf = np.cumsum(img, axis=1)  # (H, W)
    row_totals = row_cdf[:, -1]  # (H,) total per row
    row_totals = np.maximum(row_totals, 1e-10)
    row_cdf = row_cdf / row_totals[:, np.newaxis] * (w - 1)

    lines = []

    # Horizontal lines: row position is fixed, column positions are remapped
    if h_stride > 0:
        for r in range(0, h, h_stride):
            warped_cols = row_cdf[r, :]  # remapped x-coordinates
            warped_row = col_cdf[r, :]   # remapped y-coordinates (vary per column)
            lines.append(np.column_stack([warped_cols, warped_row]))

    # Vertical lines: column position is fixed, row positions are remapped
    if v_stride > 0:
        for c in range(0, w, v_stride):
            warped_col = row_cdf[:, c]   # remapped x-coordinates (vary per row)
            warped_rows = col_cdf[:, c]  # remapped y-coordinates
            lines.append(np.column_stack([warped_col, warped_rows]))

    return Paths(lines)


# ---------------------------------------------------------------------------
# Laplacian pyramid decomposition and blending
# ---------------------------------------------------------------------------

def _gaussian_pyramid(image: np.ndarray, n_levels: int) -> list[np.ndarray]:
    """Build a Gaussian pyramid by successive blur + 2x downsampling."""
    from scipy.ndimage import zoom

    levels = [image.astype(float)]
    current = image.astype(float)
    for _ in range(n_levels):
        # Blur before downsampling — this is what makes the mask soft
        blurred = ndimage.gaussian_filter(current, sigma=2.0)
        current = zoom(blurred, 0.5, order=1)
        levels.append(current)
    return levels


def _build_laplacian(gaussians: list[np.ndarray]) -> list[np.ndarray]:
    """Build Laplacian pyramid from a Gaussian pyramid."""
    from scipy.ndimage import zoom

    laplacians = []
    for i in range(len(gaussians) - 1):
        h, w = gaussians[i].shape
        upsampled = zoom(gaussians[i + 1],
                         (h / gaussians[i + 1].shape[0],
                          w / gaussians[i + 1].shape[1]),
                         order=1)
        laplacians.append(gaussians[i] - upsampled)
    laplacians.append(gaussians[-1])
    return laplacians


def _reconstruct_from_laplacian(laplacians: list[np.ndarray]) -> np.ndarray:
    """Reconstruct an image from its Laplacian pyramid."""
    from scipy.ndimage import zoom

    current = laplacians[-1].copy()
    for i in range(len(laplacians) - 2, -1, -1):
        h, w = laplacians[i].shape
        upsampled = zoom(current, (h / current.shape[0], w / current.shape[1]),
                         order=1)
        current = laplacians[i] + upsampled
    return current


def laplacian_pyramid(
    image: np.ndarray,
    n_levels: int = 4,
) -> list[np.ndarray]:
    """Decompose an image into Laplacian pyramid frequency bands.

    Each level captures detail at a different spatial frequency.
    Can be rendered with different line techniques per band.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_levels : int
        Number of pyramid levels.

    Returns
    -------
    list of (H_i, W_i) arrays, finest to coarsest.
    Last element is the coarsest (smallest) residual.
    """
    gaussians = _gaussian_pyramid(image, n_levels)
    return _build_laplacian(gaussians)


def laplacian_blend(
    image_a: np.ndarray,
    image_b: np.ndarray,
    mask: np.ndarray,
    n_levels: int = 5,
) -> np.ndarray:
    """Blend two images using Laplacian pyramid blending.

    Decomposes both images into Laplacian pyramids, blends each
    frequency band using a Gaussian-smoothed version of the mask,
    then reconstructs. Produces seamless transitions between textures.

    Parameters
    ----------
    image_a : (H, W) grayscale [0, 255]
        First image (shown where mask is white/1).
    image_b : (H, W) grayscale [0, 255]
        Second image (shown where mask is black/0).
    mask : (H, W) float [0, 1]
        Blending mask. 1 = image_a, 0 = image_b.
        Can be a hard edge — the pyramid blending smooths it.
    n_levels : int
        Pyramid depth. More levels = smoother blending across larger regions.

    Returns
    -------
    (H, W) blended image.
    """
    # Ensure same size
    h, w = image_a.shape[:2]
    if image_b.shape[:2] != (h, w):
        from scipy.ndimage import zoom
        image_b = zoom(image_b, (h / image_b.shape[0], w / image_b.shape[1]),
                       order=1)
    if mask.shape[:2] != (h, w):
        from scipy.ndimage import zoom
        mask = zoom(mask, (h / mask.shape[0], w / mask.shape[1]), order=1)

    mask = np.clip(mask.astype(float), 0, 1)

    # Heavy pre-blur on the mask before building its pyramid.
    # This is the key to smooth blending — the pyramid downsampling
    # adds further softening at each level on top of this.
    mask = ndimage.gaussian_filter(mask, sigma=min(h, w) * 0.15)

    # Build pyramids
    lap_a = _build_laplacian(_gaussian_pyramid(image_a, n_levels))
    lap_b = _build_laplacian(_gaussian_pyramid(image_b, n_levels))
    gauss_mask = _gaussian_pyramid(mask, n_levels)

    # Blend each level
    blended_lap = []
    for la, lb, gm in zip(lap_a, lap_b, gauss_mask):
        # Resize mask level to match laplacian level (might differ by 1px)
        if gm.shape != la.shape:
            from scipy.ndimage import zoom
            gm = zoom(gm, (la.shape[0] / gm.shape[0],
                           la.shape[1] / gm.shape[1]), order=1)
        blended_lap.append(gm * la + (1 - gm) * lb)

    return np.clip(_reconstruct_from_laplacian(blended_lap), 0, 255)


def repeat_blur_bands(
    image: np.ndarray,
    sizes: list[int] | None = None,
    sigma: float = 1.0,
) -> list[np.ndarray]:
    """Extract frequency bands via progressive maximum filter.

    Difference between successive maximum_filter scales reveals
    patterns at each spatial frequency — creates organic "snake skin"
    cell patterns at coarse scales.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    sizes : list of int, optional
        Maximum filter kernel sizes. Default: [5, 10, 15, 20, 30, 50, 100].
    sigma : float
        Pre-smoothing.

    Returns
    -------
    list of (H, W) band images (finest to coarsest).
    """
    if sizes is None:
        sizes = [5, 10, 15, 20, 30, 50, 100]

    img = ndimage.gaussian_filter(image, sigma=sigma) if sigma > 0 else image.copy()

    blurred = [img.copy()]
    for size in sizes:
        blurred.append(ndimage.maximum_filter(img, size=size))

    bands = []
    for i in range(len(blurred) - 1):
        diff = np.abs(blurred[i + 1] - blurred[i])
        bands.append(diff)

    return bands


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_segments(line, mask, output):
    """Split a polyline into contiguous segments where mask is True."""
    if not np.any(mask):
        return

    padded = np.concatenate([[False], mask, [False]])
    diffs = np.diff(padded.astype(int))
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]

    for s, e in zip(starts, ends):
        if e - s >= 2:
            output.append(line[s:e])
