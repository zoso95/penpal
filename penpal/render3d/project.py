"""Projection math for 3D rendering.

All matrices follow penpal convention: column vectors, left-multiply (matrix @ pts.T).
4x4 homogeneous matrices throughout.
"""

from __future__ import annotations

import numpy as np

from penpal.core.types import Lines


def look_at(eye, target, up) -> np.ndarray:
    """Build a 4x4 view matrix (world -> camera space).

    Camera looks down -Z in camera space (OpenGL convention).
    """
    eye = np.asarray(eye, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)

    forward = target - eye
    forward = forward / np.linalg.norm(forward)

    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)

    cam_up = np.cross(right, forward)

    m = np.eye(4, dtype=np.float64)
    m[0, :3] = right
    m[1, :3] = cam_up
    m[2, :3] = -forward
    m[0, 3] = -np.dot(right, eye)
    m[1, 3] = -np.dot(cam_up, eye)
    m[2, 3] = np.dot(forward, eye)
    return m


def perspective(fov: float, aspect: float, near: float, far: float,
                degrees: bool = True) -> np.ndarray:
    """Build a 4x4 perspective projection matrix.

    After projection, divide by w to get NDC in [-1, 1].
    """
    if degrees:
        fov = np.radians(fov)
    f = 1.0 / np.tan(fov / 2)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = -(far + near) / (far - near)
    m[2, 3] = -2 * far * near / (far - near)
    m[3, 2] = -1
    return m


def project_points(points: np.ndarray, mvp: np.ndarray) -> np.ndarray:
    """Project 3D points through an MVP matrix to 2D NDC.

    Parameters
    ----------
    points : (N, 3) array
    mvp : (4, 4) matrix

    Returns
    -------
    (N, 2) array after perspective divide.
    """
    n = points.shape[0]
    homo = np.hstack([points, np.ones((n, 1))])
    clip = (mvp @ homo.T).T
    w = clip[:, 3:4]
    w = np.where(np.abs(w) < 1e-10, 1e-10, w)
    ndc = clip[:, :2] / w
    return ndc


def project_lines(lines: Lines, mvp: np.ndarray) -> Lines:
    """Project a list of 3D polylines through MVP to 2D NDC."""
    result = []
    for pts in lines:
        result.append(project_points(pts[:, :3], mvp))
    return result


def viewport_map(ndc: np.ndarray, x0: float, y0: float,
                 width: float, height: float) -> np.ndarray:
    """Map NDC [-1,1] to drawing coordinates.

    Flips Y: NDC y=1 (top) → y0, NDC y=-1 (bottom) → y0+height.
    """
    x = x0 + (ndc[:, 0] + 1) * 0.5 * width
    y = y0 + (1 - ndc[:, 1]) * 0.5 * height
    return np.column_stack([x, y])
