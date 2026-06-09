# Simulation tools

Utilities for managing the Gazebo models and worlds in this repo. Each tool is
grouped by function in its own subdirectory with a dedicated README.

| Tool | Purpose |
|------|---------|
| [`worlds/`](./worlds/) | Standardize and verify world files — format to the 3-section layout (`world_format.py`) and run structure + parse + load checks (`verify_worlds.sh`). |
| [`offline/`](./offline/) | Offline model setup — download external Fuel models (`download_external_models.sh`) and verify worlds load without internet (`verify_offline.sh`). |
| [`collision/`](./collision/) | Generate simplified collision geometry from dense visual meshes — x500-style boxes (default) or CoACD convex decomposition. |
| [`avl_automation/`](./avl_automation/) | AVL aerodynamic coefficient automation for fixed-wing models. |

## Worlds

All world files follow a common three-section layout
(see [`../docs/world-structure.md`](../docs/world-structure.md)):

```
1. PHYSICS & GPS COORDINATE   physics, gravity, magnetic_field, atmosphere, wind, spherical_coordinates
2. ENVIRONMENT & LIGHT        scene, light(s)
3. WORLD MODELS               ground_plane, include, model...
```

```bash
cd Tools/simulation/gz

# format / check structure
python3 tools/worlds/world_format.py --all
python3 tools/worlds/world_format.py --all --check     # CI: non-zero if not normalized

# verify (structure + parse + load), one world or all
./tools/worlds/verify_worlds.sh --all
./tools/worlds/verify_worlds.sh uwb
```

See [`worlds/README.md`](./worlds/README.md) for details.

## Offline models

`baylands` and `forest` reference external Gazebo Fuel models. Download and
verify them for offline use:

```bash
cd Tools/simulation/gz
./tools/offline/download_external_models.sh
./tools/offline/verify_offline.sh
```

See [`offline/README.md`](./offline/README.md) for the model list and
troubleshooting.

## References

- [Gazebo Sim Documentation](https://gazebosim.org/docs)
- [SDF Format Specification](http://sdformat.org/)
- [Gazebo Fuel Models](https://fuel.gazebosim.org)
- [PX4 SITL Simulation](https://docs.px4.io/main/en/simulation/)

## Version history

- **v3.0** (2026-06): Tools grouped by function into subdirectories
  (`worlds/`, `offline/`). Worlds adopt the three-section layout; added
  `world_format.py` (idempotent formatter + `--check`) and `verify_worlds.sh`.
- **v2.0** (2026-01): Standardization of all worlds to SDF 1.9.
- **v1.0**: Original mixed-format worlds.
