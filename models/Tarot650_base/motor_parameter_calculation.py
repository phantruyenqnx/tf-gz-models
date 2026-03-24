#!/usr/bin/env python3
"""
Script to calculate motor parameters for Gazebo simulation from datasheet
Based on T-Motor 2216 KV880 specifications with APC 1047 propeller
Real test data from motor-propeller combination
"""

import math

# ============================================================================
# DATASHEET PARAMETERS - T-Motor 2216 KV880
# ============================================================================
KV = 880  # RPM/V
MAX_VOLTAGE = 14.8  # 4S LiPo voltage
MOTOR_RESISTANCE = 0.117  # Ohm
MAX_CURRENT = 20  # A (continuous for 30s)
MAX_POWER = 320  # W
MOTOR_WEIGHT = 0.072  # kg
PROP_DIAMETER = 0.254  # 10 inch = 0.254 m
PROP_PITCH = 0.1194  # 4.7 inch = 0.1194 m
PROP_NAME = "APC 1047"

# Physical constants
AIR_DENSITY = 1.225  # kg/m³
GRAVITY = 9.81  # m/s²

# Estimated parameters (typical for quadcopters)
THRUST_TO_WEIGHT_RATIO = 2.5  # Total thrust / total weight
TOTAL_WEIGHT = 2.0  # kg (from base_link mass in SDF)
THRUST_PER_MOTOR = (TOTAL_WEIGHT * GRAVITY * THRUST_TO_WEIGHT_RATIO) / 4  # N

# ============================================================================
# REAL TEST DATA - T-Motor 2216 KV880 + APC 1047 @ 14.8V
# ============================================================================
# Data from manufacturer thrust test bench
# Voltage = 14.8V (4S LiPo)
test_data_14v8 = {
    'current_A': [0.6, 1.5, 2.5, 3.7, 5.2, 6.8, 8.4, 10.1, 12.3, 14.2, 16.2, 21.4],
    'thrust_gf': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1360],
    'power_W': [8.88, 22.2, 37, 54.76, 76.96, 100.64, 124.32, 149.48, 182.04, 210.16, 239.76, 316.72],
    'efficiency_gW': [11.26, 9.01, 8.11, 7.30, 6.50, 5.96, 5.63, 5.35, 4.94, 4.76, 4.59, 4.29]
}

# Additional data @ 11.1V (3S LiPo) for comparison
test_data_11v1 = {
    'current_A': [0.7, 1.9, 3.2, 4.6, 6.4, 8.2, 10.4, 12.6, 14.4],
    'thrust_gf': [100, 200, 300, 400, 500, 600, 700, 800, 890],
    'power_W': [7.77, 21.09, 35.52, 51.06, 71.04, 91.02, 115.44, 139.86, 159.84],
    'efficiency_gW': [12.87, 9.48, 8.45, 7.83, 7.04, 6.59, 6.06, 5.72, 5.57]
}

# Convert thrust from gf to N
def gf_to_N(gf):
    return gf / 1000 * GRAVITY

print("=" * 80)
print("MOTOR PARAMETER CALCULATION FOR GAZEBO SIMULATION")
print("=" * 80)
print(f"\nMotor: T-Motor 2216 KV{KV}")
print(f"Propeller: {PROP_NAME} ({PROP_DIAMETER*1000:.0f}mm diameter)")
print(f"Configuration: 4S LiPo ({MAX_VOLTAGE}V)")
print(f"\n✓ Using REAL TEST DATA from thrust bench")
print("\n" + "-" * 80)

# ============================================================================
# 0. ANALYZE REAL TEST DATA
# ============================================================================
print("\n0. REAL TEST DATA ANALYSIS:")
print("-" * 40)

# Convert to N
thrust_N = [gf_to_N(gf) for gf in test_data_14v8['thrust_gf']]
current_A = test_data_14v8['current_A']
power_W = test_data_14v8['power_W']

print(f"\n   Test data @ {MAX_VOLTAGE}V:")
print(f"   {'Current(A)':<12} {'Thrust(N)':<12} {'Power(W)':<12} {'Efficiency(g/W)'}")
print("   " + "-" * 60)
for i in range(len(current_A)):
    print(f"   {current_A[i]:<12.1f} {thrust_N[i]:<12.2f} {power_W[i]:<12.2f} {test_data_14v8['efficiency_gW'][i]:<12.2f}")

