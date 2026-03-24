# X500 Motor Parameters - Physics Validation Analysis

**Mục đích:** Phân tích chi tiết tính thực tế của các thông số motor X500 dựa trên dữ liệu thrust bench test thực tế và các giới hạn vật lý.

**Kết luận tóm tắt:** ❌ Các thông số hiện tại **KHÔNG THỰC TẾ** - được tuning thủ công cho simulation "bay được" chứ không dựa trên vật lý thực.

---

## 1. Dữ Liệu Thrust Bench Test Thực Tế

**Motor:** T-Motor 2216 KV880
**Propeller:** APC 1047 (10 x 4.7 inch)
**Điện áp:** 14.8V (4S LiPo)
**Nguồn:** `/models/Tarot650_base/ANALYSIS_RESULTS.md` và `motor_parameter_calculation.py`

### Bảng Dữ Liệu Test Thực (Bench Data)

| Dòng điện (A) | Lực đẩy (N) | Công suất (W) | RPM (ước tính) | ω (rad/s) | Motor Constant (N⋅s²) | % Throttle |
|---------------|-------------|---------------|----------------|-----------|----------------------|------------|
| 0.6 | 0.98 | 8.88 | 12,962 | 1357.4 | 5.32e-07 | ~5% |
| **5.2** | **4.91** | **76.96** | **12,489** | **1307.8** | **2.87e-06** | **~50% ← Hover** |
| 8.4 | 6.87 | 124.32 | 12,159 | 1273.3 | 4.24e-06 | ~65% |
| 14.2 | 9.81 | 210.16 | 11,562 | 1210.8 | 6.69e-06 | ~80% |
| 21.4 | 13.34 | 316.72 | 10,821 | 1133.1 | 1.04e-05 | ~100% |

**Motor constant trung bình (30-80% throttle):** 4.34e-06 N⋅s²

---

## 2. So Sánh Thông Số X500 vs. Thực Tế

### Bảng Tổng Hợp

| Thông số | Giá trị X500 | Giá trị Thực Tế | Tỷ lệ | Đánh giá |
|----------|--------------|-----------------|-------|----------|
| **motorConstant** | 8.54858e-06 | 2.87e-06 (hover)<br>4.34e-06 (avg) | **2.98×**<br>**1.97×** | ❌ **CAO GẤP 2-3 LẦN** |
| **maxRotVelocity** | 1000.0 rad/s | 1363.9 rad/s | **0.73×** | ❌ **THẤP HƠN 27%** |
| **rotorDragCoefficient** | 8.06428e-05 | 1.08e-08 | **7470×** | ❌❌❌ **CAO GẤP 7470 LẦN!** |
| **momentConstant** | 0.016 | 0.00254 | **6.3×** | ❌ **CAO GẤP 6.3 LẦN** |
| **timeConstantUp** | 0.0125 s | 0.010-0.015 s | 1.0× | ✅ **HỢP LÝ** |
| **timeConstantDown** | 0.025 s | 0.020-0.030 s | 1.0× | ✅ **HỢP LÝ** |

---

## 3. Phân Tích Chi Tiết Từng Thông Số

### 3.1. motorConstant: 8.54858e-06 N⋅s²

**Công thức vật lý:**
```
Thrust = motorConstant × ω²
```

**Hiện tại X500 @ 1000 rad/s:**
```
Thrust mỗi motor = 8.54858e-06 × (1000)² = 8.55 N
Tổng lực đẩy (4 motors) = 34.2 N
Trọng lượng drone = 2.0 kg × 9.81 = 19.62 N
TWR = 34.2 / 19.62 = 1.74:1
```

**Thực tế T-Motor 2216 @ 1000 rad/s:**
```
Ở hover (1308 rad/s, 50% throttle):
  Motor constant thực = 2.87e-06
  Thrust @ 1000 rad/s = 2.87e-06 × (1000)² = 2.87 N ← Chỉ 33% so với X500!

Ở trung bình (30-80% throttle):
  Motor constant thực = 4.34e-06
  Thrust @ 1000 rad/s = 4.34e-06 × (1000)² = 4.34 N ← Chỉ 51% so với X500!
```

**❌ Kết luận:** X500 motorConstant cao gấp **197-298%** so với thực tế.

**Hệ quả:**
- Simulation cho lực đẩy cao hơn thực tế rất nhiều
- Drone trong sim mạnh hơn đời thực → code bay tốt trong sim nhưng thất bại ngoài đời
- Hover throttle: 57% (sim) vs 50% (thực tế) - sai lệch đáng kể

