"""Line processing operations: optimize, filter, collapse, subsample, etc.

All functions accept and return Lines (List[np.ndarray]).
"""

from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import KDTree

from penpal.core.types import Lines


def optimize(lines: Lines) -> Lines:
    """Reorder lines to minimize pen-lift travel (nearest-neighbor heuristic).

    Considers both endpoints of each line, reversing as needed.
    """
    if len(lines) <= 1:
        return lines

    remaining = list(range(len(lines)))
    result = [remaining.pop(0)]
    current_end = lines[result[0]][-1]

    while remaining:
        best_idx = None
        best_dist = float("inf")
        best_reverse = False

        for i in remaining:
            d_start = np.sum((lines[i][0] - current_end) ** 2)
            d_end = np.sum((lines[i][-1] - current_end) ** 2)
            if d_start < best_dist:
                best_dist = d_start
                best_idx = i
                best_reverse = False
            if d_end < best_dist:
                best_dist = d_end
                best_idx = i
                best_reverse = True

        remaining.remove(best_idx)
        line = lines[best_idx]
        if best_reverse:
            line = line[::-1]
        result.append(best_idx)
        current_end = line[-1]

    optimized = []
    current_end = lines[result[0]][-1]
    optimized.append(lines[result[0]])
    for idx in result[1:]:
        line = lines[idx]
        d_start = np.sum((line[0] - current_end) ** 2)
        d_end = np.sum((line[-1] - current_end) ** 2)
        if d_end < d_start:
            line = line[::-1]
        optimized.append(line)
        current_end = line[-1]
    return optimized


def filter_short(lines: Lines, min_length: float) -> Lines:
    """Remove lines shorter than min_length (total arc length)."""
    result = []
    for line in lines:
        if len(line) < 2:
            continue
        diffs = np.diff(line, axis=0)
        length = np.sum(np.sqrt(np.sum(diffs**2, axis=1)))
        if length >= min_length:
            result.append(line)
    return result


def collapse(lines: Lines, threshold: float) -> Lines:
    """Merge nearby endpoints: if the end of one line is within threshold
    of the start of the next, join them into a single polyline."""
    if len(lines) <= 1:
        return list(lines)

    result = [lines[0].copy()]
    for line in lines[1:]:
        dist = np.linalg.norm(result[-1][-1] - line[0])
        if dist <= threshold:
            result[-1] = np.vstack([result[-1], line[1:]])
        else:
            result.append(line.copy())
    return result


def subsample(lines: Lines, n: int = None, frac: float = None) -> Lines:
    """Subsample points from each polyline.

    Either keep every nth point (n=...) or keep a fraction (frac=...).
    Always keeps first and last point.
    """
    result = []
    for line in lines:
        if len(line) <= 2:
            result.append(line)
            continue
        if n is not None:
            indices = list(range(0, len(line), n))
        elif frac is not None:
            step = max(1, int(1.0 / frac))
            indices = list(range(0, len(line), step))
        else:
            result.append(line)
            continue
        if indices[-1] != len(line) - 1:
            indices.append(len(line) - 1)
        result.append(line[indices])
    return result


def every_nth(lines: Lines, n: int) -> Lines:
    """Keep only every nth line from the collection."""
    return lines[::n]


def merge_nearby(lines: Lines, threshold: float) -> Lines:
    """Merge lines whose endpoints are within threshold distance."""
    if not lines:
        return []
    result = [l.copy() for l in lines]
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(result):
            j = i + 1
            while j < len(result):
                d = np.linalg.norm(result[i][-1] - result[j][0])
                if d <= threshold:
                    result[i] = np.vstack([result[i], result[j][1:]])
                    result.pop(j)
                    changed = True
                else:
                    j += 1
            i += 1
    return result


def resample_polyline(line: np.ndarray, num_points: int) -> np.ndarray:
    """Resample a polyline to have exactly num_points evenly spaced points."""
    if len(line) < 2:
        return line
    diffs = np.diff(line, axis=0)
    seg_lengths = np.sqrt(np.sum(diffs**2, axis=1))
    cumulative = np.concatenate([[0], np.cumsum(seg_lengths)])
    total = cumulative[-1]
    if total == 0:
        return np.tile(line[0], (num_points, 1))

    target_dists = np.linspace(0, total, num_points)
    result = np.zeros((num_points, line.shape[1]), dtype=np.float64)
    for i, d in enumerate(target_dists):
        idx = np.searchsorted(cumulative, d, side="right") - 1
        idx = min(idx, len(line) - 2)
        seg_len = seg_lengths[idx]
        if seg_len == 0:
            result[i] = line[idx]
        else:
            t = (d - cumulative[idx]) / seg_len
            result[i] = line[idx] + t * (line[idx + 1] - line[idx])
    return result