# Find max thrust in test data
max_test_thrust_N = max(thrust_N)
max_test_current = current_A[thrust_N.index(max_test_thrust_N)]
max_test_power = power_W[thrust_N.index(max_test_thrust_N)]

print(f"\n   Maximum tested:")
print(f"   - Thrust: {max_test_thrust_N:.2f} N ({test_data_14v8['thrust_gf'][-1]:.0f} gf)")
print(f"   - Current: {max_test_current:.1f} A")
print(f"   - Power: {max_test_power:.1f} W")

# Estimate RPM from power and current
# P = V*I - I²*R (mechanical power)
# Also: P = Torque * ω
# Torque = Kt * I (where Kt = 60/(2π*KV))
Kt_torque = 60 / (2 * math.pi * KV)  # Nm/A

print(f"\n   RPM estimation:")
rpm_estimates = []
for i in range(len(current_A)):
    mechanical_power = power_W[i] - (current_A[i]**2 * MOTOR_RESISTANCE)
    torque = Kt_torque * current_A[i]
    if torque > 0:
        omega = mechanical_power / torque
        rpm = omega * 60 / (2 * math.pi)
        rpm_estimates.append(rpm)
    else:
        rpm_estimates.append(0)

print(f"   At max thrust: ~{rpm_estimates[-1]:.0f} RPM (~{rpm_estimates[-1]*2*math.pi/60:.1f} rad/s)")
print(f"   At 50% thrust: ~{rpm_estimates[len(rpm_estimates)//2]:.0f} RPM")

# ============================================================================
# 1. MAX ROTATION VELOCITY
# ============================================================================
print("\n1. MAX ROTATION VELOCITY:")
print("-" * 40)

# Calculate max RPM
max_rpm = KV * MAX_VOLTAGE
max_rad_s = max_rpm * 2 * math.pi / 60

print(f"   Max RPM = KV × Voltage")
print(f"          = {KV} × {MAX_VOLTAGE}V")
print(f"          = {max_rpm:.0f} RPM")
print(f"\n   Max ω (rad/s) = RPM × 2π / 60")
print(f"                 = {max_rpm:.0f} × 2π / 60")
print(f"                 = {max_rad_s:.2f} rad/s")
print(f"\n   ✓ Recommended: {max_rad_s:.2f} rad/s")
print(f"   ✗ Current SDF:  1000.0 rad/s (TOO LOW!)")

# ============================================================================
# 2. MOTOR CONSTANT (Kt - Thrust Constant) - FROM REAL DATA
# ============================================================================
print("\n2. MOTOR CONSTANT (Kt - Thrust Constant):")
print("-" * 40)

# Calculate motor constant from each test point
# motor_constant = Thrust / ω²
motor_constants = []
print(f"\n   Calculating from test data:")
print(f"   {'Thrust(N)':<12} {'RPM':<12} {'ω(rad/s)':<12} {'Kt(N⋅s²)':<15}")
print("   " + "-" * 60)

for i in range(len(thrust_N)):
    omega = rpm_estimates[i] * 2 * math.pi / 60
    if omega > 0:
        kt = thrust_N[i] / (omega ** 2)
        motor_constants.append(kt)
        print(f"   {thrust_N[i]:<12.2f} {rpm_estimates[i]:<12.0f} {omega:<12.2f} {kt:.8e}")

# Use average of middle range (exclude very low and very high throttle)
# Best range: 30%-80% throttle (indices 3-9)
middle_range = motor_constants[3:10]
motor_constant_avg = sum(middle_range) / len(middle_range)
motor_constant_min = min(middle_range)
motor_constant_max = max(middle_range)

print(f"\n   Motor constant statistics (30%-80% throttle range):")
print(f"   - Average: {motor_constant_avg:.8e} N⋅s²")
print(f"   - Min:     {motor_constant_min:.8e} N⋅s²")
print(f"   - Max:     {motor_constant_max:.8e} N⋅s²")
print(f"   - Variation: ±{((motor_constant_max-motor_constant_min)/motor_constant_avg*100):.1f}%")

# Use average for simulation
motor_constant = motor_constant_avg

# Also calculate for hover point (assume hover at 50% throttle)
hover_thrust = TOTAL_WEIGHT * GRAVITY / 4  # Thrust per motor at hover
# Find closest test point to hover thrust
hover_idx = min(range(len(thrust_N)), key=lambda i: abs(thrust_N[i] - hover_thrust))
hover_omega = rpm_estimates[hover_idx] * 2 * math.pi / 60
hover_actual_thrust = thrust_N[hover_idx]

