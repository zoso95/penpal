"""Lighting — per-face shading for NPR sketch rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Union

import numpy as np

from penpal.render3d.shapes import Face3D


@dataclass
class DirectionalLight:
    """A directional light source (e.g., sun).

    Parameters
    ----------
    direction : tuple
        Direction the light shines FROM (toward the scene).
        Auto-normalized.
    intensity : float
        Light intensity multiplier.
    """
    direction: tuple = (1, 1, 1)
    intensity: float = 1.0

    def __post_init__(self):
        d = np.asarray(self.direction, dtype=np.float64)
        norm = np.linalg.norm(d)
        if norm > 1e-12:
            d = d / norm
        self.direction = tuple(d)


@dataclass
class PointLight:
    """A point light source.

    Parameters
    ----------
    position : tuple
        Position in world space.
    intensity : float
        Light intensity multiplier.
    falloff : float
        Distance falloff exponent. 0 = no falloff, 2 = inverse square.
    """
    position: tuple = (5, 5, 5)
    intensity: float = 1.0
    falloff: float = 0.0


Light = Union[DirectionalLight, PointLight]


def compute_face_intensities(
    faces: List[Face3D],
    lights: List[Light],
    ambient: float = 0.1,
) -> np.ndarray:
    """Compute per-face lighting intensity using Lambert diffuse model.

    Parameters
    ----------
    faces : list of Face3D
    lights : list of DirectionalLight or PointLight
    ambient : float
        Ambient light contribution [0, 1].

    Returns
    -------
    np.ndarray, shape (n_faces,), values clamped to [0, 1].
    """
    n = len(faces)
    intensities = np.full(n, ambient, dtype=np.float64)

    for i, face in enumerate(faces):
        normal = face.normal()
        centroid = face.centroid()

        for light in lights:
            if isinstance(light, DirectionalLight):
                light_dir = np.asarray(light.direction, dtype=np.float64)
                ndotl = max(0.0, np.dot(normal, light_dir))
                intensities[i] += ndotl * light.intensity

            elif isinstance(light, PointLight):
                to_light = np.asarray(light.position, dtype=np.float64) - centroid
                dist = np.linalg.norm(to_light)
                if dist < 1e-10:
                    continue
                light_dir = to_light / dist
                ndotl = max(0.0, np.dot(normal, light_dir))
                if light.falloff > 0:
                    atten = 1.0 / (1.0 + dist ** light.falloff)
                else:
                    atten = 1.0
                intensities[i] += ndotl * light.intensity * atten

    return np.clip(intensities, 0.0, 1.0)
