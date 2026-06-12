# GTEC UWB Plugin — Gazebo Harmonic

ROS-free port of the GTEC UWB ranging sensor (Barral et al., *Sensors* 2019) to
Gazebo Harmonic (gz-sim 8). The plugin simulates a UWB tag, classifies the
LOS/NLOS channel to each anchor by ray tracing the world geometry, and publishes
`gtec_msgs.msgs.Ranging` messages on the gz-transport topic `/gtec/toa/ranging`.

Connect it to ROS 2 separately with `ros_gz_bridge` — a custom message mapping for
`gtec_msgs.msgs.Ranging` is required and is **out of scope** for this package.

## Dependencies

Gazebo Harmonic and dev packages: `gz-cmake3`, `gz-sim8`, `gz-transport13`,
`gz-msgs10`, `gz-math7`, `gz-plugin2`. GoogleTest for the unit tests.

## Build

```bash
cd gz_harmonic
cmake -S . -B build
cmake --build build
ctest --test-dir build --output-on-failure   # run the unit tests
```

This produces `build/libgtec_uwb_plugin.so`.

## Run the demo

```bash
cd gz_harmonic
GZ_SIM_SYSTEM_PLUGIN_PATH="$PWD/build" gz sim -r -s -v4 worlds/uwb_demo.sdf
```

`-v4` surfaces the `[GTEC UWB] plugin loaded, tag 0` confirmation. Drop `-s` to
also open the GUI.

### Inspecting the output

The plugin publishes a **custom** protobuf type. `gz topic -l` will list
`/gtec/toa/ranging` and its type, but `gz topic -e` **cannot decode** custom
messages unless their descriptor is registered with gz-msgs — it will appear to
hang silently. To inspect the data, use a small compiled subscriber that links the
generated `gtec_msgs/msgs/ranging.pb.h`, or register the message descriptor.
(Registering the descriptor is also what makes the later `ros_gz_bridge` mapping
straightforward.)

Expected behaviour in `uwb_demo.sdf`: `anchor_id 1` (clear line of sight) reports
range ≈ 6000 mm; `anchor_id 0` (behind the 0.3 m wall, wider than the 0.25 m
`nlosSoftWallWidth`) is classified NLOS-Hard and reports a longer range via the
reflection path.

## SDF parameters

Identical semantics to the legacy Gazebo Classic plugin:

| Parameter | Meaning |
|---|---|
| `update_rate` | publications per second |
| `nlosSoftWallWidth` | max wall thickness the signal penetrates (m) |
| `tag_z_offset` | height offset added to the tag (m) |
| `tag_link` | link used as the tag reference (falls back to the model) |
| `anchor_prefix` | anchors are models/links whose name starts with this |
| `all_los` | treat every anchor as line-of-sight |
| `tag_id` | tag identifier |
| `return_angle` | also publish a noisy planar bearing |

## Architecture

- `UwbChannelModel` — empirical lookup tables + Gaussian noise/power model (pure).
- `RayObstacleSet` — CPU analytic ray-vs-box/plane intersection (replaces Classic
  `RayShape`; supports box obstacles + a ground plane).
- `Resolver` — LOS / NLOS-Soft / NLOS-Hard reflection-search classification (pure).
- `EcmGeometry` — reads collision geometry and discovers tag/anchors from the ECM.
- `UwbSensorPlugin` — the gz-sim 8 system plugin (Configure + PostUpdate) and
  gz-transport publishing.

The measurement algorithm is preserved verbatim from the original; see
`../docs/superpowers/specs/2026-06-11-uwb-gazebo-harmonic-plugin-design.md`.