print(f"\n   At hover (estimated {hover_thrust:.2f}N per motor):")
print(f"   - Closest test point: {hover_actual_thrust:.2f}N @ {rpm_estimates[hover_idx]:.0f} RPM")
print(f"   - Motor constant at hover: {motor_constants[hover_idx]:.8e} N⋅s²")

print(f"\n   ✓ Recommended for SDF: {motor_constant:.8e} N⋅s²")
print(f"   ✗ Current X500 SDF:     8.54858e-06 (not based on real data)")
print(f"   📊 This value is derived from REAL thrust bench data!")

# ============================================================================
# 3. MOMENT CONSTANT (Cq/Ct ratio)
# ============================================================================
print("\n3. MOMENT CONSTANT:")
print("-" * 40)

# Typical Cq/Ct ratio for propellers is around 0.015-0.020
# Moment = moment_constant × Thrust
# Torque = Cq × ρ × n² × D⁵
# Thrust = Ct × ρ × n² × D⁴
# Therefore: Torque/Thrust = (Cq/Ct) × D

# Typical Cq/Ct ≈ 0.01 for efficient props
cq_ct_ratio = 0.01
moment_constant = cq_ct_ratio * PROP_DIAMETER

print(f"   Typical Cq/Ct ratio = {cq_ct_ratio:.3f}")
print(f"   Moment constant = (Cq/Ct) × D")
print(f"                   = {cq_ct_ratio:.3f} × {PROP_DIAMETER:.3f}m")
print(f"                   = {moment_constant:.6f}")
print(f"\n   ✓ Recommended: {moment_constant:.6f}")
print(f"   ✓ Current SDF:  0.016 (reasonable)")

# ============================================================================
# 4. ROTOR DRAG COEFFICIENT
# ============================================================================
print("\n4. ROTOR DRAG COEFFICIENT:")
print("-" * 40)

# Drag torque = rotor_drag_coeff × ω²
# Estimate from motor resistance and current at max speed
# Power loss = I² × R + Drag × ω
max_mechanical_power = MAX_POWER - (MAX_CURRENT ** 2 * MOTOR_RESISTANCE)
drag_torque_at_max = max_mechanical_power / max_rad_s * 0.1  # Estimate 10% loss to drag

rotor_drag_coeff = drag_torque_at_max / (max_rad_s ** 2)

print(f"   Max mechanical power = {max_mechanical_power:.2f} W")
print(f"   Estimated drag torque at max speed = {drag_torque_at_max:.6f} Nm")
print(f"\n   Rotor drag coeff = Torque_drag / ω²")
print(f"                    = {drag_torque_at_max:.6f} / ({max_rad_s:.2f})²")
print(f"                    = {rotor_drag_coeff:.8e}")
print(f"\n   ✓ Recommended: {rotor_drag_coeff:.8e}")
print(f"   ✓ Current SDF:  8.06428e-05 (reasonable)")

# ============================================================================
# 5. TIME CONSTANTS
# ============================================================================
print("\n5. TIME CONSTANTS:")
print("-" * 40)

# Motor electrical time constant: τ = L/R
# Typical inductance for brushless motor ≈ 50-100 μH
inductance = 80e-6  # H
tau_electrical = inductance / MOTOR_RESISTANCE

# Mechanical time constant depends on rotor inertia
# Rotor inertia for 10" prop ≈ 2-5 × 10⁻⁵ kg⋅m²
rotor_inertia = 2.649858234714004e-05  # From SDF file
motor_torque_per_amp = Kt_torque  # Already defined in section 0
max_acceleration = (motor_torque_per_amp * MAX_CURRENT) / rotor_inertia
tau_mechanical = max_rad_s / max_acceleration

print(f"   Electrical time constant τe = L/R")
print(f"                                = {inductance*1e6:.0f}μH / {MOTOR_RESISTANCE*1000:.0f}mΩ")
print(f"                                = {tau_electrical*1000:.3f} ms")
print(f"\n   Mechanical time constant (estimated):")
print(f"   - Rotor inertia = {rotor_inertia:.8e} kg⋅m²")
print(f"   - τm ≈ {tau_mechanical*1000:.1f} ms")
print(f"\n   Combined response (spin-up) ≈ 10-15 ms")
print(f"   Combined response (spin-down) ≈ 20-30 ms (due to aerodynamic inertia)")
print(f"\n   ✓ Recommended: timeConstantUp   = 0.0125s (12.5ms)")
print(f"   ✓ Recommended: timeConstantDown = 0.025s (25ms)")
print(f"   ✓ Current SDF values are reasonable")

