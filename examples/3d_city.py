"""3D city skyline — hatched buildings on a plotter."""

import numpy as np
from penpal import pen_width
from penpal.render3d import Camera, Scene, Mesh3D, TextureSpec, Wireframe

rng = np.random.default_rng(77)

scene = Scene()

# --- City grid ---
grid_rows, grid_cols = 6, 8
block_size = 0.95

for row in range(grid_rows):
    for col in range(grid_cols):
        # Skip a few slots — empty lots / parks
        if rng.random() < 0.1:
            continue

        cx = (col - grid_cols / 2 + 0.5) * block_size
        cz = (row - grid_rows / 2 + 0.5) * block_size

        # Base dimensions
        w = rng.uniform(0.35, 0.75)
        d = rng.uniform(0.35, 0.75)
        h = rng.exponential(1.0) + 0.3  # exponential gives nice skyline shape

        # Downtown cluster — taller in the middle
        dist = np.sqrt(cx**2 + cz**2)
        if dist < 1.5:
            h *= rng.uniform(1.5, 2.5)
        elif dist < 3.0:
            h *= rng.uniform(0.8, 1.5)

        h = min(h, 5.0)  # cap height

        # Per-building texture variation
        angle = rng.choice([0, 30, 45, 60, 90, 135])
        spacing = rng.uniform(0.04, 0.1)

        # Taller buildings get finer hatching (denser = darker = heavier)
        if h > 3.0:
            spacing = rng.uniform(0.03, 0.06)
            style = rng.choice(['hatch', 'crosshatch'])
        elif h > 1.5:
            style = rng.choice(['hatch', 'hatch', 'crosshatch'])
        else:
            style = 'hatch'

        front_tex = TextureSpec(style=style, spacing=spacing, angle=angle)
        side_tex = TextureSpec(style=style, spacing=spacing, angle=(angle + 90) % 180)
        roof_tex = TextureSpec(style='crosshatch', spacing=rng.uniform(0.06, 0.12))

        building = Mesh3D.box(
            size=(w, h, d),
            center=(cx, h / 2, cz),
            face_textures={
                'top': roof_tex,
                'front': front_tex,
                'back': front_tex,
                'left': side_tex,
                'right': side_tex,
            },
            face_layers={
                'top': 'roofs',
                'front': 'walls', 'back': 'walls',
                'left': 'walls', 'right': 'walls',
                'bottom': 'walls',
            },
        )
        scene.add(building)

# --- Ground ---
scene.add(Mesh3D.plane(
    width=12, depth=10,
    center=(0, 0, 0),
    normal_axis='y',
    texture=TextureSpec(style='hatch', spacing=0.25, angle=90),
    layer='ground',
))

# --- Camera: low-ish angle, looking slightly up at the skyline ---
cam = Camera.orbit(
    target=(0, 1.2, 0),
    distance=8,
    azimuth=22,
    elevation=22,
    fov=55,
)

d = scene.render(cam, width=10, height=8, hidden_lines='remove')

lw = pen_width(0.3)
d.layer('walls', color='black', linewidth=lw)
d.layer('roofs', color='black', linewidth=lw)
d.layer('ground', color='#aaaaaa', linewidth=lw)

d.save('output/review/3d_city.svg', provenance=False)
print(d)
for l in d.layers:
    print(f'  {l.name}: {len(l.lines)} lines')
print('Saved to output/review/3d_city.svg')

import matplotlib
matplotlib.use('Agg')
fig, ax = d.show()
fig.savefig('output/review/3d_city.png', dpi=200, bbox_inches='tight')
print('Saved to output/review/3d_city.png')