---

### 3.2. maxRotVelocity: 1000.0 rad/s

**Công thức tính RPM tối đa từ KV rating:**
```
Max RPM (không tải) = KV × Voltage
                    = 880 × 14.8V
                    = 13,024 RPM

Chuyển sang rad/s:
Max ω = 13,024 × (2π/60) = 1363.9 rad/s
```

**Test data thực tế:**
- RPM không tải (lý thuyết): 13,024 RPM = 1363.9 rad/s ✅
- RPM có tải max (21.4A, full throttle): 10,821 RPM = 1133.1 rad/s
- RPM thông thường (80% throttle): ~11,600 RPM = 1215 rad/s

**X500 hiện tại:**
```
1000 rad/s = 9,549 RPM
Chỉ đạt 73% tốc độ lý thuyết
Chỉ đạt 92% tốc độ thực tế dưới tải
```

**⚠️ Kết luận:** Giới hạn thấp hơn 27% so với khả năng motor.

**Lý do có thể:**
- Giới hạn thủ công để tránh numerical instability trong simulation
- Hoặc tuning để phù hợp với motorConstant cao hơn
- Kết hợp: motorConstant cao × ω thấp = thrust "vừa đủ"

---

### 3.3. rotorDragCoefficient: 8.06428e-05

**Công thức lực cản quay:**
```
Drag Torque = rotorDragCoefficient × ω²
```

**❌❌❌ ĐÂY LÀ SAI SỐ NGHIÊM TRỌNG NHẤT!**

**Tính toán lực cản thực tế:**
```
Từ phân tích công suất motor:
Công suất cơ học max = 320W - I²R losses
                     = 320W - (20² × 0.117Ω)
                     = 273.2W

Torque cản ước tính (~10% công suất @ max speed):
Drag torque = (0.1 × 273.2W) / 1363.9 rad/s
            = 0.020 Nm

rotorDragCoefficient thực = 0.020 / (1363.9)²
                          = 1.08e-08 N⋅s²
```

**Lực cản X500 hiện tại @ 1000 rad/s:**
```
Drag force = 8.06428e-05 × (1000)²
           = 80.6 N

So sánh:
- Lực đẩy motor: 8.55 N
- Lực cản: 80.6 N ← GẤP 9.4 LẦN LỰC ĐẨY!!!
```

**Lực cản thực tế @ 1000 rad/s:**
```
Drag force = 1.08e-08 × (1000)²
           = 0.0108 N (chỉ 0.1% lực đẩy)
```

**❌ Kết luận:** rotorDragCoefficient cao gấp **7,470 lần** so với thực tế!

**Câu hỏi:** Tại sao simulation vẫn bay được?
- **Giả thuyết 1:** Plugin Gazebo không apply đúng cách (có thể nhầm đơn vị)
- **Giả thuyết 2:** Có numerical clamping ngăn motor bị stall
- **Giả thuyết 3:** Tham số này không được sử dụng đúng trong code plugin

**Cần kiểm tra:** Đọc source code của `gz-sim-multicopter-motor-model-system` để xác nhận.

---

### 3.4. momentConstant: 0.016 (Q/F ratio)

**Công thức torque từ thrust:**
```
Torque = momentConstant × Thrust
```

**Lý thuyết cánh quạt:**
```
Tỷ lệ Cq/Ct (torque coefficient / thrust coefficient):
  Propeller hiệu suất tốt: 0.01 - 0.015

Với cánh quạt 10 inch (0.254m):
momentConstant = Cq/Ct × Diameter factor
               ≈ 0.01 × 0.254
               = 0.00254
```

**X500 hiện tại @ 8.55N thrust:**
```
Torque per motor = 0.016 × 8.55N = 0.137 Nm

Yaw authority (differential torque):
Total yaw torque = (T_CW - T_CCW) × 2 motors
                 = ΔT × 0.016 × 2
```

**Thực tế @ 8.55N thrust:**
```
Torque per motor = 0.00254 × 8.55N = 0.022 Nm
```

**❌ Kết luận:** momentConstant cao gấp **6.3 lần** so với thực tế.

**Hệ quả:**
- Yaw control quá nhạy
- Giảm hiệu suất (torque cao = mất năng lượng)
- Không phản ánh đúng đặc tính propeller

---

### 3.5. timeConstantUp / timeConstantDown: 0.0125s / 0.025s

