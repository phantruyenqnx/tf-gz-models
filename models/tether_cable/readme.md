# Tether cable model

A segmented tether + slung-payload model for gz-sim, generated from a Jinja template.

## Model structure

```
Link_attach -> joint_sphere(universal)_1 -> link_1 -> joint_sphere(universal) -> ...
            -> link_{n-1} -> joint_sphere(universal)_n -> link_n -> joint(fixed) -> Sphere_payload
```

**Part 1 — `Link_attach`:** 5 cm long, 3 cm radius, 200 g mass. Starts vertical, 5 cm
above the ground.

**Part 2 — the tether cable** (everything from `joint_sphere(universal)_1` through
`link_n`):

- Cable diameter: `d = 6 mm`
- Cable length: `l = 3 m`
- Cable mass: `m = 3/47 kg`
- Number of segments: `n = 100`
- The cable starts horizontal along the **Y axis**, lying on the ground.
- Links are colored **gray**; joints are colored **gray**.
- Links have `self_collide = true`.
- Keep the physics realistic:
  ```jinja
  {%- set damping = 0.001 -%}    {#- Realistic damping coefficient -#}
  {%- set friction = 0.001 -%}   {#- Realistic friction coefficient -#}
  ```
- The whole cable must weigh about `3/47 kg ≈ 63.83 g`. Distribute the mass across the
  links and joints sensibly, and keep the inertia matrices sensible.

**Part 3 — `Sphere_payload`:** 500 g mass, 5 cm radius. Starts on the ground.

### Joints between tether segments (template excerpt)

```jinja
{# Joints between tether segments #}
{% for k in range(1, number_elements) -%}
  {%- set parent_idx = k - 1 -%}
  {% if joint_type == 'revolute_alt' %}
    {{ revolute_joint_alternating('joint_' ~ k, 'link_' ~ parent_idx, 'link_' ~ k, k) }}
  {% else %}
    {{ universal_joint('joint_' ~ k, 'link_' ~ parent_idx, 'link_' ~ k) }}
  {% endif %}
{% endfor -%}
```

## Generating `model.sdf` from the template

Render a `.sdf.jinja` template with `jinja_gen.py` (it writes `model.sdf` next to the
template):

```bash
python3 simulation/UAV-gazebo-models/models/slung_payload/jinja_gen.py \
        simulation/UAV-gazebo-models/models/slung_payload/tether_slung_payload.sdf.jinja \
        simulation/UAV-gazebo-models/models/slung_payload/
```

## Spawning into a running Gazebo world

Example `gz service` calls (adjust the absolute `sdf_filename` paths to your checkout):

```bash
gz service -s /world/default/create --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'sdf_filename: ".../models/slung_payload/tether_slung_payload.sdf", name: "tether_payload", pose: {position: {x: 0.0, y: 0.0, z: 0.0}}'

gz service -s /world/default/create --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'sdf_filename: ".../models/Tarot650_base/model.sdf", name: "tarot_x650", pose: {position: {x: 0.0, y: 0.0, z: 0.0}}'

gz service -s /world/default/create --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean --timeout 1000 \
  --req 'sdf_filename: ".../models/x500_slung_payload/model.sdf", name: "x500_slung_payload", pose: {position: {x: 0.0, y: 0.0, z: 0.0}}'
```

---

# Damping in nature

## Damping ratio (ζ) — dimensionless

Instead of a `damping coefficient` (which depends on mass and stiffness), use the
**damping ratio**:

```
ζ = b / (2√(km))
```

| ζ value | State | Characteristics |
|---------|-------|-----------------|
| ζ = 0 | Undamped | Oscillates forever |
| 0 < ζ < 1 | Under-damped | Decaying oscillation |
| ζ = 1 | Critically damped | Returns to rest fastest |
| ζ > 1 | Over-damped | Slow, no oscillation |

---

## Natural phenomena

### 1. Air damping

**Small objects in air:**
```
ζ ≈ 0.001 - 0.01
```
- Falling feather: ζ ≈ 0.8 - 1.5 (over-damped)
- Tennis ball: ζ ≈ 0.02 - 0.05
- Simple pendulum: ζ ≈ 0.001 - 0.005
- Very low damping → long-lasting oscillation

**Damping coefficient in air:**
```
b = 6πηr  (Stokes drag)
```
- η: air viscosity ≈ 1.8 × 10⁻⁵ Pa·s
- r: object radius

**Concrete example:**
- φ8mm cable in air:
  - η = 1.8 × 10⁻⁵ Pa·s
  - r = 4 mm = 0.004 m
  - b ≈ 6π × 1.8×10⁻⁵ × 0.004 ≈ 1.36 × 10⁻⁶ N·s/m
  - **Very small!**

---

### 2. Water damping

```
ζ ≈ 0.05 - 0.3
```
- Pendulum in water: ζ ≈ 0.1 - 0.2
- Swimming fish: ζ ≈ 0.3 - 0.5
- Water is **~55×** more viscous than air
- η_water ≈ 1.0 × 10⁻³ Pa·s

---

### 3. Elastic materials

| Material | ζ | Application |
|----------|---|-------------|
| **Steel** | 0.001 - 0.003 | Bridges, buildings |
| **Aluminium** | 0.0005 - 0.002 | Aircraft |
| **Rubber** | 0.05 - 0.2 | Shock absorbers |
| **Wood** | 0.01 - 0.05 | Wooden houses |
| **Concrete** | 0.02 - 0.08 | Construction |

---

### 4. Cable / tether

