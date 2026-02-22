"""3D shape primitives for the render pipeline.

Face3D: a planar polygon with optional hatching texture.
Mesh3D: a collection of Face3D objects.
Wireframe: 3D line segments (no faces, no culling).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from penpal.core.types import Lines


@dataclass
class TextureSpec:
    """Specification for face hatching texture.

    Parameters
    ----------
    style : str
        'hatch', 'crosshatch', or 'none'.
    angle : float
        Hatch angle in degrees (in face-local 2D space).
    spacing : float
        Distance between hatch lines in face-local units.
    density : int, optional
        If set, overrides spacing with N lines across the face.
    draw_boundary : bool
        Whether to include the face boundary polygon.
    """
    style: str = 'hatch'
    angle: float = 45
    spacing: float = 0.1
    density: Optional[int] = None
    draw_boundary: bool = True


class Face3D:
    """A planar 3D polygon with optional hatching texture.

    Parameters
    ----------
    vertices : (N, 3) array
        Polygon vertices in 3D. CCW winding when viewed from outside = front face.
    texture : TextureSpec or None
        How to fill the face. None = boundary only.
    layer : str
        Layer name for rendered output.
    """

    def __init__(self, vertices, texture: TextureSpec = None,
                 layer: str = 'default'):
        self.vertices = np.asarray(vertices, dtype=np.float64)
        assert self.vertices.ndim == 2 and self.vertices.shape[1] == 3
        self.texture = texture if texture is not None else TextureSpec()
        self.layer = layer

    def normal(self) -> np.ndarray:
        """Outward face normal (unit vector) from CCW winding."""
        v0 = self.vertices[1] - self.vertices[0]
        v1 = self.vertices[2] - self.vertices[0]
        n = np.cross(v0, v1)
        norm = np.linalg.norm(n)
        if norm < 1e-12:
            return np.array([0.0, 0.0, 1.0])
        return n / norm

    def centroid(self) -> np.ndarray:
        """Average of vertices (used for depth sorting)."""
        return self.vertices.mean(axis=0)

    def generate_texture_lines(self) -> Lines:
        """Generate hatching in the face's local 2D plane, map back to 3D.

        1. Build local 2D coordinate frame on the face plane
        2. Project face vertices to local 2D
        3. Generate hatch lines using existing shading functions
        4. Map hatch lines back to 3D world space
        """
        from penpal.shading.hatch import hatch_polygon, shade_polygon

        verts = self.vertices
        n = len(verts)
        if n < 3:
            return []

        # Local coordinate frame
        origin = verts[0].copy()
        u_axis = verts[1] - verts[0]
        u_len = np.linalg.norm(u_axis)
        if u_len < 1e-12:
            return []
        u_axis = u_axis / u_len

        face_normal = self.normal()
        v_axis = np.cross(face_normal, u_axis)
        v_len = np.linalg.norm(v_axis)
        if v_len < 1e-12:
            return []
        v_axis = v_axis / v_len

        # Project vertices to local 2D
        local_2d = np.zeros((n, 2), dtype=np.float64)
        for i in range(n):
            d = verts[i] - origin
            local_2d[i, 0] = np.dot(d, u_axis)
            local_2d[i, 1] = np.dot(d, v_axis)

        # Close polygon
        if not np.allclose(local_2d[0], local_2d[-1]):
            local_2d_closed = np.vstack([local_2d, local_2d[0:1]])
        else:
            local_2d_closed = local_2d

        # Generate 2D hatching
        tex = self.texture
        lines_2d = []

        if tex.style == 'none':
            pass
        elif tex.style == 'crosshatch':
            p1 = hatch_polygon(local_2d_closed, angle=tex.angle, spacing=tex.spacing)
            p2 = hatch_polygon(local_2d_closed, angle=tex.angle + 90, spacing=tex.spacing)
            lines_2d = p1.lines + p2.lines
        else:  # 'hatch'
            if tex.density is not None:
                p = shade_polygon(local_2d_closed, density=tex.density, angle=tex.angle)
            else:
                p = hatch_polygon(local_2d_closed, angle=tex.angle, spacing=tex.spacing)
            lines_2d = p.lines

        # Add boundary
        if tex.draw_boundary:
            lines_2d.append(local_2d_closed.copy())

        # Map 2D back to 3D
        lines_3d = []
        for line_2d in lines_2d:
            pts_3d = (origin[np.newaxis, :]
                      + line_2d[:, 0:1] * u_axis[np.newaxis, :]
                      + line_2d[:, 1:2] * v_axis[np.newaxis, :])
            lines_3d.append(pts_3d)

        return lines_3d

    def transform(self, matrix: np.ndarray) -> Face3D:
        """Apply a 4x4 transform. Returns new Face3D."""
        from penpal.core.transforms import apply as apply_transform
        new_verts = apply_transform(matrix, [self.vertices])[0]
        return Face3D(new_verts, texture=self.texture, layer=self.layer)


class Wireframe:
    """3D line segments — no faces, no culling, no texture.

    Parameters
    ----------
    lines : list of (N_i, 3) arrays
    layer : str
    """

    def __init__(self, lines: Lines, layer: str = 'default'):
        self.lines = [np.asarray(l, dtype=np.float64) for l in lines]
        self.layer = layer

    def transform(self, matrix: np.ndarray) -> Wireframe:
        from penpal.core.transforms import apply as apply_transform
        return Wireframe(apply_transform(matrix, self.lines), layer=self.layer)


class Mesh3D:
    """A collection of Face3D objects forming a mesh.

    Parameters
    ----------
    faces : list of Face3D
    """

    def __init__(self, faces: List[Face3D] = None):
        self.faces = list(faces) if faces else []

    def transform(self, matrix: np.ndarray) -> Mesh3D:
        return Mesh3D([f.transform(matrix) for f in self.faces])

    @classmethod
    def box(cls, size=1.0, center=(0, 0, 0),
            texture: TextureSpec = None,
            face_textures: dict = None,
            face_layers: dict = None) -> Mesh3D:
        """Axis-aligned box.

        Parameters
        ----------
        size : float or (sx, sy, sz)
        center : (3,)
        texture : TextureSpec, default for all faces
        face_textures : dict mapping face name to TextureSpec
        face_layers : dict mapping face name to layer name
            Face names: 'front', 'back', 'left', 'right', 'top', 'bottom'
        """
        if isinstance(size, (int, float)):
            sx = sy = sz = float(size)
        else:
            sx, sy, sz = size

        cx, cy, cz = center
        hx, hy, hz = sx / 2, sy / 2, sz / 2

        if texture is None:
            texture = TextureSpec()
        if face_textures is None:
            face_textures = {}
        if face_layers is None:
            face_layers = {}

        v = np.array([
            [cx - hx, cy + hy, cz + hz],  # 0: front top left
            [cx + hx, cy + hy, cz + hz],  # 1: front top right
            [cx + hx, cy - hy, cz + hz],  # 2: front bottom right
            [cx - hx, cy - hy, cz + hz],  # 3: front bottom left
            [cx - hx, cy + hy, cz - hz],  # 4: back top left
            [cx + hx, cy + hy, cz - hz],  # 5: back top right
            [cx + hx, cy - hy, cz - hz],  # 6: back bottom right
            [cx - hx, cy - hy, cz - hz],  # 7: back bottom left
        ], dtype=np.float64)

        # CCW winding for outward normals
        face_defs = {
            'front':  [3, 2, 1, 0],
            'back':   [6, 7, 4, 5],
            'right':  [2, 6, 5, 1],
            'left':   [7, 3, 0, 4],
            'top':    [0, 1, 5, 4],
            'bottom': [7, 6, 2, 3],
        }

        faces = []
        for name, indices in face_defs.items():
            tex = face_textures.get(name, texture)
            lay = face_layers.get(name, 'default')
            faces.append(Face3D(v[indices], texture=tex, layer=lay))

        return cls(faces)

    @classmethod
    def plane(cls, width: float = 2.0, depth: float = 2.0,
              center=(0, 0, 0), normal_axis: str = 'y',
              texture: TextureSpec = None, layer: str = 'default') -> Mesh3D:
        """A single rectangular face.

        Parameters
        ----------
        width, depth : float
        center : (3,)
        normal_axis : 'x', 'y', or 'z'
        """
        cx, cy, cz = center
        hw, hd = width / 2, depth / 2

        if normal_axis == 'y':
            verts = np.array([
                [cx - hw, cy, cz + hd],
                [cx + hw, cy, cz + hd],
                [cx + hw, cy, cz - hd],
                [cx - hw, cy, cz - hd],
            ], dtype=np.float64)
        elif normal_axis == 'z':
            verts = np.array([
                [cx - hw, cy - hd, cz],
                [cx + hw, cy - hd, cz],
                [cx + hw, cy + hd, cz],
                [cx - hw, cy + hd, cz],
            ], dtype=np.float64)
        elif normal_axis == 'x':
            verts = np.array([
                [cx, cy - hw, cz - hd],
                [cx, cy + hw, cz - hd],
                [cx, cy + hw, cz + hd],
                [cx, cy - hw, cz + hd],
            ], dtype=np.float64)
        else:
            raise ValueError(f"normal_axis must be 'x', 'y', or 'z', got {normal_axis!r}")

        if texture is None:
            texture = TextureSpec()

        return cls([Face3D(verts, texture=texture, layer=layer)])

    def __repr__(self):
        return f"Mesh3D({len(self.faces)} faces)"
