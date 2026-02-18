"""Drawing — the convergence point for all penpal workflows.

Represents physical paper with dimensions, ordered layers, and
knows how to display/save itself.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import List

import numpy as np

from penpal.core.layer import Layer, LayerStyle
from penpal.core.paths import Paths
from penpal.core.types import Lines


class Drawing:
    """A drawing with physical dimensions and named layers.

    All workflows (2D, 3D, CV, RL) produce a Drawing.
    """

    def __init__(self, width: float, height: float, units: str = "in", show_grid: bool = True):
        self.width = width
        self.height = height
        self.units = units
        self.show_grid = show_grid
        self._layers: OrderedDict[str, Layer] = OrderedDict()

    def layer(self, name: str, **style_kwargs) -> Layer:
        """Get or create a named layer. Returns the Layer for chaining."""
        if name not in self._layers:
            self._layers[name] = Layer(name, **style_kwargs)
        elif style_kwargs:
            # Update style if kwargs provided on existing layer
            for k, v in style_kwargs.items():
                setattr(self._layers[name].style, k, v)
        return self._layers[name]

    @property
    def layers(self) -> List[Layer]:
        """Ordered list of layers."""
        return list(self._layers.values())

    def flatten(self) -> Layer:
        """Merge all layers into one."""
        merged = Layer("merged")
        for lay in self._layers.values():
            merged.paths += lay.paths
        return merged

    def transform(self, matrix: np.ndarray):
        """Apply transform to all layers."""
        for lay in self._layers.values():
            lay.transform(matrix)

    # --- Display ---

    def show(self, **kwargs):
        """Display via matplotlib."""
        from penpal.backends.matplotlib import render
        return render(self, **kwargs)

    def save(self, path: str, **kwargs):
        """Save as SVG."""
        from penpal.io.svg_write import save_drawing
        save_drawing(self, path, **kwargs)

    def save_layers(self, path: str, **kwargs):
        """Save each layer as a separate SVG."""
        from penpal.io.svg_write import save_drawing_layers
        save_drawing_layers(self, path, **kwargs)

    def _repr_svg_(self) -> str:
        """Jupyter notebook inline SVG display."""
        from penpal.io.svg_write import to_svg_string
        return to_svg_string(self, grid=self.show_grid)

    def _repr_html_(self) -> str:
        """Fallback HTML display with embedded SVG."""
        svg = self._repr_svg_()
        return f'<div style="background:white;padding:10px">{svg}</div>'

    @classmethod
    def from_svg(cls, path: str) -> Drawing:
        """Load from SVG file."""
        from penpal.io.svg_read import read_svg
        return read_svg(path)

    def __repr__(self) -> str:
        n_layers = len(self._layers)
        layer_names = ", ".join(self._layers.keys()) if n_layers <= 5 else f"{n_layers} layers"
        return f"Drawing({self.width}x{self.height} {self.units}, [{layer_names}])"
