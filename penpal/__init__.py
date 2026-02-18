"""penpal — Unified plotter art library."""

from penpal.core.drawing import Drawing
from penpal.core.layer import Layer, LayerStyle
from penpal.core.paths import Paths
from penpal.core.types import Lines, Polyline
from penpal.core.transforms import (
    rotate, reflect, translate, scale,
    rotate_x, rotate_y, rotate_z, rotate_axis, translate3d, scale3d,
    apply,
)

# Submodules available as penpal.gen, penpal.io, etc.
from penpal import gen

__version__ = "0.1.0"
