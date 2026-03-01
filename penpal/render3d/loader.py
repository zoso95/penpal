"""STL file loader — parse binary and ASCII STL into Mesh3D."""

from __future__ import annotations

import struct

import numpy as np

from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec


def _is_ascii_stl(path: str) -> bool:
    """Detect whether an STL file is ASCII format."""
    try:
        with open(path, 'rb') as f:
            head = f.read(256)
        text = head.decode('ascii', errors='ignore')
        return text.strip().startswith('solid') and 'facet' in text
    except Exception:
        return False


def _load_binary_stl(path: str, layer: str, max_faces: int = None) -> Mesh3D:
    """Parse binary STL format using vectorized numpy reads."""
    with open(path, 'rb') as f:
        f.read(80)  # header
        count = struct.unpack('<I', f.read(4))[0]
        data = f.read()

    dt = np.dtype([
        ('normal', '<f4', (3,)),
        ('vertices', '<f4', (3, 3)),
        ('attr', '<u2'),
    ])
    triangles = np.frombuffer(data, dtype=dt, count=count)

    # Decimate during parsing if needed
    if max_faces is not None and count > max_faces:
        step = max(1, count // max_faces)
        triangles = triangles[::step]

    all_verts = triangles['vertices'].astype(np.float64)
    all_normals = triangles['normal'].astype(np.float64)

    texture = TextureSpec(style='none', draw_boundary=False)
    faces = []
    for i in range(len(triangles)):
        verts = all_verts[i]
        face = Face3D(verts, texture=texture, layer=layer)

        stl_n = all_normals[i]
        if np.linalg.norm(stl_n) > 0.1:
            computed_n = face.normal()
            if np.dot(stl_n, computed_n) < 0:
                face = Face3D(verts[::-1], texture=texture, layer=layer)
        faces.append(face)

    return Mesh3D(faces)


def _load_ascii_stl(path: str, layer: str, max_faces: int = None) -> Mesh3D:
    """Parse ASCII STL format."""
    texture = TextureSpec(style='none', draw_boundary=False)
    faces = []
    tri_count = 0

    # Compute step for decimation
    step = 1

    with open(path, 'r') as f:
        verts = []
        stl_normal = None

        for line in f:
            line = line.strip()
            if line.startswith('facet normal'):
                parts = line.split()
                stl_normal = np.array([float(parts[2]), float(parts[3]),
                                       float(parts[4])], dtype=np.float64)
                verts = []
            elif line.startswith('vertex'):
                parts = line.split()
                verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('endfacet'):
                tri_count += 1
                if max_faces is not None and tri_count % step != 0:
                    continue
                if len(verts) == 3:
                    v = np.array(verts, dtype=np.float64)
                    face = Face3D(v, texture=texture, layer=layer)
                    if stl_normal is not None and np.linalg.norm(stl_normal) > 0.1:
                        if np.dot(stl_normal, face.normal()) < 0:
                            face = Face3D(v[::-1], texture=texture, layer=layer)
                    faces.append(face)
                    if max_faces is not None and len(faces) >= max_faces:
                        break

    return Mesh3D(faces)


def load_stl(path: str, layer: str = 'default',
             max_faces: int = None) -> Mesh3D:
    """Load an STL file (binary or ASCII) into a Mesh3D.

    Parameters
    ----------
    path : str
        Path to the .stl file.
    layer : str
        Layer name assigned to all faces.
    max_faces : int, optional
        If set, decimate the mesh during loading to at most this many faces.
        Much faster than loading the full mesh for large STL files.

    Returns
    -------
    Mesh3D
    """
    if _is_ascii_stl(path):
        return _load_ascii_stl(path, layer, max_faces)
    return _load_binary_stl(path, layer, max_faces)
