"""SVG writer — multi-layer Inkscape SVG output.

Direct XML generation. Supports Inkscape layer groups for multi-pen plotting.
Handles centered coordinate systems via viewBox offset.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from penpal.core.drawing import Drawing


def to_svg_string(drawing: Drawing, grid: bool = False, precision: int = 4) -> str:
    """Generate SVG string from a Drawing."""
    w, h, units = drawing.width, drawing.height, drawing.units
    x0, _ = drawing.x_range
    y0, _ = drawing.y_range

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        f'     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"',
        f'     width="{w}{units}" height="{h}{units}"',
        f'     viewBox="{x0} {y0} {w} {h}">',
    ]

    if grid:
        parts.append(_grid_svg(drawing, precision))

    for layer in drawing.layers:
        style = layer.style
        parts.append(
            f'  <g inkscape:groupmode="layer" inkscape:label="{layer.name}"'
            f' stroke="{style.color}" stroke-width="{style.linewidth}"'
            f' fill="none" opacity="{style.alpha}">'
        )
        for line in layer.lines:
            if len(line) == 2:
                x1, y1 = line[0, :2]
                x2, y2 = line[1, :2]
                parts.append(
                    f'    <line x1="{x1:.{precision}f}" y1="{y1:.{precision}f}"'
                    f' x2="{x2:.{precision}f}" y2="{y2:.{precision}f}"/>'
                )
            else:
                pts = " ".join(
                    f"{x:.{precision}f},{y:.{precision}f}" for x, y in line[:, :2]
                )
                parts.append(f'    <polyline points="{pts}"/>')
        parts.append("  </g>")

    parts.append("</svg>")
    return "\n".join(parts)


def _grid_svg(drawing, precision: int = 4) -> str:
    """Generate SVG grid lines for reference display."""
    import numpy as np

    x0, x1 = drawing.x_range
    y0, y1 = drawing.y_range

    lines = ['  <g id="grid" stroke="#e0e0e0" stroke-width="0.01" fill="none">']
    for x in np.arange(np.ceil(x0), x1 + 0.01, 1):
        lines.append(f'    <line x1="{x:.{precision}f}" y1="{y0:.{precision}f}" x2="{x:.{precision}f}" y2="{y1:.{precision}f}"/>')
    for y in np.arange(np.ceil(y0), y1 + 0.01, 1):
        lines.append(f'    <line x1="{x0:.{precision}f}" y1="{y:.{precision}f}" x2="{x1:.{precision}f}" y2="{y:.{precision}f}"/>')
    lines.append("  </g>")

    lines.append('  <g id="grid-major" stroke="#c0c0c0" stroke-width="0.02" fill="none">')
    for x in np.arange(np.ceil(x0 / 5) * 5, x1 + 0.01, 5):
        lines.append(f'    <line x1="{x:.{precision}f}" y1="{y0:.{precision}f}" x2="{x:.{precision}f}" y2="{y1:.{precision}f}"/>')
    for y in np.arange(np.ceil(y0 / 5) * 5, y1 + 0.01, 5):
        lines.append(f'    <line x1="{x0:.{precision}f}" y1="{y:.{precision}f}" x2="{x1:.{precision}f}" y2="{y:.{precision}f}"/>')
    lines.append("  </g>")

    # Origin crosshair if centered
    if drawing.center:
        lines.append('  <g id="grid-origin" stroke="#aaaaaa" stroke-width="0.015" fill="none">')
        lines.append(f'    <line x1="{x0:.{precision}f}" y1="0" x2="{x1:.{precision}f}" y2="0"/>')
        lines.append(f'    <line x1="0" y1="{y0:.{precision}f}" x2="0" y2="{y1:.{precision}f}"/>')
        lines.append("  </g>")

    return "\n".join(lines)


def save_drawing(drawing: Drawing, path: str, **kwargs):
    """Save a Drawing as SVG file."""
    if not path.endswith(".svg"):
        path = path + ".svg"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    svg = to_svg_string(drawing, **kwargs)
    with open(path, "w") as f:
        f.write(svg)


def save_drawing_layers(drawing: Drawing, path_prefix: str, **kwargs):
    """Save each layer as a separate SVG file."""
    from penpal.core.drawing import Drawing as DrawingCls

    os.makedirs(os.path.dirname(path_prefix) or ".", exist_ok=True)
    for layer in drawing.layers:
        d = DrawingCls(drawing.width, drawing.height, drawing.units, show_grid=False,
                       center=drawing.center)
        d.layer(layer.name, color=layer.style.color, linewidth=layer.style.linewidth)
        d.layer(layer.name).add(layer.paths)
        save_drawing(d, f"{path_prefix}_{layer.name}.svg", **kwargs)
