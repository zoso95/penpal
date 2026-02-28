"""Halftone techniques — convert photos to plotter line art.

All functions take a grayscale image (H, W) float64 [0, 255] and
return Paths in pixel coordinates. Use cv.image.map_to_drawing()
to fit the result into a Drawing.
"""

from __future__ import annotations

from typing import List, Tuple, Union

import numpy as np

from penpal.core.paths import Paths
from penpal.core.types import Lines
from penpal.cv.image import smooth


# ---------------------------------------------------------------------------
# Core clipper
# ---------------------------------------------------------------------------

def _clip_line_to_mask(p0: np.ndarray, p1: np.ndarray,
                       mask: np.ndarray,
                       n_samples: int = 500) -> Lines:
    """Walk along a line and emit segments where the mask is True.

    Parameters
    ----------
    p0, p1 : (2,) arrays
        Line endpoints in pixel coordinates (x, y).
    mask : (H, W) boolean array
    n_samples : int
        Number of sample points along the line.

    Returns
    -------
    List of (N, 2) arrays — visible segments.
    """
    h, w = mask.shape
    ts = np.linspace(0.0, 1.0, n_samples)
    pts = p0[np.newaxis, :] + ts[:, np.newaxis] * (p1 - p0)[np.newaxis, :]

    # Sample mask at each point
    px = np.round(pts[:, 0]).astype(int)
    py = np.round(pts[:, 1]).astype(int)

    # Bounds check
    in_bounds = (px >= 0) & (px < w) & (py >= 0) & (py < h)
    hits = np.zeros(n_samples, dtype=bool)
    valid = np.where(in_bounds)[0]
    if len(valid) == 0:
        return []
    hits[valid] = mask[py[valid], px[valid]]

    # Extract contiguous runs of True
    segments = []
    in_run = False
    run_start = 0

    for i in range(n_samples):
        if hits[i] and not in_run:
            in_run = True
            run_start = i
        elif not hits[i] and in_run:
            in_run = False
            if i - run_start >= 2:
                segments.append(pts[run_start:i])
    if in_run and n_samples - run_start >= 2:
        segments.append(pts[run_start:])

    return segments


