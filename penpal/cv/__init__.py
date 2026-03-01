"""Computer vision pipeline — photo to plotter line art."""

from penpal.cv.image import load, smooth, resize, gamma_correct, map_to_drawing
from penpal.cv.halftone import (
    crosshatch, line_scan, edges, morphological_halftone,
    dot_grid, dot_grid_cmyk, mezzotint, voronoi_stipple, spiral_portrait,
)
from penpal.cv import dither
from penpal.cv import texture
from penpal.cv import datasets
