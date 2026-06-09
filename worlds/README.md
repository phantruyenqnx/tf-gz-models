# Gazebo worlds

SDF world files used for PX4 SITL / HITL simulation. All files follow the same
three-section layout — see [World file structure convention](../docs/world-structure.md).

```
1. PHYSICS & GPS COORDINATE   physics, gravity, magnetic_field, atmosphere, wind, spherical_coordinates
2. ENVIRONMENT & LIGHT        scene, light(s)
3. WORLD MODELS               ground_plane, include, model...
```

## Available worlds

| World | Physics | Description |
|-------|---------|-------------|
| `default.sdf` | ode | Minimal flat ground plane — the standard starting world. |
| `default_bullet.sdf` | ode | Default flat world variant kept for the Bullet/featherstone setup. |
| `aruco.sdf` | ode | Flat ground with an ArUco marker for vision / precision-landing tests. |
| `baylands.sdf` | ode | Large outdoor Baylands terrain. |
| `forest.sdf` | ode | Outdoor scene populated with many tree `include`s. |
| `lawn.sdf` | ode | Grass lawn environment (two directional lights). |
| `walls.sdf` | ode | Flat ground with box walls for obstacle-avoidance tests. |
| `frictionless.sdf` | ode | Flat ground with frictionless surface for dynamics tests. |
| `windy.sdf` | ode | Flat ground with a global `<wind>` field. |
| `moving_platform.sdf` | ode | World containing a moving platform for landing-on-target tests. |
| `rover.sdf` | ode | Ground world tuned for rover vehicles. |
| `warehouse.sdf` | dart | Indoor warehouse (`model://workcell`), DART solver. |
| `hitl_default.sdf` | ode | Default world for hardware-in-the-loop runs. |
| `uav_contest_2026.sdf` | ode | **Project:** UAV contest 2026 arena (zones, targets, helipad, rescued objects). |
| `uwb.sdf` | ode | **Project:** UWB precise-landing environment (`model://uwb`: buildings, roads, soccer field, helipad + 4 UWB anchors). |

`default*`, `aruco`, `baylands`, `forest`, `lawn`, `walls`, `frictionless`,
`windy`, `moving_platform`, `rover`, `warehouse` and `hitl_default` are tracked
from upstream PX4; `uav_contest_2026` and `uwb` are project-specific.

## Running a world

# direct
gz sim worlds/uwb.sdf


## Validating after edits

```shell
gz sdf -k worlds/<name>.sdf                       # syntax check
gz sim -s -r --iterations 10 worlds/<name>.sdf    # headless load test
```

`gz sdf -k` cannot resolve `model://` URIs by itself (`Unable to find uri[...]`
messages are expected); the `gz sim` load is the real check.
