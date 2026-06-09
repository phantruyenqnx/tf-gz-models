# Offline model setup

Some worlds reference external models hosted on Gazebo Fuel. These tools
download those models into [`../../models/`](../../models/) and verify that the
worlds can load without an internet connection.

| Script | Purpose |
|--------|---------|
| [`download_external_models.sh`](./download_external_models.sh) | Download the external Fuel models required by the `baylands` and `forest` worlds. |
| [`verify_offline.sh`](./verify_offline.sh) | Check that the required models exist locally and reference local paths (no Fuel URLs). |

## Quick start

```bash
cd Tools/simulation/gz
./tools/offline/download_external_models.sh
./tools/offline/verify_offline.sh
```

After downloading, make sure Gazebo can find the models:

```bash
export GZ_SIM_RESOURCE_PATH=${GZ_SIM_RESOURCE_PATH}:/path/to/Tools/simulation/gz/models
```

## Models downloaded

| Model | Owner | Used by |
|-------|-------|---------|
| `baylands` | OpenRobotics | baylands |
| `Coast Water` | OpenRobotics | baylands |
| `grasspatch` | hexarotor | forest |
| `Oak Tree` | OpenRobotics | forest |
| `Pine Tree` | OpenRobotics | forest |

## Manual download

If the script fails, download each model from Gazebo Fuel
(<https://fuel.gazebosim.org>) and place it under `../../models/<name>/` with its
`model.config`, `model.sdf` and any `meshes/`.

## Troubleshooting

**`Unable to find model[...]`** — run `download_external_models.sh`, confirm the
model exists under `../../models/`, and check `GZ_SIM_RESOURCE_PATH`.
