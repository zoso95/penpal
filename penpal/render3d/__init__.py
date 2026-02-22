"""3D rendering pipeline for penpal.

Renders 3D shapes with hatching textures to 2D line art,
with proper hidden line removal for plotter output.
"""

from penpal.render3d.camera import Camera
from penpal.render3d.scene import Scene
from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec, Wireframe

__all__ = ['Camera', 'Scene', 'Face3D', 'Mesh3D', 'TextureSpec', 'Wireframe']
