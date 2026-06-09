# World file structure convention

Every `.sdf` world under [`worlds/`](../worlds/) follows the same three-section
layout so that any file is easy to read and edit. Sections are marked with a
banner comment and always appear in this order:

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="...">

    <!-- ===================== 1. PHYSICS & GPS COORDINATE ===================== -->
    <physics .../>
    <gravity>...</gravity>
    <magnetic_field>...</magnetic_field>
    <atmosphere .../>
    <wind>...</wind>                  <!-- optional -->
    <spherical_coordinates>...</spherical_coordinates>

    <!-- ===================== 2. ENVIRONMENT & LIGHT ===================== -->
    <scene>...</scene>
    <light name="sunUTC" .../>
    <!-- additional lights, if any -->

    <!-- ===================== 3. WORLD MODELS ===================== -->
    <model name="ground_plane">...</model>
    <include><uri>model://...</uri></include>
    <model name="...">...</model>

  </world>
</sdf>
```

SDF places no ordering requirement on the children of `<world>`, so this layout
is purely a project convention to keep the files consistent and diff-friendly.

## Section 1 — Physics & GPS coordinate

Global simulation parameters and the world origin in geographic coordinates.

| Element | Purpose |
|---------|---------|
| `<physics>` | Solver type and step rate (`max_step_size`, `real_time_update_rate`). |
| `<gravity>` | Gravity vector, normally `0 0 -9.8`. |
| `<magnetic_field>` | Earth magnetic field used by the simulated magnetometer. |
| `<atmosphere>` | Atmosphere model (`adiabatic`). |
| `<wind>` | Optional global wind (see `windy.sdf`). |
| `<spherical_coordinates>` | **GPS origin.** Maps the local ENU frame to lat/long/elevation; required for GPS/GNSS-based estimators. |

`<spherical_coordinates>` should always declare `EARTH_WGS84`, `ENU` world-frame
orientation, and a real `latitude_deg` / `longitude_deg` / `elevation`:

```xml
<spherical_coordinates>
  <surface_model>EARTH_WGS84</surface_model>
  <world_frame_orientation>ENU</world_frame_orientation>
  <latitude_deg>10.851572</latitude_deg>
  <longitude_deg>106.772496</longitude_deg>
  <elevation>10.0</elevation>
</spherical_coordinates>
```

## Section 2 — Environment & light

Everything that defines how the world looks: the `<scene>` (ambient/background,
grid, shadows, optional `<sky>`) and one or more `<light>` sources. The primary
directional light is conventionally named `sunUTC`.

## Section 3 — World models

The actual content of the world, in this order of preference:

1. `ground_plane` (the base collision/visual plane), then
2. `<include>` references to reusable models under [`models/`](../models/), then
3. inline `<model>` definitions specific to this world.

Keep reusable scenery in its own model directory and pull it in with
`<include><uri>model://name</uri></include>` instead of pasting large model
trees directly into the world. See `uwb.sdf` / `models/uwb` and
`warehouse.sdf` / `models/workcell` for examples. Bundle any texture or mesh a
model needs inside that model's own folder so the model stays self-contained.

## Adding or editing a world

1. Start from the skeleton above (or copy an existing small world such as
   `default.sdf`).
2. Set a real GPS origin in `<spherical_coordinates>`.
3. Put scenery into a model under `models/` and `<include>` it.
4. Validate before committing:

   ```shell
   cd Tools/simulation/gz
   export GZ_SIM_RESOURCE_PATH="$PWD/models:$PWD/worlds"

   gz sdf -k worlds/<name>.sdf          # syntax check
   gz sim -s -r --iterations 10 worlds/<name>.sdf   # headless load test
   ```

   `gz sdf -k` cannot resolve `model://` URIs on its own (it prints
   `Unable to find uri[...]` / empty `findFile` callback) — those messages are
   harmless. The `gz sim` load is the authoritative check.
