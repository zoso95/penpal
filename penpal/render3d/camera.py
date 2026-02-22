"""Camera for 3D rendering.

Provides view + projection matrices. Use Camera.orbit() for interactive control.
"""

from __future__ import annotations

import numpy as np

from penpal.render3d.project import look_at, perspective


class Camera:
    """A 3D camera defined by position, target, and projection parameters.

    Parameters
    ----------
    position : (3,) array-like
        Camera position in world space.
    target : (3,) array-like
        Point the camera looks at.
    up : (3,) array-like
        World up vector (default [0, 1, 0]).
    fov : float
        Vertical field of view in degrees.
    near, far : float
        Clipping planes.
    """

    def __init__(self, position=(0, 0, 5), target=(0, 0, 0), up=(0, 1, 0),
                 fov: float = 60, near: float = 0.1, far: float = 100.0):
        self.position = np.asarray(position, dtype=np.float64)
        self.target = np.asarray(target, dtype=np.float64)
        self.up = np.asarray(up, dtype=np.float64)
        self.fov = fov
        self.near = near
        self.far = far

    @classmethod
    def orbit(cls, target=(0, 0, 0), distance: float = 5.0,
              azimuth: float = 30, elevation: float = 30,
              fov: float = 60, **kwargs) -> Camera:
        """Create a camera orbiting around a target point.

        Parameters
        ----------
        target : (3,) center of orbit
        distance : float from target
        azimuth : float, degrees (0 = +X, 90 = +Z)
        elevation : float, degrees (0 = horizontal, 90 = top-down)
        fov : float, degrees
        """
        target = np.asarray(target, dtype=np.float64)
        az = np.radians(azimuth)
        el = np.radians(elevation)
        x = distance * np.cos(el) * np.cos(az)
        y = distance * np.sin(el)
        z = distance * np.cos(el) * np.sin(az)
        position = target + np.array([x, y, z])
        return cls(position=position, target=target, up=(0, 1, 0),
                   fov=fov, **kwargs)

    @property
    def view_matrix(self) -> np.ndarray:
        """4x4 view matrix (world -> camera space)."""
        return look_at(self.position, self.target, self.up)

    @property
    def projection_matrix(self) -> np.ndarray:
        """4x4 perspective projection matrix."""
        return perspective(self.fov, 1.0, self.near, self.far)

    @property
    def vp_matrix(self) -> np.ndarray:
        """Combined view-projection matrix."""
        return self.projection_matrix @ self.view_matrix

    @property
    def forward(self) -> np.ndarray:
        """Unit vector from camera toward target."""
        d = self.target - self.position
        return d / np.linalg.norm(d)

    def __repr__(self):
        return (f"Camera(pos={self.position.tolist()}, "
                f"target={self.target.tolist()}, fov={self.fov})")
