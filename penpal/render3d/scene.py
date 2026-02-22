"""Scene — 3D-to-2D rendering pipeline with hidden line removal.

Usage:
    scene = Scene()
    scene.add(Mesh3D.box())
    scene.add(Wireframe([...], layer='axes'))
    cam = Camera.orbit(distance=5, azimuth=30, elevation=30)
    drawing = scene.render(cam)
"""

from __future__ import annotations

from typing import List, Literal

import numpy as np

from penpal.core.drawing import Drawing
from penpal.core.geo import clip_away
from penpal.core.types import Lines
from penpal.render3d.camera import Camera
from penpal.render3d.project import project_points, viewport_map
from penpal.render3d.shapes import Face3D, Mesh3D, Wireframe


class Scene:
    """A collection of 3D objects to render.

    Parameters
    ----------
    objects : list, optional
        Initial objects (Face3D, Mesh3D, Wireframe).
    """

    def __init__(self, objects=None):
        self._objects: list = list(objects) if objects else []

    def add(self, obj) -> Scene:
        """Add an object. Returns self for chaining."""
        self._objects.append(obj)
        return self

    def render(self, camera: Camera, width: float = 8, height: float = 8,
               center: bool = False, margin: float = 0.5,
               cull_backfaces: bool = True,
               hidden_lines: Literal['remove', 'show'] = 'remove') -> Drawing:
        """Render the scene to a 2D Drawing.

        Parameters
        ----------
        camera : Camera
        width, height : float
            Drawing dimensions in inches.
        center : bool
            Center the drawing coordinate system.
        margin : float
            Margin on each side (reserved space).
        cull_backfaces : bool
            Discard faces pointing away from camera.
        hidden_lines : 'remove' or 'show'
            'remove' = clip occluded lines (default).
            'show' = render all lines (debug mode).

        Returns
        -------
        Drawing
        """
        drawing = Drawing(width, height, center=center)

        # Drawable area
        if center:
            vp_x0 = -width / 2 + margin
            vp_y0 = -height / 2 + margin
        else:
            vp_x0 = margin
            vp_y0 = margin
        vp_w = width - 2 * margin
        vp_h = height - 2 * margin

        mvp = camera.vp_matrix
        cam_pos = camera.position

        # --- 1. Flatten objects ---
        faces: List[Face3D] = []
        wireframes: List[Wireframe] = []

        for obj in self._objects:
            if isinstance(obj, Mesh3D):
                faces.extend(obj.faces)
            elif isinstance(obj, Face3D):
                faces.append(obj)
            elif isinstance(obj, Wireframe):
                wireframes.append(obj)

        # --- 2. Back-face cull ---
        visible_faces: List[Face3D] = []
        for face in faces:
            to_cam = cam_pos - face.centroid()
            if not cull_backfaces or np.dot(face.normal(), to_cam) > 0:
                visible_faces.append(face)

        # --- 3. Generate 3D texture lines + project to 2D ---
        # For each face: its projected 2D lines and its projected 2D polygon
        face_data = []
        for face in visible_faces:
            # 3D lines (hatching + boundary)
            lines_3d = face.generate_texture_lines()

            # Project lines to 2D viewport
            lines_2d = []
            for pts_3d in lines_3d:
                if len(pts_3d) < 2:
                    continue
                ndc = project_points(pts_3d[:, :3], mvp)
                screen = viewport_map(ndc, vp_x0, vp_y0, vp_w, vp_h)
                lines_2d.append(screen)

            # Project face polygon to 2D (for occlusion)
            ndc_poly = project_points(face.vertices[:, :3], mvp)
            screen_poly = viewport_map(ndc_poly, vp_x0, vp_y0, vp_w, vp_h)
            # Close polygon
            if not np.allclose(screen_poly[0], screen_poly[-1]):
                screen_poly = np.vstack([screen_poly, screen_poly[0:1]])

            # Depth for sorting (camera-space Z of centroid)
            centroid = face.centroid()
            centroid_h = np.append(centroid, 1.0)
            cam_space = camera.view_matrix @ centroid_h
            depth = cam_space[2]  # more negative = further away

            face_data.append({
                'lines_2d': lines_2d,
                'polygon_2d': screen_poly,
                'depth': depth,
                'layer': face.layer,
            })

        # --- 4. Sort front-to-back (closest first = least negative Z) ---
        face_data.sort(key=lambda d: d['depth'], reverse=True)

        # --- 5. Hidden line removal ---
        occlusion_polygons: List[np.ndarray] = []

        for fd in face_data:
            visible_lines = fd['lines_2d']

            if hidden_lines == 'remove' and visible_lines:
                for occluder in occlusion_polygons:
                    visible_lines = clip_away(visible_lines, occluder)
                    if not visible_lines:
                        break

            # Add to drawing
            if visible_lines:
                drawing.layer(fd['layer']).add(visible_lines)

            # Add this face's polygon to occlusion set
            occlusion_polygons.append(fd['polygon_2d'])

        # --- 6. Wireframes ---
        for wf in wireframes:
            lines_2d = []
            for pts_3d in wf.lines:
                if len(pts_3d) < 2:
                    continue
                ndc = project_points(pts_3d[:, :3], mvp)
                screen = viewport_map(ndc, vp_x0, vp_y0, vp_w, vp_h)
                lines_2d.append(screen)

            if hidden_lines == 'remove' and lines_2d:
                for occluder in occlusion_polygons:
                    lines_2d = clip_away(lines_2d, occluder)
                    if not lines_2d:
                        break

            if lines_2d:
                drawing.layer(wf.layer).add(lines_2d)

        return drawing

    def __repr__(self):
        counts = {}
        for obj in self._objects:
            name = type(obj).__name__
            counts[name] = counts.get(name, 0) + 1
        parts = [f"{v} {k}" for k, v in counts.items()]
        return f"Scene({', '.join(parts) or 'empty'})"