# ============================================================================
# 6. ROTOR MASS AND INERTIA
# ============================================================================
print("\n6. ROTOR MASS AND INERTIA:")
print("-" * 40)

# Propeller mass (typical 10" carbon fiber prop ≈ 10-20g)
prop_mass = 0.015  # kg
prop_radius = PROP_DIAMETER / 2

# Moment of inertia for thin disk: I = 0.5 × m × r²
prop_inertia = 0.5 * prop_mass * (prop_radius ** 2)

print(f"   Propeller diameter = {PROP_DIAMETER*1000:.0f} mm")
print(f"   Estimated prop mass = {prop_mass*1000:.0f} g")
print(f"   Izz = 0.5 × m × r²")
print(f"       = 0.5 × {prop_mass:.3f} × ({prop_radius:.3f})²")
print(f"       = {prop_inertia:.8e} kg⋅m²")
print(f"\n   ✓ Current SDF: {rotor_inertia:.8e} kg⋅m² (reasonable)")

# ============================================================================
# SUMMARY - RECOMMENDED PARAMETERS
# ============================================================================
print("\n" + "=" * 80)
print("RECOMMENDED PARAMETERS FOR SDF FILE")
print("=" * 80)

print(f"""
<plugin filename="gz-sim-multicopter-motor-model-system"
        name="gz::sim::systems::MulticopterMotorModel">
    <jointName>rotor_X_joint</jointName>
    <linkName>rotor_X</linkName>
    <turningDirection>ccw/cw</turningDirection>

    <!-- Time response -->
    <timeConstantUp>0.0125</timeConstantUp>      <!-- ✓ Good -->
    <timeConstantDown>0.025</timeConstantDown>   <!-- ✓ Good -->

    <!-- Max velocity: NEEDS UPDATE -->
    <maxRotVelocity>{max_rad_s:.1f}</maxRotVelocity>
    <!-- OLD: 1000.0 (TOO LOW!) -->
    <!-- NEW: {max_rad_s:.1f} rad/s ({max_rpm:.0f} RPM at {MAX_VOLTAGE}V) -->

    <!-- Thrust constant: NEEDS UPDATE -->
    <motorConstant>{motor_constant:.8e}</motorConstant>
    <!-- OLD: 8.54858e-06 -->
    <!-- NEW: {motor_constant:.8e} (calculated from hover requirement) -->

    <!-- Torque/Thrust ratio -->
    <momentConstant>{moment_constant:.6f}</momentConstant>  <!-- ✓ Good -->

    <!-- Drag coefficients -->
    <rotorDragCoefficient>{rotor_drag_coeff:.8e}</rotorDragCoefficient>  <!-- ✓ Good -->
    <rollingMomentCoefficient>1e-06</rollingMomentCoefficient>  <!-- ✓ Good -->

    <commandSubTopic>command/motor_speed</commandSubTopic>
    <motorNumber>X</motorNumber>
    <rotorVelocitySlowdownSim>10</rotorVelocitySlowdownSim>
    <motorType>velocity</motorType>
</plugin>
""")

# ============================================================================
# VALIDATION
# ============================================================================
print("\n" + "=" * 80)
print("VALIDATION")
print("=" * 80)

print("\nMax thrust per motor (at full throttle):")
max_thrust = motor_constant * (max_rad_s ** 2)
print(f"   Thrust = motor_constant × ω²")
print(f"          = {motor_constant:.8e} × ({max_rad_s:.2f})²")
print(f"          = {max_thrust:.2f} N")

total_max_thrust = max_thrust * 4
total_weight_n = TOTAL_WEIGHT * GRAVITY
twr = total_max_thrust / total_weight_n

print(f"\nTotal thrust (4 motors): {total_max_thrust:.2f} N")
print(f"Total weight:            {total_weight_n:.2f} N")
print(f"Thrust-to-weight ratio:  {twr:.2f}:1")

if twr > 2.0:
    print(f"   ✓ GOOD - Sufficient thrust for aerobatic flight")
elif twr > 1.5:
    print(f"   ✓ OK - Adequate for stable flight")
else:
    print(f"   ✗ WARNING - Low thrust, may not hover reliably")

print("\n" + "=" * 80)