def _generate_rotated_lines(n_lines: int, angle_deg: float,
                            img_h: int, img_w: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Generate parallel lines rotated around the image center.

    Returns list of (p0, p1) endpoint pairs in pixel coordinates.
    """
    cx, cy = img_w / 2, img_h / 2
    diag = np.sqrt(img_w**2 + img_h**2)
    half = diag / 2

    angle = np.radians(angle_deg)
    cos_a, sin_a = np.cos(angle), np.sin(angle)

    # Direction along the line
    dx, dy = cos_a, sin_a
    # Perpendicular direction (for spacing)
    nx, ny = -sin_a, cos_a

    lines = []
    offsets = np.linspace(-half, half, n_lines)
    for offset in offsets:
        # Center of this line (offset perpendicular to angle)
        mx = cx + offset * nx
        my = cy + offset * ny
        # Line endpoints (extend along direction)
        p0 = np.array([mx - half * dx, my - half * dy])
        p1 = np.array([mx + half * dx, my + half * dy])
        lines.append((p0, p1))
    return lines


# ---------------------------------------------------------------------------
# Contour extraction
# ---------------------------------------------------------------------------

def _extract_contours(field: np.ndarray, levels, min_length: int = 10) -> Lines:
    """Extract contour polylines from a 2D scalar field.

    Uses matplotlib's contour machinery. Returns lines in pixel
    coordinates (x=col, y=row).
    """
    from matplotlib.figure import Figure

    fig = Figure()
    ax = fig.add_subplot(111)
    cs = ax.contour(field, levels=levels)

    segments: Lines = []
    for level_segs in cs.allsegs:
        for seg in level_segs:
            if len(seg) >= min_length:
                segments.append(seg.astype(np.float64))

    return segments


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def crosshatch(
    image: np.ndarray,
    angles: tuple = (45, -45),
    n_bands: int = 8,
    max_density: int = 1200,
    min_density: int = 0,
    gamma: float = 2.2,
    sigma: float = 2.0,
    samples_per_line: int = 500,
) -> Paths:
    """Convert a grayscale image to crosshatched line art.

    Divides the image into tone bands from dark to light. Each band
    gets parallel lines at the given angles, with denser lines for
    darker tones.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    angles : tuple of float
        Hatch angles in degrees (e.g. (45, -45) for crosshatch).
    n_bands : int
        Number of tone bands.
    max_density : int
        Number of lines for the darkest band.
    min_density : int
        Number of lines for the lightest band.
    gamma : float
        Controls density falloff curve. Higher = more contrast.
    sigma : float
        Gaussian pre-smoothing sigma.
    samples_per_line : int
        Precision of line-to-mask clipping.

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = smooth(image, sigma)
    h, w = img.shape[:2]

    # Threshold levels
    thresholds = np.linspace(0, 255, n_bands + 1)

    all_segments: Lines = []

    for band_idx in range(n_bands):
        lo = thresholds[band_idx]
        hi = thresholds[band_idx + 1]

        # Mask: pixels in this tone band
        # Dark pixels (low values) are in low-index bands
        mask = (img >= lo) & (img < hi) if band_idx < n_bands - 1 else (img >= lo) & (img <= hi)

        if not np.any(mask):
            continue

        # Density: dark bands (low index) get more lines
        t = band_idx / max(n_bands - 1, 1)  # 0=darkest, 1=lightest
        density = int(max_density * (1 - t) ** gamma + min_density * (1 - (1 - t) ** gamma))
        if density < 2:
            continue

        for angle in angles:
            lines = _generate_rotated_lines(density, angle, h, w)
            for p0, p1 in lines:
                segs = _clip_line_to_mask(p0, p1, mask, n_samples=samples_per_line)
                all_segments.extend(segs)

    return Paths(all_segments)


def edges(
    image: np.ndarray,
    sigma: float = 2.0,
    threshold: float = 0.3,
    min_length: int = 20,
) -> Paths:
    """Extract edge outlines from a grayscale image.

    Uses Sobel gradient magnitude to detect edges, then traces
    contour lines at the threshold level. Returns clean polylines
    suitable for bold outlines on top of crosshatching.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    sigma : float
        Gaussian pre-smoothing sigma. Larger = fewer, bolder edges.
    threshold : float
        Edge threshold (0-1). Lower = more edges.
    min_length : int
        Minimum contour length in points. Filters tiny edge fragments.

    Returns
    -------
    Paths in pixel coordinates.
    """
    from scipy.ndimage import sobel

    img = smooth(image, sigma)

    gx = sobel(img, axis=1)
    gy = sobel(img, axis=0)
    mag = np.sqrt(gx**2 + gy**2)

    mag_max = mag.max()
    if mag_max > 0:
        mag /= mag_max

    segments = _extract_contours(mag, levels=[threshold], min_length=min_length)
    return Paths(segments)


def morphological_halftone(
    image: np.ndarray,
    n_bands: int = 5,
    erosion_step: int | tuple = None,
    sigma: float = 2.0,
    clean: int = 2,
    min_length: int = 10,
) -> Paths:
    """Morphological halftone — concentric contour rings from repeated erosion.

    Divides the image into tone bands, then repeatedly erodes each
    band's binary mask. The accumulation creates a distance-like field
    whose contour lines form concentric rings following the shape of
    each tone region. Darker regions get tighter spacing (denser lines).

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_bands : int
        Number of tone bands.
    erosion_step : int or tuple of ints, optional
        Binary erosion iterations per step for each band. Can be a single
        int (same for all bands) or a tuple of length n_bands.
        Default: linearly from 2 (darkest, densest) to 2*n_bands (lightest).
    sigma : float
        Gaussian pre-smoothing sigma.
    clean : int
        Binary opening iterations for noise reduction. 0 = no cleaning.
    min_length : int
        Minimum contour length in points.

    Returns
    -------
    Paths in pixel coordinates.
    """
    from scipy.ndimage import binary_erosion, binary_opening

    img = smooth(image, sigma)
    h, w = img.shape[:2]

    if erosion_step is None:
        steps = tuple(
            int(2 + (2 * n_bands - 2) * (i / max(n_bands - 1, 1)))
            for i in range(n_bands)
        )
    elif isinstance(erosion_step, int):
        steps = (erosion_step,) * n_bands
    else:
        steps = tuple(erosion_step)

    thresholds = np.linspace(0, 255, n_bands + 1)
    accumulator = np.zeros((h, w), dtype=np.float64)

    for band_idx in range(n_bands):
        lo = thresholds[band_idx]
        hi = thresholds[band_idx + 1]

        if band_idx < n_bands - 1:
            mask = (img >= lo) & (img < hi)
        else:
            mask = (img >= lo) & (img <= hi)

        if not np.any(mask):
            continue

        if clean > 0:
            mask = binary_opening(mask, iterations=clean)
            if not np.any(mask):
                continue

        n_iter = steps[band_idx] if band_idx < len(steps) else steps[-1]

        base = mask.copy()
        accumulator += base.astype(np.float64)

        while np.any(base):
            eroded = binary_erosion(base, iterations=n_iter)
            if not np.any(eroded):
                break
            accumulator += eroded.astype(np.float64)
            base = eroded

    max_val = accumulator.max()
    if max_val <= 0:
        return Paths([])

    levels = np.arange(0.5, max_val + 0.5, 1.0)
    segments = _extract_contours(accumulator, levels=levels, min_length=min_length)
    return Paths(segments)


def line_scan(
    image: np.ndarray,
    n_bands: int = 4,
    sigma: float = 1.0,
    row_skip: int = 1,
) -> Paths:
    """Convert a grayscale image to horizontal scan lines.

    Scans the image row by row. Rows are interleaved across tone bands —
    darker regions get more rows assigned to them.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_bands : int
        Number of tone bands. Each band scans every n_bands-th row.
    sigma : float
        Gaussian pre-smoothing sigma.
    row_skip : int
        Additional row skipping factor (1 = every interleaved row).

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = smooth(image, sigma)
    h, w = img.shape

    thresholds = np.linspace(0, 255, n_bands + 1)[1:]  # upper bounds

    all_segments: Lines = []

    for band_idx in range(n_bands):
        thresh = thresholds[band_idx]

        # Scan interleaved rows for this band
        rows = range(band_idx * row_skip, h, n_bands * row_skip)

        for y in rows:
            if y >= h:
                break
            # Dark pixels (below threshold) are drawn
            dark = img[y] < thresh
            if not np.any(dark):
                continue

            # Find contiguous runs of True
            # Pad with False to detect edges
            padded = np.concatenate([[False], dark, [False]])
            diffs = np.diff(padded.astype(int))
            starts = np.where(diffs == 1)[0]
            ends = np.where(diffs == -1)[0]

            for s, e in zip(starts, ends):
                if e - s >= 2:
                    all_segments.append(np.array([[s, y], [e - 1, y]],
                                                 dtype=np.float64))

    return Paths(all_segments)


def dot_grid(
    image: np.ndarray,
    spacing: int = 8,
    max_radius: float = None,
    min_radius: float = 0.5,
    sigma: float = 1.0,
    n_circle_points: int = 16,
    threshold: float = 240,
) -> Paths:
    """Convert a grayscale image to halftone dots on a regular grid.

    Each grid cell gets a circle whose radius is proportional to the
    local average darkness.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    spacing : int
        Grid cell size in pixels.
    max_radius : float, optional
        Maximum dot radius. Defaults to spacing / 2.
    min_radius : float
        Minimum dot radius (dots below this are omitted).
    sigma : float
        Gaussian pre-smoothing sigma.
    n_circle_points : int
        Points per dot circle.
    threshold : float
        Brightness threshold — pixels brighter than this get no dot.

    Returns
    -------
    Paths in pixel coordinates.
    """
    img = smooth(image, sigma)
    h, w = img.shape

    if max_radius is None:
        max_radius = spacing / 2

    theta = np.linspace(0, 2 * np.pi, n_circle_points + 1)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    lines = []
    for row in range(spacing // 2, h, spacing):
        for col in range(spacing // 2, w, spacing):
            # Sample local average
            r0 = max(0, row - spacing // 2)
            r1 = min(h, row + spacing // 2)
            c0 = max(0, col - spacing // 2)
            c1 = min(w, col + spacing // 2)
            mean_val = img[r0:r1, c0:c1].mean()

            if mean_val > threshold:
                continue

            # Darker = larger radius (invert brightness)
            darkness = 1 - mean_val / 255
            radius = min_radius + darkness * (max_radius - min_radius)

            if radius < min_radius:
                continue

            circle = np.column_stack([
                col + radius * cos_t,
                row + radius * sin_t,
            ])
            lines.append(circle)

    return Paths(lines)


def dot_grid_cmyk(
    image_rgb: np.ndarray,
    spacing: int = 10,
    max_radius: float = None,
    sigma: float = 1.0,
    n_circle_points: int = 16,
    angles: tuple = (15, 75, 0, 45),
) -> list[Paths]:
    """CMYK halftone dots — separate dot grids per color channel.

    Each channel gets a rotated grid to minimize moire interference.

    Parameters
    ----------
    image_rgb : (H, W, 3) RGB [0, 255]
    spacing : int
        Grid cell size.
    max_radius : float, optional
        Maximum dot radius.
    sigma : float
        Pre-smoothing.
    n_circle_points : int
        Points per circle.
    angles : tuple of 4 floats
        Grid rotation angles in degrees for C, M, Y, K channels.

    Returns
    -------
    list of 4 Paths (C, M, Y, K) in pixel coordinates.
    """
    if max_radius is None:
        max_radius = spacing / 2

    # Convert RGB to CMYK
    rgb = image_rgb.astype(float) / 255
    k = 1 - np.max(rgb, axis=2)
    c = np.where(k < 1, (1 - rgb[:, :, 0] - k) / (1 - k + 1e-10), 0)
    m = np.where(k < 1, (1 - rgb[:, :, 1] - k) / (1 - k + 1e-10), 0)
    y = np.where(k < 1, (1 - rgb[:, :, 2] - k) / (1 - k + 1e-10), 0)

    channels = [c, m, y, k]
    result = []

    for ch, angle in zip(channels, angles):
        # Convert channel to "image" (0=no ink, 255=full ink -> invert for dot_grid)
        ch_img = (1 - ch) * 255
        result.append(dot_grid(ch_img, spacing=spacing, max_radius=max_radius,
                               sigma=sigma, n_circle_points=n_circle_points))

    return result


def mezzotint(
    image: np.ndarray,
    n_points: int = 50000,
    dot_radius: float = 1.0,
    n_circle_points: int = 8,
    sigma: float = 1.0,
    seed: int | None = None,
) -> Paths:
    """Mezzotint / importance-sampled stippling.

    Places dots randomly with probability proportional to image darkness
    (multinomial sampling). Denser stippling in darker areas.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_points : int
        Total number of stipple dots.
    dot_radius : float
        Radius of each dot circle.
    n_circle_points : int
        Points per dot circle.
    sigma : float
        Pre-smoothing.
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths in pixel coordinates.
    """
    rng = np.random.default_rng(seed)
    img = smooth(image, sigma)
    h, w = img.shape

    # Invert: dark pixels = high probability
    darkness = 255 - img
    darkness = np.clip(darkness, 0, None)

    # Flatten to PMF
    flat = darkness.ravel()
    total = flat.sum()
    if total <= 0:
        return Paths()
    pmf = flat / total

    # Multinomial sampling
    counts = rng.multinomial(n_points, pmf)

    theta = np.linspace(0, 2 * np.pi, n_circle_points + 1)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    lines = []
    for pixel_idx in np.nonzero(counts)[0]:
        row = pixel_idx // w
        col = pixel_idx % w
        count = counts[pixel_idx]
        for _ in range(count):
            # Jitter within pixel
            cx = col + rng.uniform(-0.5, 0.5)
            cy = row + rng.uniform(-0.5, 0.5)
            circle = np.column_stack([cx + dot_radius * cos_t,
                                      cy + dot_radius * sin_t])
            lines.append(circle)

    return Paths(lines)


def voronoi_stipple(
    image: np.ndarray,
    n_points: int = 2000,
    sigma: float = 2.0,
    show_edges: bool = True,
    show_points: bool = False,
    dot_radius: float = 1.5,
    seed: int | None = None,
) -> Paths:
    """Voronoi-based stippling weighted by image darkness.

    Samples points with density proportional to image darkness using
    rejection sampling, then computes Voronoi diagram. Returns either
    Voronoi edges, stipple dots, or both.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_points : int
        Number of sample points.
    sigma : float
        Pre-smoothing.
    show_edges : bool
        Include Voronoi ridge edges.
    show_points : bool
        Include dot marks at Voronoi sites.
    dot_radius : float
        Radius of dot marks (if show_points=True).
    seed : int, optional
        Random seed.

    Returns
    -------
    Paths in pixel coordinates.
    """
    from scipy.spatial import Voronoi

    rng = np.random.default_rng(seed)
    img = smooth(image, sigma)
    h, w = img.shape

    # Importance sampling via rejection
    darkness = 255 - img
    max_dark = darkness.max()
    if max_dark <= 0:
        return Paths()

    points = []
    while len(points) < n_points:
        batch_size = n_points * 3
        xs = rng.uniform(0, w, batch_size)
        ys = rng.uniform(0, h, batch_size)
        px = np.clip(xs.astype(int), 0, w - 1)
        py = np.clip(ys.astype(int), 0, h - 1)
        probs = darkness[py, px] / max_dark
        accept = rng.random(batch_size) < probs
        accepted = np.column_stack([xs[accept], ys[accept]])
        points.append(accepted)
    points = np.vstack(points)[:n_points]

    vor = Voronoi(points)

    lines = []

    if show_edges:
        for start, finish in vor.ridge_vertices:
            if start == -1 or finish == -1:
                continue
            v0 = vor.vertices[start]
            v1 = vor.vertices[finish]
            # Clip to image bounds
            if (0 <= v0[0] <= w and 0 <= v0[1] <= h and
                    0 <= v1[0] <= w and 0 <= v1[1] <= h):
                lines.append(np.array([v0, v1]))

    if show_points:
        theta = np.linspace(0, 2 * np.pi, 9)
        for cx, cy in points:
            dot = np.column_stack([cx + dot_radius * np.cos(theta),
                                   cy + dot_radius * np.sin(theta)])
            lines.append(dot)

    return Paths(lines)


def spiral_portrait(
    image: np.ndarray,
    n_turns: int = 80,
    center: tuple = None,
    amplitude_scale: float = 3.0,
    frequency_scale: float = 8.0,
    sigma: float = 2.0,
    n_points_per_turn: int = 200,
) -> Paths:
    """Convert image to an Archimedean spiral with brightness-modulated amplitude.

    A single spiral traces from center outward. At each point along the
    spiral, the sine-wave amplitude is modulated by the local image darkness,
    creating a TSP-art-like portrait from a single continuous curve.

    Parameters
    ----------
    image : (H, W) grayscale [0, 255]
    n_turns : int
        Number of spiral turns.
    center : tuple, optional
        Spiral center in pixel coords. Defaults to image center.
    amplitude_scale : float
        Maximum wave amplitude (in pixels).
    frequency_scale : float
        Wave frequency multiplier (waves per turn).
    sigma : float
        Pre-smoothing.
    n_points_per_turn : int
        Resolution of spiral per turn.

    Returns
    -------
    Paths in pixel coordinates (single continuous polyline).
    """
    img = smooth(image, sigma)
    h, w = img.shape

    if center is None:
        center = (w / 2, h / 2)
    cx, cy = center

    max_r = min(w, h) / 2 * 0.95
    n_total = n_turns * n_points_per_turn
    t = np.linspace(0, n_turns * 2 * np.pi, n_total)

    # Archimedean spiral radius
    r_base = max_r * t / (n_turns * 2 * np.pi)

    # Sample image darkness along spiral
    x_spiral = cx + r_base * np.cos(t)
    y_spiral = cy + r_base * np.sin(t)

    px = np.clip(x_spiral.astype(int), 0, w - 1)
    py = np.clip(y_spiral.astype(int), 0, h - 1)
    darkness = (255 - img[py, px]) / 255  # 0=white, 1=black

    # Modulate radius with sine wave whose amplitude depends on darkness
    wave = amplitude_scale * darkness * np.sin(frequency_scale * t)

    # Add wave perpendicular to spiral direction
    dx = -np.sin(t)
    dy = np.cos(t)
    x_final = x_spiral + wave * dx
    y_final = y_spiral + wave * dy

    pts = np.column_stack([x_final, y_final])
    return Paths([pts])
