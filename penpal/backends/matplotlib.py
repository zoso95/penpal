"""Matplotlib rendering backend for Drawing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

if TYPE_CHECKING:
    from penpal.core.drawing import Drawing


def render(drawing: Drawing, ax=None, figsize=None, grid=None, **kwargs):
    """Render a Drawing using matplotlib."""
    if figsize is None:
        figsize = (drawing.width, drawing.height)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.figure

    show_grid = grid if grid is not None else drawing.show_grid

    x0, x1 = drawing.x_range
    y0, y1 = drawing.y_range

    if show_grid:
        _draw_grid(ax, drawing)

    # Draw each layer
    for layer in drawing.layers:
        if not layer.lines:
            continue
        segments = [line[:, :2] for line in layer.lines]
        lc = LineCollection(
            segments,
            colors=layer.style.color,
            linewidths=layer.style.linewidth,
            alpha=layer.style.alpha,
            zorder=2,
        )
        ax.add_collection(lc)

    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xlabel(drawing.units)
    ax.set_ylabel(drawing.units)

    plt.tight_layout()
    return fig, ax


def _draw_grid(ax, drawing):
    """Draw reference grid lines."""
    x0, x1 = drawing.x_range
    y0, y1 = drawing.y_range

    for x in np.arange(np.ceil(x0), x1 + 0.01, 1):
        ax.axvline(x, color="#e0e0e0", linewidth=0.3, zorder=0)
    for y in np.arange(np.ceil(y0), y1 + 0.01, 1):
        ax.axhline(y, color="#e0e0e0", linewidth=0.3, zorder=0)
    for x in np.arange(np.ceil(x0 / 5) * 5, x1 + 0.01, 5):
        ax.axvline(x, color="#c0c0c0", linewidth=0.6, zorder=0)
    for y in np.arange(np.ceil(y0 / 5) * 5, y1 + 0.01, 5):
        ax.axhline(y, color="#c0c0c0", linewidth=0.6, zorder=0)

    # Origin crosshair if centered
    if drawing.center:
        ax.axhline(0, color="#aaaaaa", linewidth=0.8, zorder=0)
        ax.axvline(0, color="#aaaaaa", linewidth=0.8, zorder=0)

    # Border
    ax.plot(
        [x0, x1, x1, x0, x0],
        [y0, y0, y1, y1, y0],
        color="#999999",
        linewidth=1.0,
        zorder=0,
    )
