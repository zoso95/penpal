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

# Physical pen width defaults (in inches)
# 0.3mm Micron = ~0.012in, 0.5mm = ~0.020in
PEN_WIDTH_MM = {
    0.2: 0.2 / 25.4,
    0.3: 0.3 / 25.4,
    0.5: 0.5 / 25.4,
    0.8: 0.8 / 25.4,
    1.0: 1.0 / 25.4,
}
DEFAULT_PEN_WIDTH_IN = 0.3 / 25.4  # 0.3mm Micron pen


def pen_width(mm: float) -> float:
    """Convert pen width from mm to inches (the internal unit)."""
    return mm / 25.4


class Drawing:
    """A drawing with physical dimensions and named layers.

    All workflows (2D, 3D, CV, RL) produce a Drawing.

    Parameters
    ----------
    width, height : float
        Physical dimensions in the given units.
    units : str
        'in', 'mm', 'cm', etc.
    show_grid : bool
        Show reference grid in notebook display.
    center : bool
        If True, coordinate origin is at center of page.
        x ranges from -width/2 to width/2, y from -height/2 to height/2.
    """

    # TODO: add margin parameter — margin=0.5 would reserve 0.25in on each side,
    # adjusting x_range/y_range and auto-clipping all layers to the drawable area.

    def __init__(self, width: float, height: float, units: str = "in",
                 show_grid: bool = True, center: bool = False):
        self.width = width
        self.height = height
        self.units = units
        self.show_grid = show_grid
        self.center = center
        self._layers: OrderedDict[str, Layer] = OrderedDict()

    @property
    def x_range(self) -> tuple:
        """(xmin, xmax) in drawing coordinates."""
        if self.center:
            return (-self.width / 2, self.width / 2)
        return (0, self.width)

    @property
    def y_range(self) -> tuple:
        """(ymin, ymax) in drawing coordinates."""
        if self.center:
            return (-self.height / 2, self.height / 2)
        return (0, self.height)

    @property
    def bounds_polygon(self) -> np.ndarray:
        """Page boundary as a closed polygon (for clipping)."""
        x0, x1 = self.x_range
        y0, y1 = self.y_range
        return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]],
                        dtype=np.float64)

    def layer(self, name: str, guide: bool = False, **style_kwargs) -> Layer:
        """Get or create a named layer. Returns the Layer for chaining.

        Parameters
        ----------
        name : str
            Layer name (identity).
        guide : bool
            If True, this layer is a guide/overlay — displayed in show()
            and notebook preview but excluded from save(). Use for reference
            grids, flow field arrows, construction lines, etc.
        **style_kwargs
            color, linewidth, alpha for LayerStyle.
        """
        if name not in self._layers:
            self._layers[name] = Layer(name, guide=guide, **style_kwargs)
        elif style_kwargs or guide:
            layer = self._layers[name]
            if guide:
                layer.guide = True
            for k, v in style_kwargs.items():
                setattr(layer.style, k, v)
        return self._layers[name]

    @property
    def layers(self) -> List[Layer]:
        """Ordered list of all layers (including guides)."""
        return list(self._layers.values())

    @property
    def output_layers(self) -> List[Layer]:
        """Ordered list of non-guide layers (for save/export)."""
        return [l for l in self._layers.values() if not l.guide]

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

    def save(self, path: str, provenance: bool = True, params: dict = None,
             include_guides: bool = False, **kwargs):
        """Save as SVG, with optional provenance (source code + metadata).

        Parameters
        ----------
        path : str
            Output SVG path (e.g. 'output/piece.svg').
        provenance : bool
            If True (default), also saves {base}_provenance.json and
            {base}_source.py alongside the SVG.
        params : dict, optional
            User parameters to record in provenance (seeds, densities, etc.).
        include_guides : bool
            If True, also export guide layers. Default False (guides are
            display-only).
        """
        from penpal.io.svg_write import save_drawing
        save_drawing(self, path, include_guides=include_guides, **kwargs)

        if provenance:
            from penpal.io.provenance import save_provenance
            svg_path = path if path.endswith(".svg") else path + ".svg"
            save_provenance(self, svg_path, params=params)

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