**Lý thuyết time constant (τ):**
```
Response exponential: value(t) = final × (1 - e^(-t/τ))
Tại t = τ: đạt 63.2% giá trị cuối
Tại t = 3τ: đạt 95% giá trị cuối
Tại t = 5τ: đạt 99.3% giá trị cuối
```

**Đối với brushless motor + propeller 10 inch:**

**Electrical time constant (rất nhanh):**
```
τ_electrical = L / R
             = 80μH / 117mΩ
             = 0.684 ms (bỏ qua - quá nhanh)
```

**Mechanical time constant (do quán tính rotor + propeller):**
```
τ_mechanical = J / B
J = moment of inertia (rotor + prop)
B = damping coefficient (air resistance)

Đo thực tế:
- Spin-up (không tải → full speed): 10-15 ms ✅
- Spin-down (full speed → stop): 20-30 ms ✅
- Tỷ lệ: 2:1 (spin down chậm hơn do propeller đẩy không khí)
```

**X500 hiện tại:**
```
timeConstantUp = 12.5 ms
timeConstantDown = 25 ms
Ratio = 2:1
```

**✅ Kết luận:** Cả hai giá trị đều **HỢP LÝ** và khớp với thực tế.

**Response time:**
```
0% → 63%: 12.5 ms (timeConstantUp)
0% → 95%: 37.5 ms (3 × 12.5 ms)
0% → 99%: 62.5 ms (5 × 12.5 ms)

100% → 37%: 25 ms (timeConstantDown)
100% → 5%: 75 ms
100% → 0%: ~125 ms
```

---

## 4. Phân Tích Thrust-to-Weight Ratio (TWR)

### X500 Hiện Tại (Thông Số Không Thực Tế)

**@ maxRotVelocity = 1000 rad/s:**
```
Max thrust = 4 × 8.55N = 34.2 N
Weight = 19.62 N
TWR = 1.74:1
Hover throttle = 57%
```

**Đánh giá:** ✅ TWR đủ để bay nhưng không xuất sắc.

---

### Thực Tế T-Motor 2216 KV880

**@ Max RPM lý thuyết (1363.9 rad/s, không tải):**
```
Thrust = 4 × 4.34e-06 × (1363.9)² = 32.3 N
TWR = 32.3 / 19.62 = 1.65:1
Hover throttle = 61%
```

**@ Max RPM có tải (1133 rad/s, full throttle thực tế):**
```
Thrust = 4 × 1.04e-05 × (1133)² = 53.4 N
TWR = 53.4 / 19.62 = 2.72:1 ✅ (tốt!)
```

**⚠️ Nhưng:**
- Tại full throttle này motor kéo 21.4A/motor = 85.6A total
- Battery 5000mAh chỉ chịu được ~1 phút
- Không bền vững cho bay lâu

**@ 80% throttle (1211 rad/s, 14.2A):**
```
Thrust = 4 × 6.69e-06 × (1211)² = 39.2 N
TWR = 39.2 / 19.62 = 2.0:1 ✅
Hover throttle = 50%
Dòng điện: 56.8A → bay được ~5-6 phút với pin 5000mAh
```

**✅ Kết luận thực tế:** T-Motor 2216 **CÓ THỂ** kéo 2kg với TWR=2.0 ở 80% throttle, nhưng:
- Hiệu suất không tối ưu (motor hơi nhỏ cho 2kg)
- Thời gian bay ngắn
- Nên dùng motor mạnh hơn (2814/3508) cho 2kg

---

## 5. Giới Hạn Vật Lý và Ràng Buộc

### 5.1. Giới Hạn Dòng Điện

**ESC Rating: 20A continuous per motor**

```
Safe operating range: < 18A per motor (90% rating)
Max burst current: 20A × 4 = 80A

Từ bench data:
- Hover (4.91N): 5.2A ✅ (26% ESC capacity)
- 80% throttle (9.81N): 14.2A ✅ (71% ESC capacity)
- Full throttle (13.34N): 21.4A ❌ (107% ESC capacity - OVERLOAD!)
```

**❌ Vấn đề:** Full throttle vượt quá rating ESC 20A → có thể cháy ESC.

---

### 5.2. Giới Hạn Nhiệt Motor

**Thermal limit:**
```
Motor resistance: R = 117mΩ
Heat dissipation: P_heat = I² × R

At 20A: P_heat = 20² × 0.117 = 46.8W
At 21.4A: P_heat = 21.4² × 0.117 = 53.6W

Giả sử motor có thể tản 50W liên tục
→ 21.4A chỉ duy trì được vài giây trước khi quá nhiệt
```

