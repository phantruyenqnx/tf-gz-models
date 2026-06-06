# F450 — Gazebo (gz-sim) Model for PX4 SITL

A DJI-style **F450 quadrotor** for PX4 Software-In-The-Loop (SITL) simulation with
Gazebo (gz-sim / Harmonic). The model is split into a reusable airframe (`f450_base`)
and a thin wrapper (`f450`) that adds the four motor plugins.

- **Author:** Frank (phantruyenqnx@gmail.com)
- **SDF version:** 1.9
- **Airframe type:** Quadrotor (X)
- **PX4 sim model:** `gz_f450`
- **PX4 autostart ID:** `4022` (`ROMFS/.../airframes/4022_gz_f450`)

## Quick start

```bash
make px4_sitl gz_f450
```

This spawns the model in the default world and starts PX4 + the gz bridge.

## Model structure

| Model | Role |
|-------|------|
| [`f450`](./model.sdf) | Wrapper: `merge`-includes `f450_base`, then attaches 4 `MulticopterMotorModel` plugins (one per rotor). |
| [`f450_base`](../f450_base/model.sdf) | Airframe: `base_link` (body, collisions, sensors), 4 rotor links + joints, odometry plugin. |

Splitting base vs. motorized model mirrors the upstream `x500` / `x500_base` convention,
so variants (sensors, payloads) can reuse `f450_base`.

## Physical properties (`base_link`)

| Property | Value |
|----------|-------|
| Mass | 1.5 kg |
| Inertia `Ixx` / `Iyy` | 0.02167 kg·m² |
| Inertia `Izz` | 0.04 kg·m² |
| Body mesh | `meshes/F450-base.STL` |
| Body material | Carbon dark-grey PBR (metalness 0.7, roughness 0.35) |
| Collisions | 1 body box + 4 leg boxes |

> The body mesh is **STL**, which carries no UV coordinates, so an image texture
> (`materials/textures/CF.png`) cannot be wrapped onto it. The body is colored with
> solid PBR values instead. To get a true carbon-fiber weave (like `x500`), convert
> `F450-base.STL` to a UV-mapped `.dae`/`.obj`.

## Propulsion

Four rotors driven by `gz-sim-multicopter-motor-model-system`. Geometry/spin matches the
PX4 control-allocation airframe (X quad):

| Motor | Link / joint | Spin | PX4 function |
|-------|--------------|------|--------------|
| 0 | `rotor_0` | CCW | `SIM_GZ_EC_FUNC1` = 101 |
| 1 | `rotor_1` | CCW | `SIM_GZ_EC_FUNC2` = 102 |
| 2 | `rotor_2` | CW  | `SIM_GZ_EC_FUNC3` = 103 |
| 3 | `rotor_3` | CW  | `SIM_GZ_EC_FUNC4` = 104 |

Common motor-plugin parameters:

| Parameter | Value |
|-----------|-------|
| `motorConstant` | 8.54858e-06 |
| `momentConstant` | 0.016 |
| `maxRotVelocity` | 1000 rad/s |
| `timeConstantUp` / `Down` | 0.0125 / 0.025 s |
| `rotorDragCoefficient` | 8.06428e-05 |
| ESC range (`SIM_GZ_EC_MIN/MAX`) | 150 … 1000 |
| Hover throttle (`MPC_THR_HOVER`) | 0.60 |

## Sensors (all on `base_link`)

| Sensor | Type | Rate | Noise model |
|--------|------|------|-------------|
| `air_pressure_sensor` | barometer | 50 Hz | BMP390 (σ = 3 Pa) |
| `magnetometer_sensor` | magnetometer | 100 Hz | IIS2MDC (σ = 1e-4) |
| `imu_perfect` | IMU | 250 Hz | IIM42653 |
| `imu_sensor` | IMU | 250 Hz | IIM42653 (variant, currently `always_on=0`) |
| `navsat_sensor` | GNSS | 25 Hz | u-blox NEO-M9N (see below) — **read by PX4** |
| `navsat_ground_truth` | GNSS | 30 Hz | noiseless — **ignored by PX4**, for comparison/logging |

### GNSS noise model (`navsat_sensor`)

The PX4 gz bridge hard-codes the GPS sensor name to **`navsat_sensor`** on `base_link`
(`src/modules/simulation/gz_bridge/GZBridge.cpp`); do not rename it or PX4 receives no GPS.

GNSS noise is modeled as **small white noise + a slow Gauss-Markov (dynamic) bias**, which
reproduces a real receiver's smoothed output:

- **White noise** is tiny (fix-to-fix jitter), so EKF2's on-ground "GPS Pos Drift" pre-arm
  check (which measures fix-to-fix *rate*, not absolute error) passes.
- **Dynamic bias** provides the realistic ~1–2 m absolute horizontal wander.

| Channel | White σ | Dynamic-bias σ | Corr. time | Steady-state abs. error |
|---------|---------|----------------|------------|--------------------------|
| Horizontal pos | 2e-7 ° (~0.02 m) | 1.6e-6 ° | 150 s | ≈ 1.5 m |
| Vertical pos | 0.05 m | 0.35 m | 150 s | ≈ 3.0 m |
| Horizontal vel | 0.05 m/s | — | — | — |
| Vertical vel | 0.10 m/s | — | — | — |

Units per gz-sensors: **horizontal position = degrees** (1° ≈ 111 320 m), vertical = meters,
velocity = m/s. Steady-state bias σ = `dynamic_bias_stddev × √(corr_time / 2)`.

To relax the GPS pre-arm check while keeping noise: `param set EKF2_REQ_HDRIFT` /
`EKF2_REQ_VDRIFT`, or adjust the `EKF2_GPS_CHECK` bitmask.

## Plugins

- **Motor models** (×4) — `gz-sim-multicopter-motor-model-system` (in `f450/model.sdf`).
- **Odometry publisher** — `gz-sim-odometry-publisher-system`, publishes ground-truth
  odometry on `/model/f450/odometry` (world frame, `base_link`, 3D).

## UWB (work in progress — `EKF-UWB-fusion` branch)

`f450_base` contains a **commented-out** UWB anchor block (`model://uwb` +
`libuwb_range.so` plugin + `uwb_joint`). It is disabled because the `uwb` model and the
range plugin do not exist yet. Re-enable it after adding the model and building the plugin.

## Files

```
f450/
├── README.md          ← this file
├── model.config
└── model.sdf          ← wrapper + motor plugins
f450_base/
├── model.config
├── model.sdf          ← airframe, sensors, rotors
├── meshes/            ← F450-base.STL, CCW-prob.STL, CW-prob.STL
└── materials/textures/CF.png   (not yet used — STL has no UVs)
```

## Known cleanup TODO

- Fix spawn height
- Fix collision for model.
- Add model UWB
- Add plugin UWB tag.
