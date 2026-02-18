"""Layer — a named, styled collection of Paths.

Layer = name + style + Paths. Manipulation delegates to Paths internally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union, List

import numpy as np

from penpal.core.paths import Paths
from penpal.core.types import Lines


@dataclass
class LayerStyle:
    """Visual style for a layer."""

    color: str = "black"
    linewidth: float = 0.5
    alpha: float = 1.0


class Layer:
    """A named layer containing Paths with a visual style."""

    def __init__(self, name: str, **style_kwargs):
        self.name = name
        self.paths = Paths()
        self.style = LayerStyle(**style_kwargs)

    def add(self, data: Union[Paths, Lines, np.ndarray]) -> Layer:
        """Append lines. Accepts Paths, Lines, or single ndarray."""
        if isinstance(data, Paths):
            self.paths += data
        else:
            self.paths += Paths(data)
        return self

    # --- Convenience: delegate to self.paths ---

    def transform(self, matrix: np.ndarray):
        self.paths = self.paths.transform(matrix)

    def optimize(self):
        self.paths = self.paths.optimize()

    def clip(self, polygon: np.ndarray):
        self.paths = self.paths.clip(polygon)

    def clip_rect(self, xmin, ymin, xmax, ymax):
        self.paths = self.paths.clip_rect(xmin, ymin, xmax, ymax)

    def filter(self, min_length: float):
        self.paths = self.paths.filter(min_length)

    # --- Info ---

    @property
    def lines(self) -> Lines:
        return self.paths.lines

    def bounds(self):
        return self.paths.bounds()

    def __len__(self):
        return len(self.paths)

    def __repr__(self):
        return f"Layer('{self.name}', {len(self.paths)} lines, style={self.style})"
