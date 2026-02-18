"""2D and 3D transform builders + unified apply().

Convention: column vectors, matrix @ points.
2D uses 3x3 homogeneous matrices, 3D uses 4x4 homogeneous matrices.
"""

from __future__ import annotations

from typing import List

import numpy as np

from penpal.core.types import Lines

# ---------------------------------------------------------------------------
# 2D transforms (return 3x3 homogeneous matrices)
# ---------------------------------------------------------------------------


def rotate(angle: float, center=None, degrees: bool = True) -> np.ndarray:
    """2D rotation matrix. Positive = counter-clockwise."""
    if degrees:
        angle = np.radians(angle)
    c, s = np.cos(angle), np.sin(angle)
    m = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)
    if center is not None:
        cx, cy = center
        m = translate(cx, cy) @ m @ translate(-cx, -cy)
    return m


def reflect(angle: float, point=None, degrees: bool = True) -> np.ndarray:
    """2D reflection across a line through origin at given angle."""
    if degrees:
        angle = np.radians(angle)
    c2, s2 = np.cos(2 * angle), np.sin(2 * angle)
    m = np.array([[c2, s2, 0], [s2, -c2, 0], [0, 0, 1]], dtype=np.float64)
    if point is not None:
        px, py = point
        m = translate(px, py) @ m @ translate(-px, -py)
    return m


def translate(dx: float, dy: float) -> np.ndarray:
    """2D translation matrix."""
    return np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]], dtype=np.float64)


def scale(sx: float, sy: float = None, center=None) -> np.ndarray:
    """2D scale matrix. If sy is None, uniform scale."""
    if sy is None:
        sy = sx
    m = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], dtype=np.float64)
    if center is not None:
        cx, cy = center
        m = translate(cx, cy) @ m @ translate(-cx, -cy)
    return m


# ---------------------------------------------------------------------------
# 3D transforms (return 4x4 homogeneous matrices)
# ---------------------------------------------------------------------------


def rotate_x(angle: float, degrees: bool = True) -> np.ndarray:
    """3D rotation around X axis."""
    if degrees:
        angle = np.radians(angle)
    c, s = np.cos(angle), np.sin(angle)
    return np.array(
        [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )


def rotate_y(angle: float, degrees: bool = True) -> np.ndarray:
    """3D rotation around Y axis."""
    if degrees:
        angle = np.radians(angle)
    c, s = np.cos(angle), np.sin(angle)
    return np.array(
        [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )


def rotate_z(angle: float, degrees: bool = True) -> np.ndarray:
    """3D rotation around Z axis."""
    if degrees:
        angle = np.radians(angle)
    c, s = np.cos(angle), np.sin(angle)
    return np.array(
        [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )


def rotate_axis(axis, angle: float, degrees: bool = True) -> np.ndarray:
    """3D rotation around arbitrary axis (Rodrigues)."""
    if degrees:
        angle = np.radians(angle)
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    c, s = np.cos(angle), np.sin(angle)
    t = 1 - c
    return np.array(
        [
            [t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0],
            [t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0],
            [t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0],
            [0, 0, 0, 1],
        ],
        dtype=np.float64,
    )


def translate3d(dx: float, dy: float, dz: float) -> np.ndarray:
    """3D translation matrix."""
    return np.array(
        [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]],
        dtype=np.float64,
    )


def scale3d(sx: float, sy: float = None, sz: float = None) -> np.ndarray:
    """3D scale matrix. If sy/sz are None, uniform scale."""
    if sy is None:
        sy = sx
    if sz is None:
        sz = sx
    return np.array(
        [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]],
        dtype=np.float64,
    )


# ---------------------------------------------------------------------------
# Unified apply — works for both 2D and 3D
# ---------------------------------------------------------------------------


def apply(matrix: np.ndarray, lines: Lines) -> Lines:
    """Apply a homogeneous transform to a list of polylines.

    Detects 2D (3x3 matrix, (N,2) points) vs 3D (4x4 matrix, (N,3) points)
    automatically. Pads to homogeneous, matmuls, strips back.
    """
    if not lines:
        return []

    result = []
    for pts in lines:
        n = pts.shape[0]
        d = pts.shape[1]  # 2 or 3
        # Pad with ones for homogeneous coords
        ones = np.ones((n, 1), dtype=np.float64)
        homo = np.hstack([pts, ones])  # (N, d+1)
        # matrix @ points.T → (d+1, N), then transpose back
        transformed = (matrix @ homo.T).T
        result.append(transformed[:, :d].copy())
    return result
