"""penpal — Unified plotter art library."""

from penpal.core.drawing import Drawing, pen_width
from penpal.core.layer import Layer, LayerStyle
from penpal.core.paths import Paths
from penpal.core.mesh import Mesh
from penpal.core import noise
from penpal.core.types import Lines, Polyline
from penpal.core.transforms import (
    rotate, reflect, translate, scale,
    rotate_x, rotate_y, rotate_z, rotate_axis, translate3d, scale3d,
    apply,
)

# Submodules available as penpal.gen, penpal.sampling, penpal.shading, etc.
from penpal import gen
from penpal import sampling
from penpal import shading
from penpal import symmetry
from penpal import render3d
from penpal import cv
from penpal import effects

__version__ = "0.1.0"
