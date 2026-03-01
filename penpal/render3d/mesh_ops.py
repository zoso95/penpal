"""Mesh processing — vertex welding, curvature estimation, silhouette extraction."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

from penpal.render3d.shapes import Face3D, Mesh3D
from penpal.core.types import Lines


def triangulate_mesh(mesh: Mesh3D) -> Mesh3D:
    """Convert all faces to triangles via fan triangulation."""
    tri_faces = []
    for face in mesh.faces:
        n = len(face.vertices)
        if n == 3:
            tri_faces.append(face)
        elif n > 3:
            # Fan triangulation from vertex 0
            for i in range(1, n - 1):
                verts = np.array([face.vertices[0], face.vertices[i],
                                  face.vertices[i + 1]], dtype=np.float64)
                tri_faces.append(Face3D(verts, texture=face.texture,
                                        layer=face.layer))
    return Mesh3D(tri_faces)


def weld_vertices(
    mesh: Mesh3D, tolerance: float = 1e-6,
) -> Tuple[np.ndarray, np.ndarray, Dict[Tuple[int, int], List[int]]]:
    """Merge coincident vertices from triangle soup.

    Parameters
    ----------
    mesh : Mesh3D
        Input mesh (must be triangulated — use triangulate_mesh() first).
    tolerance : float
        Distance below which vertices are considered identical.

    Returns
    -------
    verts : (V, 3) unique vertices
    faces_idx : (F, 3) int array — triangle indices into verts
    adjacency : dict mapping sorted edge tuple (vi, vj) → list of face indices
    """
    # Collect all vertices
    all_verts = []
    for face in mesh.faces:
        for v in face.vertices:
            all_verts.append(v)
    all_verts = np.array(all_verts, dtype=np.float64)

    # Quantize for hashing
    scale = 1.0 / tolerance if tolerance > 0 else 1e6
    quantized = np.round(all_verts * scale).astype(np.int64)

    # Map quantized coords → unique index
    vertex_map: Dict[tuple, int] = {}
    unique_verts = []
    index_remap = np.zeros(len(all_verts), dtype=np.int64)

    for i in range(len(all_verts)):
        key = tuple(quantized[i])
        if key not in vertex_map:
            vertex_map[key] = len(unique_verts)
            unique_verts.append(all_verts[i])
        index_remap[i] = vertex_map[key]

    verts = np.array(unique_verts, dtype=np.float64)

    # Build face index array
    n_faces = len(mesh.faces)
    faces_idx = np.zeros((n_faces, 3), dtype=np.int64)
    for fi, face in enumerate(mesh.faces):
        base = fi * 3
        for vi in range(3):
            faces_idx[fi, vi] = index_remap[base + vi]

    # Build edge → face adjacency
    adjacency: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for fi in range(n_faces):
        v0, v1, v2 = faces_idx[fi]
        for a, b in [(v0, v1), (v1, v2), (v2, v0)]:
            edge = (min(a, b), max(a, b))
            adjacency[edge].append(fi)

    return verts, faces_idx, dict(adjacency)


def compute_face_normals(mesh: Mesh3D) -> np.ndarray:
    """Compute unit normal for each face.

    Returns
    -------
    (F, 3) unit normals.
    """
    normals = np.zeros((len(mesh.faces), 3), dtype=np.float64)
    for i, face in enumerate(mesh.faces):
        normals[i] = face.normal()
    return normals


def compute_vertex_normals(
    verts: np.ndarray,
    faces_idx: np.ndarray,
    face_normals: np.ndarray,
) -> np.ndarray:
    """Area-weighted average of incident face normals per vertex.

    Parameters
    ----------
    verts : (V, 3) unique vertices
    faces_idx : (F, 3) face vertex indices
    face_normals : (F, 3) unit face normals

    Returns
    -------
    (V, 3) unit vertex normals.
    """
    n_verts = len(verts)
    v_normals = np.zeros((n_verts, 3), dtype=np.float64)

    for fi in range(len(faces_idx)):
        v0, v1, v2 = faces_idx[fi]
        # Face area via cross product magnitude
        e1 = verts[v1] - verts[v0]
        e2 = verts[v2] - verts[v0]
        area = 0.5 * np.linalg.norm(np.cross(e1, e2))

        weighted_n = face_normals[fi] * area
        v_normals[v0] += weighted_n
        v_normals[v1] += weighted_n
        v_normals[v2] += weighted_n

    # Normalize
    norms = np.linalg.norm(v_normals, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return v_normals / norms


def compute_curvature_directions(
    faces_idx: np.ndarray,
    face_normals: np.ndarray,
    mesh: Mesh3D,
    adjacency: Dict[Tuple[int, int], List[int]],
) -> np.ndarray:
    """Estimate principal curvature direction per face via dihedral angles.

    For each face, examines shared edges with neighbors. The edge with
    the maximum dihedral angle (biggest normal change) indicates the
    direction of strongest bending. The curvature direction is
    perpendicular to that edge, in the face plane.

    Parameters
    ----------
    faces_idx : (F, 3) face vertex indices
    face_normals : (F, 3) unit face normals
    mesh : Mesh3D (for vertex positions)
    adjacency : edge → face list mapping

    Returns
    -------
    (F, 3) unit curvature direction vectors in world space.
    """
    n_faces = len(faces_idx)
    directions = np.zeros((n_faces, 3), dtype=np.float64)

    for fi in range(n_faces):
        verts = mesh.faces[fi].vertices
        v_idx = faces_idx[fi]
        n_face = face_normals[fi]

        best_angle = -1.0
        best_edge_vec = None

        # Check each of the 3 edges
        edges = [(0, 1), (1, 2), (2, 0)]
        for ei, ej in edges:
            a, b = int(v_idx[ei]), int(v_idx[ej])
            edge_key = (min(a, b), max(a, b))
            adj_faces = adjacency.get(edge_key, [])

            # Find the adjacent face (not this face)
            neighbor = None
            for fj in adj_faces:
                if fj != fi:
                    neighbor = fj
                    break

            if neighbor is None:
                continue

            # Dihedral angle between face normals
            n_neighbor = face_normals[neighbor]
            dot = np.clip(np.dot(n_face, n_neighbor), -1.0, 1.0)
            dihedral = np.arccos(dot)

            if dihedral > best_angle:
                best_angle = dihedral
                best_edge_vec = verts[ej] - verts[ei]

        if best_edge_vec is not None and np.linalg.norm(best_edge_vec) > 1e-12:
            # Curvature direction = perpendicular to edge, in face plane
            # = edge × face_normal (gives in-plane perpendicular)
            curv = np.cross(best_edge_vec, n_face)
            norm = np.linalg.norm(curv)
            if norm > 1e-12:
                directions[fi] = curv / norm
                continue

        # Fallback: use longest edge direction
        longest = 0.0
        for ei, ej in edges:
            e = verts[ej] - verts[ei]
            length = np.linalg.norm(e)
            if length > longest:
                longest = length
                directions[fi] = e / length

    return directions


def extract_silhouette_edges(
    mesh: Mesh3D,
    faces_idx: np.ndarray,
    face_normals: np.ndarray,
    adjacency: Dict[Tuple[int, int], List[int]],
    camera_position: np.ndarray,
) -> Lines:
    """Find silhouette edges — boundaries between front/back-facing faces.

    Parameters
    ----------
    mesh : Mesh3D
    faces_idx : (F, 3) vertex indices
    face_normals : (F, 3) unit normals
    adjacency : edge → face list mapping
    camera_position : (3,) camera world position

    Returns
    -------
    List of (2, 3) arrays — edge segments in 3D.
    """
    # Precompute front-facing status per face
    n_faces = len(mesh.faces)
    front_facing = np.zeros(n_faces, dtype=bool)
    for i, face in enumerate(mesh.faces):
        to_cam = camera_position - face.centroid()
        front_facing[i] = np.dot(face_normals[i], to_cam) > 0

    edges_out: Lines = []
    seen = set()

    for edge_key, face_list in adjacency.items():
        if edge_key in seen:
            continue
        seen.add(edge_key)

        vi, vj = edge_key

        if len(face_list) == 1:
            # Boundary edge — always a silhouette if front-facing
            fi = face_list[0]
            if front_facing[fi]:
                p0 = mesh.faces[fi].vertices
                # Find the actual vertex positions from the face
                idx0 = np.where(faces_idx[fi] == vi)[0]
                idx1 = np.where(faces_idx[fi] == vj)[0]
                if len(idx0) > 0 and len(idx1) > 0:
                    v0 = p0[idx0[0]]
                    v1 = p0[idx1[0]]
                    edges_out.append(np.array([v0, v1], dtype=np.float64))
        elif len(face_list) >= 2:
            # Shared edge — silhouette if one face is front, other is back
            fi, fj = face_list[0], face_list[1]
            if front_facing[fi] != front_facing[fj]:
                p0 = mesh.faces[fi].vertices
                idx0 = np.where(faces_idx[fi] == vi)[0]
                idx1 = np.where(faces_idx[fi] == vj)[0]
                if len(idx0) > 0 and len(idx1) > 0:
                    v0 = p0[idx0[0]]
                    v1 = p0[idx1[0]]
                    edges_out.append(np.array([v0, v1], dtype=np.float64))

    return edges_out
