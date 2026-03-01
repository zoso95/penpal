"""Sketch rendering — curvature-driven hatching from 3D meshes."""

from __future__ import annotations

from typing import List, Literal

import numpy as np

from penpal.core.drawing import Drawing
from penpal.core.paths import Paths
from penpal.core.types import Lines
from penpal.render3d.camera import Camera
from penpal.render3d.lighting import Light, compute_face_intensities
from penpal.render3d.project import project_points, viewport_map
from penpal.render3d.shapes import Face3D, Mesh3D, TextureSpec, Wireframe
from penpal.render3d.scene import Scene
from penpal.render3d.mesh_ops import (
    triangulate_mesh, weld_vertices, compute_face_normals,
    compute_curvature_directions, extract_silhouette_edges,
)


def _curvature_angle_in_face_frame(face: Face3D, curv_dir: np.ndarray) -> float:
    """Project a 3D curvature direction into the face's local 2D frame.

    Returns angle in degrees matching the convention used by
    Face3D.generate_texture_lines().
    """
    verts = face.vertices
    u_axis = verts[1] - verts[0]
    u_len = np.linalg.norm(u_axis)
    if u_len < 1e-12:
        return 45.0
    u_axis = u_axis / u_len

    face_normal = face.normal()
    v_axis = np.cross(face_normal, u_axis)
    v_len = np.linalg.norm(v_axis)
    if v_len < 1e-12:
        return 45.0
    v_axis = v_axis / v_len

    proj_u = np.dot(curv_dir, u_axis)
    proj_v = np.dot(curv_dir, v_axis)

    return np.degrees(np.arctan2(proj_v, proj_u))


def _average_face_size(mesh: Mesh3D) -> float:
    """Estimate average triangle diagonal length."""
    diags = []
    sample = mesh.faces[::max(1, len(mesh.faces) // 200)]
    for face in sample:
        v = face.vertices
        extent = v.max(axis=0) - v.min(axis=0)
        diags.append(np.sqrt((extent**2).sum()))
    return float(np.median(diags)) if diags else 1.0


def sketch_render(
    mesh: Mesh3D,
    camera: Camera,
    lights: List[Light],
    width: float = 8,
    height: float = 8,
    density: float = 1.0,
    ambient: float = 0.1,
    outline: bool = True,
    style: str = 'hatch',
    margin: float = 0.5,
    center: bool = False,
    max_faces_hlr: int = 5000,
    **kwargs,
) -> Drawing:
    """Render a 3D mesh as sketch-like line art with curvature-driven hatching.

    Hatching direction follows the surface curvature; density is driven
    by lighting (dense in shadow, sparse in highlights).

    Parameters
    ----------
    mesh : Mesh3D
        The 3D model.
    camera : Camera
        Viewpoint.
    lights : list of Light
        Scene lighting.
    width, height : float
        Drawing dimensions in inches.
    density : float
        Hatching density multiplier. 1.0 = default (auto-scaled to mesh).
        Higher = denser lines, lower = sparser.
    ambient : float
        Ambient light level [0, 1].
    outline : bool
        Add bold silhouette edges.
    style : str
        'hatch' or 'crosshatch'.
    margin : float
        Drawing margin.
    center : bool
        Center the drawing coordinate system.
    max_faces_hlr : int
        Skip hidden line removal above this face count.

    Returns
    -------
    Drawing with 'hatch' and optionally 'outline' layers.
    """
    # --- Triangulate non-triangle faces (e.g. quads from Mesh3D.box()) ---
    mesh = triangulate_mesh(mesh)
    n_faces = len(mesh.faces)

    # --- Auto-compute spacing from mesh geometry ---
    avg_size = _average_face_size(mesh)
    # Scale spacing to face size: dense in shadow, sparse in highlights
    min_spacing = avg_size / (8.0 * density)   # ~8 lines per face at darkest
    max_spacing = avg_size / (1.2 * density)   # ~1.2 lines per face at brightest

    # --- Mesh processing ---
    verts, faces_idx, adjacency = weld_vertices(mesh)
    face_normals = compute_face_normals(mesh)

    # --- Curvature directions ---
    curv_dirs = compute_curvature_directions(
        faces_idx, face_normals, mesh, adjacency
    )

    # --- Lighting ---
    intensities = compute_face_intensities(mesh.faces, lights, ambient=ambient)

    # --- Build faces with curvature-driven TextureSpec ---
    shaded_faces = []
    for i, face in enumerate(mesh.faces):
        intensity = intensities[i]
        spacing = min_spacing + (max_spacing - min_spacing) * intensity

        angle = _curvature_angle_in_face_frame(face, curv_dirs[i])

        tex = TextureSpec(
            style=style,
            angle=angle,
            spacing=spacing,
            draw_boundary=False,
        )
        shaded_faces.append(Face3D(face.vertices, texture=tex, layer='hatch'))

    # --- Render via Scene ---
    scene = Scene(shaded_faces)
    use_hlr = n_faces <= max_faces_hlr
    drawing = scene.render(
        camera,
        width=width,
        height=height,
        center=center,
        margin=margin,
        cull_backfaces=True,
        hidden_lines='remove' if use_hlr else 'show',
    )

    # --- Post-process: collapse nearby line endpoints into flowing strokes ---
    # The viewport diagonal gives us a reference scale for collapse threshold
    vp_diag = np.sqrt((width - 2 * margin)**2 + (height - 2 * margin)**2)
    collapse_threshold = vp_diag * 0.003  # merge endpoints within ~0.3% of viewport

    hatch_layer = drawing.layer('hatch')
    if hatch_layer.paths.lines:
        hatch_layer.paths = hatch_layer.paths.collapse(collapse_threshold)

    # --- Silhouette edges ---
    if outline:
        silhouette_3d = extract_silhouette_edges(
            mesh, faces_idx, face_normals, adjacency,
            camera.position,
        )
        if silhouette_3d:
            mvp = camera.vp_matrix
            if center:
                vp_x0 = -width / 2 + margin
                vp_y0 = -height / 2 + margin
            else:
                vp_x0 = margin
                vp_y0 = margin
            vp_w = width - 2 * margin
            vp_h = height - 2 * margin

            silhouette_2d = []
            for seg_3d in silhouette_3d:
                ndc = project_points(seg_3d[:, :3], mvp)
                screen = viewport_map(ndc, vp_x0, vp_y0, vp_w, vp_h)
                silhouette_2d.append(screen)

            if silhouette_2d:
                # Collapse silhouette segments into continuous contours
                sil_paths = Paths(silhouette_2d).collapse(collapse_threshold)
                drawing.layer('outline').add(sil_paths)

    return drawing
