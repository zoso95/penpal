"""3D rendering pipeline for penpal.

Renders 3D shapes with hatching textures to 2D line art,
with proper hidden line removal for plotter output.
"""

from penpal.render3d.camera import Camera
from penpal.render3d.scene import Scene
from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec, Wireframe
from penpal.render3d.lighting import DirectionalLight, PointLight
from penpal.render3d.loader import load_stl
from penpal.render3d.sketch import sketch_render

__all__ = [
    'Camera', 'Scene', 'Face3D', 'Mesh3D', 'TextureSpec', 'Wireframe',
    'DirectionalLight', 'PointLight', 'load_stl', 'sketch_render',
]