**Steel cable:**
```
ζ ≈ 0.002 - 0.01
Material damping: very low
Air damping: dominant
```

**Nylon / polymer cable:**
```
ζ ≈ 0.02 - 0.05
Material damping: higher (polymer)
```

**Kevlar cable:**
```
ζ ≈ 0.005 - 0.015
```

**Damping sources for a tether:**
1. **Internal material damping** — very small (ζ < 0.01)
2. **Air drag** — dominant (depends on velocity²)
3. **Bending damping** — when the cable bends

---

## Computing damping for the tether cable

### Combined formula

```python
# 1. Material damping (internal)
ζ_material = 0.005  # for steel / nylon cable

# 2. Air drag damping (external)
ρ_air = 1.225  # kg/m³
C_d = 1.2      # drag coefficient (cylinder)
D = 0.008      # cable diameter (m)
L = 0.1        # segment length (m)
A = D * L      # cross-section area
m = 0.001      # segment mass (kg)
v = 1.0        # velocity (m/s)

# Drag force
F_drag = 0.5 * ρ_air * v² * C_d * A

# Damping coefficient
b_air = F_drag / v
      = 0.5 * 1.225 * 1.2 * 0.008 * 0.1
      = 5.88 × 10⁻⁴ N·s/m

# With spring stiffness k = 0.01 N/m
b_critical = 2 * √(k * m)
           = 2 * √(0.01 * 0.001)
           = 6.32 × 10⁻³

# Damping ratio
ζ_air = b_air / b_critical
      = 5.88×10⁻⁴ / 6.32×10⁻³
      ≈ 0.093
```

### Total damping
```
ζ_total = ζ_material + ζ_air
        ≈ 0.005 + 0.093
        ≈ 0.098 ≈ 0.1
```

---

## Comparing the current code with nature

### Current code
```python
damping = 0.05
spring_stiffness = 0.01
m = 0.001

b_critical = 2 * √(0.01 * 0.001) = 0.00632

ζ = 0.05 / 0.00632 ≈ 7.9
```

### ⚠️ Problem
```
ζ ≈ 7.9 >> 1 → HEAVILY OVER-DAMPED!
```

About **79× higher** than nature.

---

## Practical values for the tether

### In still air
```xml
<damping>0.0005</damping>  <!-- ζ ≈ 0.08 - close to real -->
```

### In wind / fast flight
```xml
<damping>0.002</damping>   <!-- ζ ≈ 0.3 - accounts for air drag -->
```

### For a stable simulation
```xml
<damping>0.01</damping>    <!-- ζ ≈ 1.5 - critically damped -->
```

---

## Measuring damping experimentally

### Method 1: logarithmic decrement

```
Excite the oscillation and measure the amplitudes:

A₁, A₂, A₃, A₄...

δ = ln(A₁/A₂)  # logarithmic decrement

ζ = δ / √(4π² + δ²)
```

**Experimental example:**
- Pull the tether and release.
- Measure the oscillation:
  - A₁ = 10 cm
  - A₂ = 8 cm (after one period)

```python
δ = ln(10/8) = 0.223
ζ = 0.223 / √(4π² + 0.223²)
  = 0.223 / 6.283
  ≈ 0.0355
```

→ Natural damping ratio ≈ **0.03 - 0.04**

---

### Method 2: Gazebo experiment

```python
# Test the values
damping_tests = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05]

# For each value:
1. Spawn the tether
2. Raise the drone
3. Release
4. Count the oscillations before it stops
5. Compare against real footage
```

**Expected results:**
- `damping = 0.0001`: 20-30 oscillations
- `damping = 0.001`: 5-10 oscillations ← **close to real**
- `damping = 0.01`: 1-2 oscillations
- `damping = 0.05`: no oscillation

---

## Summary table

| Environment | ζ (damping ratio) | b (N·s/m) for φ8mm tether |
|-------------|-------------------|---------------------------|
| **Vacuum** | 0.0001 | ~10⁻⁷ |
| **Still air** | 0.005 - 0.01 | 3×10⁻⁵ - 6×10⁻⁵ |
| **Low-speed flight** | 0.02 - 0.05 | 1×10⁻⁴ - 3×10⁻⁴ |
| **High-speed flight** | 0.1 - 0.3 | 6×10⁻⁴ - 2×10⁻³ |
| **In water** | 0.5 - 1.0 | 3×10⁻³ - 6×10⁻³ |

---

## Recommended code changes

### Option 1: Realistic (hard to stabilise)
```xml
<damping>0.001</damping>  <!-- ζ ≈ 0.16 - close to nature -->
<max_step_size>0.0001</max_step_size>  <!-- needs a small timestep -->
```

### Option 2: Balanced (recommended)
```xml
<damping>0.005</damping>  <!-- ζ ≈ 0.8 - balanced -->
<max_step_size>0.001</max_step_size>
```

### Option 3: Stable (current, OK)
```xml
<damping>0.05</damping>   <!-- ζ ≈ 8 - very stable -->
<!-- change to 0.01 for a slightly more natural feel -->
```

---

## Summary

**In nature:**
- A cable in air: **ζ ≈ 0.005 - 0.05**
- Damping comes mostly from **air drag**, not the material.

**The current code:**
- `damping = 0.05` → **ζ ≈ 7.9** → higher than nature
- Good for stability but not realistic.

**Recommendation:**
```xml
<damping>0.001</damping>  <!-- for close-to-real -->
<damping>0.005</damping>  <!-- best balance -->
<damping>0.01</damping>   <!-- stable, acceptable -->
```