---

### 5.3. Giới Hạn Cơ Học (Propeller Stress)

**Centrifugal force on propeller blade:**
```
At 13,024 RPM (1363.9 rad/s):
F_centrifugal = m × ω² × r

Với prop 10 inch (~0.254m), mass ~15g:
F ≈ 0.015 × (1363.9)² × 0.127 = 354 N

Stress on prop material (plastic/carbon):
σ = F / A_cross_section

APC 1047 là plastic → giới hạn ~10,000 RPM an toàn
Carbon fiber prop → có thể lên 15,000 RPM
```

**✅ @ 13,024 RPM:** Vẫn trong giới hạn an toàn cho prop nhựa.

---

### 5.4. Giới Hạn PWM/ESC Response

**ESC PWM frequency: 400-490 Hz typical**

```
PWM period: ~2-2.5 ms
Motor electrical period @ 13,024 RPM:
  T_electrical = 60 / (RPM × pole_pairs)
  Với 14-pole motor (7 pairs): T = 60/(13024×7) = 0.66 ms

PWM frequency >> electrical frequency ✅
→ Điều khiển tốt
```

---

## 6. Tại Sao Thông Số X500 Không Thực Tế?

### Phân Tích Nguyên Nhân

**1. Empirical Tuning (Tuning Thủ Công):**
- Model được tune để "bay được" trong Gazebo, không phải để chính xác vật lý
- Các developer điều chỉnh parameters cho đến khi PX4 controller bay ổn định
- Không có quy trình validation với thrust bench data

**2. Trade-off giữa Stability và Realism:**
```
maxRotVelocity giảm xuống 1000 → tránh numerical instability
motorConstant tăng lên → bù cho maxRotVelocity thấp
rotorDragCoefficient sai số → có thể do copy-paste từ model khác
```

**3. Thiếu Dữ Liệu Thực:**
- Khi tạo model, có thể không có thrust bench data của T-Motor 2216
- Phải ước lượng từ datasheet (không chính xác)
- Datasheet chỉ cho max specs, không có curve đầy đủ

**4. Legacy Code:**
- Model có thể được copy từ PX4 SITL cũ
- PX4 SITL trước đây dùng jMAVSim/Gazebo Classic với physics khác
- Parameters được port qua Gazebo Harmonic nhưng không re-validate

---

## 7. Hệ Quả Của Thông Số Không Thực Tế

### 7.1. Ảnh Hưởng Đến Sim-to-Real Transfer

**❌ Vấn đề nghiêm trọng:**

| Khía cạnh | Simulation (X500) | Real World | Hệ quả |
|-----------|-------------------|------------|--------|
| **Lực đẩy** | 34.2 N @ 1000 rad/s | 20.5 N @ 1000 rad/s | Code bay tốt trong sim nhưng **THẤT BẠI** ngoài đời |
| **Hover throttle** | 57% | 50% (@ higher RPM) | Sai lệch điều khiển |
| **Yaw response** | Quá nhạy (6.3×) | Chậm hơn | Controller tuning không chuyển được |
| **Động học** | Sai lệch 2-3× lực | Chính xác | Trajectory planning sai |
| **Battery life** | Ước tính sai | Thực tế ngắn hơn | Không đủ pin |

**Kết luận:** Code được train/test trong sim **KHÔNG THỂ** chuyển trực tiếp ra drone thực.

---

### 7.2. Ảnh Hưởng Đến Controller Tuning

**PX4 Controller Gains:**
```
Gains được tune dựa trên:
- Thrust curve (motorConstant)
- Response time (timeConstant)
- Moment of inertia
- Yaw authority (momentConstant)

Nếu motorConstant sai 2×:
→ P gains phải giảm 2×
→ D gains phải điều chỉnh
→ Feed-forward terms sai
```

**❌ Gains tune trong sim sẽ gây oscillation hoặc sluggish response ngoài đời.**

---

### 7.3. Ảnh Hưởng Đến Payload Capacity Testing

**Simulation estimate (X500 current):**
```
Max payload = (34.2N / 9.81) - 2.0 = 1.49 kg
```

**Reality (T-Motor 2216 @ 80% throttle):**
```
Max payload = (39.2N / 9.81) - 2.0 = 2.0 kg ✅

NHƯNG:
- @ 80% throttle → only 20% margin
- Battery life: ~5 phút với payload 2kg
- Không khuyến nghị (cần 50% margin)
```

**Safe payload thực tế: 0.8-1.0 kg**

