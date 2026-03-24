# Gazebo World Standardization and Offline Setup

This directory contains tools for managing Gazebo models and ensuring offline capability for all simulation worlds.

## Overview

All world files in `../worlds/` have been standardized to follow a consistent format based on the warehouse world configuration. This ensures:

- **Consistency**: Uniform structure, physics settings, and lighting across all worlds
- **Offline Support**: All external models can be downloaded and cached locally
- **Maintainability**: Easy to update and modify world configurations
- **Performance**: Optimized physics settings for UAV simulation

## Standardized Format

### SDF Version and Structure

All worlds now use:
- **SDF Version**: 1.9 (Gazebo Harmonic compatible)
- **XML Declaration**: `<?xml version="1.0"?>`
- **Physics**: High-precision configuration (max_step_size=0.001, real_time_update_rate=1000)
- **Ground Plane**: 500x500 visual size, 1x1 collision size
- **Lighting**: Standardized directional light named "sunUTC"
- **Boolean Format**: `true/false` instead of `1/0`

### Standard Element Order

```xml
<?xml version="1.0"?>
<sdf version='1.9'>
  <world name='...'>
    <physics name='default_physics' default='0' type='ode'>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    <gravity>0 0 -9.8</gravity>
    <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
    <atmosphere type='adiabatic'/>
    <scene>...</scene>
    <model name='ground_plane'>...</model>
    <!-- World-specific models/includes -->
    <light name='sunUTC'>...</light>
    <spherical_coordinates>...</spherical_coordinates>
  </world>
</sdf>
```

## Downloading External Models for Offline Use

Some worlds (baylands, forest) reference external models from Gazebo Fuel. To use these worlds offline, you need to download the models locally.

### Quick Start

```bash
cd /path/to/UAV-gazebo-models/tools
chmod +x download_external_models.sh
./download_external_models.sh
```

This script will download the following models:
- **baylands** (OpenRobotics) - Park environment
- **Coast Water** (OpenRobotics) - Water surface
- **grasspatch** (hexarotor) - Grass terrain patches
- **Oak Tree** (OpenRobotics) - Oak tree models
- **Pine Tree** (OpenRobotics) - Pine tree models

### Manual Download

If the script fails, you can manually download models from:

1. **Gazebo Fuel (Harmonic)**: https://fuel.gazebosim.org
2. **Ignition Fuel (Legacy)**: https://fuel.ignitionrobotics.org

Download each model and place it in the `../models/` directory with the following structure:

```
models/
├── baylands/
│   ├── model.config
│   ├── model.sdf
│   └── meshes/
├── Coast Water/
│   ├── model.config
│   └── model.sdf
├── grasspatch/
│   ├── model.config
│   └── model.sdf
├── Oak Tree/
│   ├── model.config
│   ├── model.sdf
│   └── meshes/
└── Pine Tree/
    ├── model.config
    ├── model.sdf
    └── meshes/
```

### Environment Configuration

After downloading models, ensure Gazebo can find them by setting the resource path:

```bash
export GZ_SIM_RESOURCE_PATH=${GZ_SIM_RESOURCE_PATH}:/path/to/UAV-gazebo-models/models
```

Add this to your shell configuration file (`~/.bashrc` or `~/.zshrc`) for persistence.

## World Files Summary

### Simple Worlds (No External Dependencies)

These worlds work immediately without additional downloads:

| World | Description | Special Features |
|-------|-------------|------------------|
| **default** | Basic empty world | Standard testing environment |
| **aruco** | World with ArUco marker | Vision-based navigation testing |
| **warehouse** | Indoor warehouse environment | Complex collision geometry |
| **walls** | World with box walls | Obstacle avoidance testing |
| **moving_platform** | Dynamic moving platform | Landing on moving targets |
| **rover** | Ground vehicle optimized | Higher friction for rovers |
| **lawn** | Green grass field | Custom lawn material, clouds |
| **windy** | World with wind effects | Wind simulation enabled |
| **frictionless** | Low-friction surface | Physics testing |

### Complex Worlds (Require External Models)

These worlds need the external models downloaded:

| World | Description | Required Models |
|-------|-------------|-----------------|
| **baylands** | Large outdoor park | baylands, Coast Water |
| **forest** | Forest with trees | grasspatch, Oak Tree, Pine Tree |

## Physics Configuration Details

All worlds use the warehouse physics configuration for consistency:

```xml
<physics name='default_physics' default='0' type='ode'>
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>
</physics>
```

**Benefits:**
- **High precision**: 0.001s step size for accurate UAV dynamics
- **Real-time capable**: 1000 Hz update rate matches typical control loops
- **Stable simulation**: Prevents physics instabilities with fast-moving objects

### World-Specific Customizations

Some worlds retain special features:

- **rover.sdf**: Higher friction coefficients (mu=1, mu2=1) for ground vehicles
- **lawn.sdf**: Custom green material and additional lighting
- **windy.sdf**: Wind effects enabled with `<wind>` element
- **baylands.sdf**: Custom ambient lighting and sky configuration

## Troubleshooting

### Models Not Found

**Error**: `[Err] [Model.cc:XXX] Unable to find model[...]`

**Solution**: 
1. Run `./download_external_models.sh`
2. Verify models exist in `../models/` directory
3. Check `GZ_SIM_RESOURCE_PATH` environment variable

### Slow Simulation

**Issue**: Simulation runs slower than real-time

**Solutions**:
- Reduce physics update rate (not recommended for UAVs)
- Use simpler worlds (default, walls)
- Check system resources (CPU, GPU)

### Lighting Issues

**Issue**: World appears too dark or too bright

**Solution**: All worlds now use standardized lighting. If issues persist, check graphics drivers and Gazebo rendering settings.

## Contributing

When creating new worlds:

1. Copy an existing standardized world as a template
2. Follow the standard element order
3. Use the warehouse physics configuration
4. Set ground plane visual size to 500x500
5. Use `model://` URIs for all model references
6. Test with `gz sim <world_name>.sdf`

## References

- [Gazebo Sim Documentation](https://gazebosim.org/docs)
- [SDF Format Specification](http://sdformat.org/)
- [Gazebo Fuel Models](https://fuel.gazebosim.org)
- [PX4 SITL Simulation](https://docs.px4.io/main/en/simulation/)

## Version History

- **v2.0** (2026-01): Complete standardization of all 11 worlds
  - Updated to SDF 1.9
  - Warehouse physics configuration
  - 500x500 ground plane
  - Local model references for offline support
  
- **v1.0** (Previous): Original mixed format worlds

