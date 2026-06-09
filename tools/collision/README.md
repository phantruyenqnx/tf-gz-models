# Collision generator (`gen_collision.py`)

Generate **simplified, physics-friendly collision geometry** for gz-sim models from
their dense visual meshes. CAD-exported visual meshes are far too heavy to use as
collisions (the f450 body is **261,692 faces**), which makes Gazebo physics lag.

Two methods:

| `--method` | Output | Use when |
|------------|--------|----------|
| **`box`** (default) | One body box + N landing-leg boxes (x500 style) | You want it light and resting on the ground correctly — the usual case for multicopters. |
| `coacd` | A set of convex sub-mesh STLs (CoACD decomposition) | The model genuinely needs a mesh-shaped collision. |

## Install

```bash
pip install -r requirements.txt   # trimesh, coacd, numpy
```

## Box method (default)

Fits boxes to the model's actual geometry:

- **Body box** — bounding box of everything at/above `--split-z`.
- **Leg boxes** — vertices below `--split-z` are split into `--n-legs` angular sectors;
  each cluster's bounding box becomes one leg box. The lowest box face is the foot
  contact, so the model rests at `base_link z = -lowest`.

```bash
python3 gen_collision.py --model <model> --link <link> [--mesh <file>] \
    [--transform "x y z R P Y"] \
    --method box --split-z <z> --n-legs <N> [--apply] [--dry-run]
```

The tool prints the **lowest collision z** — set the model's `<pose>` z to its negation
(plus a ~2 mm margin) so it spawns resting on the ground.

### Example: f450

The body visual is posed at `0 0 0.02 0 0 -0.125861774`, so bake that in; legs live
below `z = -0.045`, four of them:

```bash
python3 gen_collision.py --model f450_base --link base_link --mesh F450-base.STL \
    --transform "0 0 0.02 0 0 -0.125861774" \
    --method box --split-z -0.045 --n-legs 4 --apply
```

Result: **5 boxes** (1 body + 4 legs), lowest collision `z = -0.1633` (matches the
visual mesh bottom). Then set `f450_base` `<pose>` z = `0.165`. Verify:

```bash
gz sdf -p ../../models/f450/model.sdf      # 0 errors/warnings, 9 collisions
```

### Box options

| Option | Meaning | Default |
|--------|---------|---------|
| `--split-z` | z (model frame) splitting body from legs (required) | — |
| `--n-legs` | number of landing-leg clusters below split-z | 4 |
| `--leg-offset` | angular offset (rad) for leg sectoring | 0 |
| `--leg-min-pts` | drop leg clusters with fewer vertices | 30 |

> Tune `--split-z` by inspecting the mesh z-profile (where the legs start). If legs are
> at the corners (45°) the default `--leg-offset 0` works; rotate it if a leg straddles
> two sectors.

## CoACD method (optional)

Convex decomposition of the full mesh into convex sub-mesh STLs under
`models/<model>/meshes/collision/`, one `<collision><mesh>` each (every part is convex,
so the engine handles it cheaply — unlike one concave mesh, and unlike a single convex
hull which fills the gaps of an X-frame).

```bash
python3 gen_collision.py --model <model> --link <link> --mesh <file> \
    --method coacd --threshold 0.05 --min-volume 1e-5 [--apply]
```

| Option | Meaning | Default |
|--------|---------|---------|
| `--threshold` | CoACD concavity (0.01 fine … 1 coarse) | 0.05 |
| `--min-volume` | drop convex parts below this volume (m³) | 1e-5 |
| `--preprocess-resolution` | CoACD manifold voxel resolution (raise for thin features) | 50 |
| `--max-ch-vertex` | max vertices per convex hull | 64 |

> Caveat: with aggressive `--min-volume` or a low `--preprocess-resolution`, CoACD can
> leave gaps (thin arms/legs under-resolved). Check coverage before shipping.

## Common options

| Option | Meaning |
|--------|---------|
| `--model` / `--link` | model folder under `models/` and the link to attach collisions to |
| `--mesh` | mesh under `<model>/meshes/` (default: first `*.STL/.stl/.dae/.obj`) |
| `--transform "x y z R P Y"` | bake the visual `<pose>` (radians) into the collision so it lines up |
| `--apply` | replace the marked block in `model.sdf` in place (idempotent) |
| `--dry-run` | print the block only, write nothing |

The marker `<!-- BEGIN/END gen-collision:<link> -->` makes `--apply` idempotent — a
re-run updates the same block instead of duplicating it.