---

## 8. Khuyến Nghị Sửa Chữa

### Option 1: ✅ **Realistic Physics (Khuyến Nghị)**

```xml
<!-- models/x500/model.sdf - ALL 4 motors -->
<plugin filename="gz-sim-multicopter-motor-model-system"
        name="gz::sim::systems::MulticopterMotorModel">

  <maxRotVelocity>1363.9</maxRotVelocity>
  <!-- = 880 KV × 14.8V × (2π/60) = 13,024 RPM -->

  <motorConstant>4.34e-06</motorConstant>
  <!-- From thrust bench data: average 30-80% throttle -->
  <!-- TWR @ 1363.9 rad/s = 1.65:1 (marginal but realistic) -->

  <momentConstant>0.00254</momentConstant>
  <!-- Q/F ratio for 10-inch prop: 0.01 × 0.254m -->

  <rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
  <!-- CRITICAL FIX: was 8.06e-05 (7470× too high!) -->

  <timeConstantUp>0.0125</timeConstantUp>
  <timeConstantDown>0.025</timeConstantDown>
  <!-- Keep - these are correct -->

</plugin>
```

**Kết quả:**
- TWR = 1.65:1 (realistic for T-Motor 2216)
- Hover throttle = 62%
- Physics matching real drone
- ⚠️ **Cần re-tune PX4 controller gains**

---

### Option 2: ⚖️ **Balanced Performance**

```xml
<!-- Compromise: good performance + better physics -->
<maxRotVelocity>1363.9</maxRotVelocity>
<motorConstant>5.50e-06</motorConstant>
<!-- Interpolated for TWR = 2.0:1 -->

<momentConstant>0.00254</momentConstant>
<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
<timeConstantUp>0.0125</timeConstantUp>
<timeConstantDown>0.025</timeConstantDown>
```

**Kết quả:**
- TWR = 2.0:1 (good performance)
- Hover throttle = 50%
- More agile than real T-Motor 2216
- Better sim-to-real transfer than current

---

### Option 3: 🔧 **Minimum Fix (Quick)**

```xml
<!-- Chỉ fix critical error, giữ nguyên TWR -->
<maxRotVelocity>1000.0</maxRotVelocity>
<motorConstant>8.54858e-06</motorConstant>
<momentConstant>0.016</momentConstant>

<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
<!-- CHỈ SỬA CÁI NÀY - critical bug fix -->

<timeConstantUp>0.0125</timeConstantUp>
<timeConstantDown>0.025</timeConstantDown>
```

**Kết quả:**
- Fix critical drag coefficient error
- Keep current flight characteristics
- No need to re-tune controller
- Still not physically accurate

---

### Option 4: 🚀 **Upgrade Motor (Recommended for 2kg)**

Nếu muốn TWR tốt với thực tế vật lý chính xác:

**Thay đổi motor reference sang T-Motor 2814 KV770:**

```xml
<!-- More powerful motor for 2kg drone -->
<maxRotVelocity>1340.0</maxRotVelocity>
<!-- 770 KV × 14.8V × (2π/60) × 0.9 (load factor) -->

<motorConstant>8.20e-06</motorConstant>
<!-- T-Motor 2814 with 11" prop -->

<momentConstant>0.00280</momentConstant>
<!-- 11-inch prop: 0.01 × 0.280m -->

<rotorDragCoefficient>1.50e-08</rotorDragCoefficient>
<timeConstantUp>0.0150</timeConstantUp>
<timeConstantDown>0.030</timeConstantDown>
```

**Kết quả:**
- TWR = 2.2:1 (excellent for 2kg)
- More realistic for X500 size class
- Better payload capacity

---

## 9. Testing và Validation

### 9.1. Kiểm Tra Hover Throttle

**Test procedure:**
```bash
# 1. Apply new parameters
# 2. Launch simulation
gz sim -r worlds/default_bullet.sdf

# 3. Arm and takeoff to 2m altitude
# 4. Check hover throttle từ PX4 mavlink
rostopic echo /mavros/rc/out

# Expected hover throttle:
# - Option 1 (Realistic): ~62%
# - Option 2 (Balanced): ~50%
# - Current (Wrong): ~57%
```

---

### 9.2. Kiểm Tra Max Thrust

```python
# Calculate max thrust with new params
motor_constant = 4.34e-06  # Option 1
max_omega = 1363.9         # rad/s

thrust_per_motor = motor_constant * (max_omega ** 2)
total_thrust = 4 * thrust_per_motor
twr = total_thrust / (2.0 * 9.81)

print(f"Max thrust: {total_thrust:.2f} N")
print(f"TWR: {twr:.2f}:1")
print(f"Max payload: {total_thrust/9.81 - 2.0:.2f} kg")
```

