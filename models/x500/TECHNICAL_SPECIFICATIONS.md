# X500 Quadcopter - Technical Specifications

**Reference Aircraft:** NXP HoverGames Drone Kit (KIT-HGDRONEK66)
**Frame Type:** X-configuration quadcopter
**Wheelbase:** 500mm

---

## Table of Contents
1. [Mass and Weight](#mass-and-weight)
2. [Physical Dimensions](#physical-dimensions)
3. [Motor and Propeller Specifications](#motor-and-propeller-specifications)
4. [Thrust and Force Analysis](#thrust-and-force-analysis)
5. [Payload Capacity](#payload-capacity)
6. [Inertia Tensors](#inertia-tensors)
7. [Battery and Power System](#battery-and-power-system)
8. [Aerodynamic Parameters](#aerodynamic-parameters)
9. [Sensor Suite](#sensor-suite)
10. [X500 Model Variants](#x500-model-variants)
11. [Tuning Recommendations](#tuning-recommendations)

---

## Mass and Weight

| Component | Mass (kg) | Notes |
|-----------|-----------|-------|
| Base link (chassis) | 2.000 | Main airframe |
| Rotor assembly (each) | 0.0161 | Motor + propeller + mount |
| Total (4 rotors) | 0.0644 | All rotors combined |
| **Total Dry Weight** | **2.064 kg** | Without battery/payload |

**Weight Distribution:**
- Chassis: 96.9% of total mass
- All rotors: 3.1% of total mass

---

## Physical Dimensions

### Frame Geometry
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Wheelbase** | 500 mm | Motor-to-motor diagonal |
| **Motor arm length** | 174 mm | Center to motor center |
| **Frame size (LxWxH)** | 410 x 410 x 300 mm | Official dimensions |
| **Motor X-spacing** | ±174 mm | X-axis motor offset |
| **Motor Y-spacing** | ±174 mm | Y-axis motor offset |

### Collision Geometry
| Element | Dimensions (m) | Shape |
|---------|----------------|-------|
| Base platform | 0.354 x 0.354 x 0.05 | Box |
| Each rotor | 0.2792 x 0.0169 x 0.00085 | Box (rotating) |

### Motor Positions (X-configuration)
```
      NW (0)           NE (1)
        ↻               ↺
         \             /
          \           /
           \         /
            \       /
             \     /
              \ ↓ /
               [+]  ← Center (base_link)
              / ↑ \
             /     \
            /       \
           /         \
          /           \
         /             \
        ↺               ↻
      SW (2)           SE (3)

Position coordinates (relative to base_link):
- rotor_0 (NW): (-0.174, -0.174, 0.024) m - CCW
- rotor_1 (NE): ( 0.174, -0.174, 0.024) m - CW
- rotor_2 (SW): (-0.174,  0.174, 0.024) m - CW
- rotor_3 (SE): ( 0.174,  0.174, 0.024) m - CCW
```

**Spawn Height:** 0.24 m above ground level

---

## Motor and Propeller Specifications

### Motor Hardware (Reference)
| Specification | Value | Source |
|--------------|-------|--------|
| **Motor Model** | T-Motor 2216 | PX4 documentation |
| **KV Rating** | 880 KV | RPM per volt |
| **Max RPM @ 14.8V** | 13,024 RPM | KV × Voltage |
| **Max Angular Velocity** | 1363.9 rad/s | Theoretical @ 14.8V |
| **Motor Quantity** | 4 | Standard quad |
| **Motor Type** | Brushless outrunner | - |

### Current SDF Motor Parameters
| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| `maxRotVelocity` | 1000.0 | rad/s | Maximum rotor speed limit |
| `motorConstant` | 8.54858e-06 | N⋅s² | Thrust coefficient (F = k_m × ω²) |
| `momentConstant` | 0.016 | Nm/N | Torque-to-thrust ratio (Q/F) |
| `rotorDragCoefficient` | 8.06428e-05 | - | Aerodynamic drag |
| `rollingMomentCoefficient` | 1e-06 | - | Bearing friction |
| `timeConstantUp` | 0.0125 | s | Spin-up time constant (12.5 ms) |
| `timeConstantDown` | 0.025 | s | Spin-down time constant (25 ms) |

**Motor Response Characteristics:**
- **Acceleration:** Reaches 63% of target speed in 12.5 ms
- **Deceleration:** Drops to 37% of initial speed in 25 ms
- **Spin-down ratio:** 2× slower than spin-up (realistic for propeller drag)

### Propeller Specifications
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Propeller Model** | 1345 prop | ~13 x 4.5 inch |
| **Reference Prop** | APC 1047 | From documentation |
| **Configuration** | 2x CCW + 2x CW | Differential torque cancellation |
| **Mesh Scale** | 0.8462 | Scale factor applied |
| **Visual Mesh** | `1345_prop_ccw.stl` / `1345_prop_cw.stl` | - |

---

## Thrust and Force Analysis

### Current Configuration (motorConstant = 8.54858e-06)

**Thrust Calculation:**
```
Thrust per motor = motorConstant × ω²
                 = 8.54858e-06 × (1000 rad/s)²
                 = 8.55 N

Total thrust (4 motors) = 4 × 8.55 N = 34.2 N
```

**Thrust-to-Weight Ratio (TWR):**
```
Weight = mass × g = 2.0 kg × 9.81 m/s² = 19.62 N

TWR = Total Thrust / Weight
    = 34.2 N / 19.62 N
    = 1.74:1
```

**Performance Margins:**
- Hover throttle: ~57% (1/1.74)
- Available excess thrust: 14.58 N (74% above weight)
- Maximum vertical acceleration: ~7.3 m/s² (0.74g + 1.0g gravity)

### Recommended Motor Constants (From Bench Data Analysis)

Based on T-Motor 2216 KV880 thrust bench testing with APC 1047 propeller @ 14.8V:

| Scenario | motorConstant | TWR | Hover% | Max Thrust | Notes |
|----------|---------------|-----|--------|------------|-------|
| **Conservative** | 4.34e-06 | 1.65:1 | 61% | 32.4 N | Realistic hover |
| **Balanced** | 5.50e-06 | 2.0:1 | 50% | 39.2 N | **Recommended** |
| **Aggressive** | 6.70e-06 | 2.5:1 | 40% | 49.1 N | Aerobatic flight |
| **Current X500** | 8.54858e-06 | 1.74:1 | 57% | 34.2 N | Empirically tuned |

**Analysis Notes:**
- Current `motorConstant` is ~2× higher than realistic bench test values
- Real T-Motor 2216 produces ~4.91N at hover (not 8.55N)
- Model appears tuned for simulation stability rather than physics accuracy
- `maxRotVelocity` (1000 rad/s) is conservative vs. theoretical 1363.9 rad/s

---

## Payload Capacity

### Maximum Payload Estimates

| Configuration | Available Margin | Max Payload | Notes |
|---------------|------------------|-------------|-------|
| Current params (TWR=1.74) | 0.74:1 | **1.45 kg** | Conservative estimate |
| Recommended (TWR=2.0) | 1.0:1 | **2.0 kg** | With agility margin |
| Conservative (TWR=1.65) | 0.65:1 | **1.28 kg** | Hover-only capability |
| Aggressive (TWR=2.5) | 1.5:1 | **2.94 kg** | Maximum performance |

**Payload Calculation Formula:**
```
Max Payload = (Total Thrust / g) - Base Mass
            = (Total Thrust / 9.81) - 2.0

Example (current params):
Max Payload = (34.2 / 9.81) - 2.0 = 1.49 kg
```

**Operational Recommendations:**
- **Slung Payload:** ≤ 1.0 kg for stable flight (current params)
- **Fixed Payload:** ≤ 1.5 kg if centered (better CG control)
- **Safety Margin:** Keep 20-30% thrust reserve for maneuvering

### Slung Payload Considerations
For `x500_slung_payload` variant with 3m tether:
- **Recommended max:** 0.4-0.8 kg (cable dynamics add instability)
- **Tested payload mass:** 0.4 kg (from payload model default)
- **Tether mass:** 0.064 kg (3m cable @ 6mm diameter)
- **Total slung load:** ~0.46 kg
- **Remaining margin:** ~1.0 kg for aggressive maneuvers

---

## Inertia Tensors

### Base Link (Chassis) - 2.0 kg
```xml
<inertial>
  <mass>2.0</mass>
  <inertia>
    <ixx>0.02166666666667</ixx>
    <ixy>0.0</ixy>
    <ixz>0.0</ixz>
    <iyy>0.02166666666667</iyy>
    <iyz>0.0</iyz>
    <izz>0.04000000000001</izz>
  </inertia>
</inertial>
```

**Inertia Matrix:**
```
⎡ 0.0217    0       0    ⎤
⎢   0     0.0217    0    ⎥  kg⋅m²
⎣   0       0     0.0400 ⎦
```

**Physical Interpretation:**
- **Ixx, Iyy (roll/pitch):** 0.0217 kg⋅m² (symmetric - X-quad)
- **Izz (yaw):** 0.0400 kg⋅m² (~1.85× larger - easier to roll/pitch than yaw)
- **Cross-terms:** 0 (perfect symmetry)

### Each Rotor (Motor + Propeller + Mount) - 0.0161 kg
```xml
<inertial>
  <mass>0.016076923</mass>
  <inertia>
    <ixx>3.8464910e-07</ixx>
    <iyy>2.6115852e-05</iyy>
    <izz>2.6498582e-05</izz>
  </inertia>
</inertial>
```

**Rotor Inertia Characteristics:**
- **Ixx (spin axis):** 3.85e-07 kg⋅m² (very low - disc spinning)
- **Iyy, Izz (perpendicular):** 2.61e-05 kg⋅m² (~68× larger - gyroscopic effect)

**Gyroscopic Torque (per rotor @ 1000 rad/s):**
```
L_gyro = I_rotor × ω_rotor × ω_angular
       ≈ 2.65e-05 × 1000 × ω_ang
       = 0.0265 × ω_ang [Nm]
```

For 1 rad/s pitch rate: **0.0265 Nm** gyroscopic torque per rotor

---

## Battery and Power System

### Battery Specifications
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Configuration** | 4S LiPo | 4 cells in series |
| **Max Voltage** | 14.8 V | Fully charged (4.2V × 4) |
| **Nominal Voltage** | 14.8 V | Used in calculations |
| **Min Voltage** | 12.0 V | Low battery cutoff (3.0V × 4) |
| **Reference Voltage** | 7.4 V | 2S minimum (for ESC compatibility) |

### Electronic Speed Controllers (ESC)
| Parameter | Value | Notes |
|-----------|-------|-------|
| **ESC Model** | Holybro BLHeli S | From documentation |
| **Max Current (each)** | 20 A | Per ESC rating |
| **Max Power (each)** | 320 W | @ 14.8V, 20A |
| **Total Power** | 1280 W | All 4 motors |

### Power Consumption Estimates
| Flight Mode | Throttle | Current/Motor | Total Current | Power |
|-------------|----------|---------------|---------------|-------|
| Hover | ~57% | ~12 A | ~48 A | ~710 W |
| Cruising | 60-70% | 13-15 A | 52-60 A | 770-890 W |
| Max Thrust | 100% | 20 A | 80 A | 1184 W |

**Flight Time Estimates** (with typical battery):
- 5000 mAh 4S: ~5-6 minutes hover, 4-5 minutes cruise
- 10000 mAh 4S: ~10-12 minutes hover, 8-10 minutes cruise

---

## Aerodynamic Parameters

### Motor/Rotor Aerodynamics
| Parameter | Value | Description |
|-----------|-------|-------------|
| `rotorDragCoefficient` | 8.06428e-05 | Propeller drag (F_drag = k_d × ω²) |
| `rollingMomentCoefficient` | 1e-06 | Bearing/motor friction torque |
| `momentConstant` | 0.016 | Torque-to-thrust ratio (Q = k_q × F) |

**Drag Force Calculation:**
```
F_drag = rotorDragCoefficient × ω²
       = 8.06e-05 × (1000)²
       = 80.6 N (deceleration drag)
```

**Torque Calculation:**
```
Q_motor = momentConstant × Thrust
        = 0.016 × 8.55 N
        = 0.137 Nm per motor
```

**Total Yaw Authority:**
```
Q_total = (Q_CW - Q_CCW) × 2 motors
        = Differential torque for yaw control
```

### Airframe Drag (Not explicitly modeled)
- No fuselage drag plugin in base x500 model
- Drag primarily from rotor disc area
- Total frontal area: ~0.125 m² (4× propeller discs)

---

## Sensor Suite

### Air Pressure Sensor (Barometer)
```xml
<update_rate>50</update_rate>
<noise type="gaussian">
  <stddev>3</stddev>  <!-- ~3 Pa noise -->
</noise>
```
- **Model:** BMP390 equivalent
- **Altitude resolution:** ~0.25 m (at sea level)
- **Update rate:** 50 Hz

### IMU (Inertial Measurement Unit)
```xml
<update_rate>250</update_rate>
<angular_velocity>
  <noise type="gaussian">
    <stddev>0.000873</stddev>  <!-- 0.05 deg/s -->
  </noise>
</angular_velocity>
<linear_acceleration>
  <x><noise><stddev>0.00637</stddev></noise></x>
  <y><noise><stddev>0.00637</stddev></noise></y>
  <z><noise><stddev>0.00686</stddev></noise></z>
</linear_acceleration>
```
- **Gyro noise:** 0.05 deg/s (very clean)
- **Accel noise:** 0.006-0.007 m/s² (~0.06% g)
- **Update rate:** 250 Hz (4 ms period)

### Magnetometer
```xml
<update_rate>100</update_rate>
<noise type="gaussian">
  <stddev>0.0001</stddev>  <!-- 0.1 mT -->
</noise>
```
- **Update rate:** 100 Hz
- **Noise:** 0.1 mT (1 mGauss) on all axes

### GPS/NavSat
```xml
<update_rate>30</update_rate>
```
- **Update rate:** 30 Hz (33.3 ms period)
- **Position accuracy:** Depends on world configuration

---

## X500 Model Variants

The UAV-gazebo-models repository contains **14 X500 variants**, all inheriting from `x500_base`:

| Model Name | Description | Added Sensors/Payloads |
|------------|-------------|------------------------|
| `x500` | Base model with motors | IMU, GPS, Magnetometer, Barometer |
| `x500_base` | Core airframe only | No motors (reference template) |
| `x500_depth` | Depth camera variant | Intel RealSense D435 equivalent |
| `x500_gimbal` | With gimbal mount | 2-axis stabilized gimbal |
| `x500_flow` | Optical flow sensor | PX4Flow equivalent (downward) |
| `x500_lidar_2d` | 2D LiDAR scanner | RPLidar A2 equivalent |
| `x500_lidar_down` | Downward LiDAR | Rangefinder for altitude |
| `x500_lidar_front` | Forward LiDAR | Obstacle avoidance |
| `x500_livox_mid_360` | Livox Mid-360 LiDAR | 360° spinning LiDAR |
| `x500_livox_mid_360_down` | Downward Livox LiDAR | Ground mapping |
| `x500_mono_cam` | Monocular camera | Forward-facing camera |
| `x500_mono_cam_down` | Downward camera | Ground observation |
| `x500_vision` | Vision processing | Multiple cameras |
| `x500_slung_payload` | Slung payload ops | Includes tether_cable + payload |

**Common Inheritance Pattern:**
```
x500_base (airframe)
    ↓ (include + merge)
x500 (+ motors + basic sensors)
    ↓ (include + additional sensors)
x500_[variant] (+ specialized payload)
```

**Key Files:**
- All variants reference: `models/x500_base/model.sdf`
- Sensor plugins: `models/x500/model.sdf`
- Specialized payloads: Individual variant directories

---

## Tuning Recommendations

### For Realistic Physics Simulation

**1. Update Motor Parameters (Recommended):**
```xml
<!-- Replace in x500_base/model.sdf -->
<maxRotVelocity>1363.9</maxRotVelocity>
<!-- Calculation: 880 KV × 14.8V × 2π/60 = 1363.87 rad/s -->

<motorConstant>5.50e-06</motorConstant>
<!-- Balanced TWR = 2.0:1, hover at 50% throttle -->

<momentConstant>0.00254</momentConstant>
<!-- From thrust bench data: Q/F ratio -->

<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
<!-- Corrected for realistic propeller drag -->
```

**2. Performance Scenarios:**

**Conservative (Stable Hover):**
```xml
<motorConstant>4.34e-06</motorConstant>  <!-- TWR = 1.65:1 -->
<maxRotVelocity>1200</maxRotVelocity>    <!-- Limit to 88% max RPM -->
```

**Aggressive (Aerobatic):**
```xml
<motorConstant>6.70e-06</motorConstant>  <!-- TWR = 2.5:1 -->
<maxRotVelocity>1363.9</maxRotVelocity>  <!-- Full motor capability -->
```

**3. Controller Tuning (PX4 Parameters):**

For new motor constants, re-tune:
- `MC_ROLLRATE_P`, `MC_PITCHRATE_P`: Reduce if TWR increases
- `MC_ROLLRATE_D`, `MC_PITCHRATE_D`: Increase for higher responsiveness
- `MPC_THR_HOVER`: Adjust to new hover throttle % (e.g., 0.50 for TWR=2.0)

**4. Payload Capacity Testing:**

Test incremental payload increases:
```bash
# Edit models/payload/model.sdf.jinja
{%- set payload_mass = 0.4 -%}  # Start here
{%- set payload_mass = 0.8 -%}  # Medium test
{%- set payload_mass = 1.2 -%}  # Stress test
{%- set payload_mass = 1.5 -%}  # Maximum test
```

Monitor:
- Hover throttle % (should stay < 70%)
- Altitude hold stability
- Oscillations during aggressive maneuvers

---

## Reference Documentation

**Primary Sources:**
- Model SDF: `/models/x500_base/model.sdf`
- Motor SDF: `/models/x500/model.sdf`
- PX4 Docs: `/flightcontroller/uav-flightcontroller-PX4/docs/en/frames_multicopter/holybro_x500_pixhawk4.md`

**Related Analysis:**
- Tarot650 Motor Guide: `/models/Tarot650_base/MOTOR_PARAMETERS_GUIDE.md`
- Thrust Bench Data: `/models/Tarot650_base/ANALYSIS_RESULTS.md`

**Hardware References:**
- NXP HoverGames Kit: https://www.nxp.com/design/designs/px4-robotic-drone-fmu-rddrone-fmuk66
- T-Motor 2216: https://store.tmotor.com/goods-291-MN2216+KV880.html
- Holybro X500 V2: https://holybro.com/products/x500-v2-kit

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Author:** Generated from model analysis
**Model Version:** Gazebo Harmonic (gz-sim8)