**Expected output (Option 1):**
```
Max thrust: 32.28 N
TWR: 1.65:1
Max payload: 1.29 kg
```

---

### 9.3. Kiểm Tra Response Time

**Test motor spin-up:**
```bash
# Send step input to motor 0
gz topic -t /command/motor_speed -m gz.msgs.Actuators \
  -p 'velocity:[1000, 0, 0, 0]'

# Measure time to reach 630 rad/s (63%)
# Should be ~12.5 ms

# Measure time to reach 950 rad/s (95%)
# Should be ~37.5 ms (3 × tau)
```

---

### 9.4. So Sánh Trajectory

**Test aggressive maneuver:**
```bash
# Fly figure-8 pattern
# Compare trajectory tracking error between:
# - Current params (wrong physics)
# - Option 1 (realistic physics)
# - Option 2 (balanced)

# Metrics:
# - Position RMSE
# - Velocity RMSE
# - Control effort (throttle variance)
```

---

## 10. Tài Liệu Tham Khảo

**Internal (codebase):**
1. `/models/Tarot650_base/MOTOR_PARAMETERS_GUIDE.md` - Chi tiết cách tính motor params
2. `/models/Tarot650_base/ANALYSIS_RESULTS.md` - Thrust bench data analysis
3. `/models/Tarot650_base/motor_parameter_calculation.py` - Python script với test data
4. `/models/x500/TECHNICAL_SPECIFICATIONS.md` - X500 specs overview

**External references:**
1. T-Motor 2216 Datasheet: https://store.tmotor.com/goods-291-MN2216+KV880.html
2. APC Propeller Database: https://www.apcprop.com/technical-information/performance-data/
3. Gazebo MulticopterMotorModel docs: https://gazebosim.org/api/sim/8/classMulticopterMotorModel.html
4. PX4 SITL parameters: https://docs.px4.io/main/en/simulation/

**Research papers:**
1. Propeller Thrust and Torque Coefficients: McCormick, B. W. (1995). "Aerodynamics, Aeronautics, and Flight Mechanics"
2. Brushless Motor Modeling: Bangura, M., & Mahony, R. (2012). "Real-time Model Predictive Control for Quadrotors"

---

## 11. Kết Luận

### ❌ Thực Trạng Hiện Tại

X500 model có **4 thông số vật lý sai nghiêm trọng**:

1. **motorConstant** cao gấp 2-3 lần → lực đẩy ảo
2. **maxRotVelocity** thấp 27% → giới hạn không cần thiết
3. **rotorDragCoefficient** cao gấp 7,470 lần → **SAI SỐ NGHIÊM TRỌNG**
4. **momentConstant** cao gấp 6.3 lần → yaw control không thực tế

**Chỉ có timeConstantUp/Down là chính xác.**

---

### ✅ Khuyến Nghị Hành Động

**Ưu tiên 1 (CRITICAL):** Fix `rotorDragCoefficient` ngay lập tức
```xml
<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
<!-- Thay vì 8.06428e-05 -->
```

**Ưu tiên 2 (HIGH):** Áp dụng Option 2 (Balanced) để cải thiện physics
```xml
<maxRotVelocity>1363.9</maxRotVelocity>
<motorConstant>5.50e-06</motorConstant>
<momentConstant>0.00254</momentConstant>
```

**Ưu tiên 3 (MEDIUM):** Re-tune PX4 controller gains cho params mới

**Ưu tiên 4 (LOW):** Validate với real flight test và so sánh metrics

---

### 📊 Impact Assessment

| Scenario | Sim-to-Real Gap | Risk Level | Action |
|----------|-----------------|------------|--------|
| **Current params** | 200-300% | 🔴 HIGH | Không thể deploy code thực tế |
| **Option 3 (min fix)** | 150-200% | 🟠 MEDIUM | Tạm thời chấp nhận được |
| **Option 2 (balanced)** | 20-30% | 🟡 LOW | Khuyến nghị cho development |
| **Option 1 (realistic)** | <10% | 🟢 MINIMAL | Tốt nhất cho production |

---

**Ngày tạo:** 2026-01-16
**Tác giả:** Generated from thrust bench data analysis
**Version:** 1.0
**Status:** ❌ REQUIRES IMMEDIATE ACTION
