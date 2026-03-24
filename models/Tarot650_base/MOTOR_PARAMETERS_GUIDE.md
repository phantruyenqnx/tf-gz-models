# Hướng dẫn chuyển đổi thông số động cơ từ Datasheet sang Gazebo Simulation

## Tổng quan

File này giải thích cách chuyển đổi thông số từ datasheet động cơ thực tế (T-Motor 2216 KV880) sang các tham số mô phỏng Gazebo.

---

## Datasheet T-Motor 2216 KV880

### Thông số điện:
- **KV Rating:** 880 RPM/V
- **Motor Resistance:** 117mΩ
- **Max Continuous Current:** 20A (30s)
- **Max Continuous Power:** 320W
- **No-load Current:** 0.5A @ 10V

### Thông số cơ khí:
- **Stator Diameter:** 22mm
- **Stator Thickness:** 16mm
- **Rotor Diameter:** 27.5mm
- **Weight:** 72g
- **Stator Slots:** 12
- **Rotor Poles:** 14

### Thông số cánh quạt khuyến nghị:
- **Recommended Props:** 10x4.7, 10x7, 11x4.7, 11x5.5 (inch)
- **Max Lipo:** 2-4S (7.4V - 14.8V)
- **ESC:** 30A

---

## Các thông số mô phỏng Gazebo

### 1. **maxRotVelocity** - Vận tốc quay tối đa

**Công thức:**
```
Max RPM = KV × Voltage
Max ω (rad/s) = Max_RPM × 2π / 60
```

**Tính toán với 4S LiPo (14.8V):**
```
Max RPM = 880 × 14.8 = 13,024 RPM
Max ω = 13,024 × 2π / 60 = 1,363.87 rad/s
```

**Trong SDF:**
```xml
<maxRotVelocity>1363.9</maxRotVelocity>
```

**Giải thích:**
- KV rating cho biết động cơ quay bao nhiêu vòng/phút trên mỗi volt
- 880 KV nghĩa là: ở 1V, động cơ không tải quay 880 RPM
- Với pin 4S (14.8V), tốc độ tối đa là 880 × 14.8 = 13,024 RPM
- Chuyển sang rad/s để phù hợp với đơn vị Gazebo

**Lưu ý:** Giá trị 1000 rad/s trong file x500 hiện tại là quá thấp!

---

### 2. **motorConstant** - Hằng số lực đẩy (Thrust Constant)

**Công thức mô phỏng:**
```
Thrust (N) = motorConstant × ω²
```

**Phương pháp tính:**

#### Phương pháp 1: Từ yêu cầu hover
```
Giả sử:
- Tổng trọng lượng drone: 2.0 kg
- Hover ở 50% throttle
- Cần 4 động cơ

Hover RPM = Max_RPM × 0.5 = 6,512 RPM = 681.94 rad/s
Thrust per motor at hover = (2.0 kg × 9.81) / 4 = 4.91 N

motorConstant = Thrust / ω²
              = 4.91 / (681.94)²
              = 1.054758e-05 N⋅s²
```

#### Phương pháp 2: Từ KV rating (lý thuyết)
```
Kt (Torque constant) = 60 / (2π × KV)
                      = 60 / (2π × 880)
                      = 0.010851 Nm/A
```

Sau đó cần dữ liệu thực nghiệm về lực đẩy để chuyển từ torque constant sang thrust constant.

**Trong SDF:**
```xml
<motorConstant>1.05475840e-05</motorConstant>
```

**Giải thích:**
- Là hệ số quan hệ giữa vận tốc góc và lực đẩy
- Phụ thuộc vào: động cơ, cánh quạt, mật độ không khí
- Quan trọng nhất để điều chỉnh khả năng bay của drone
- Nếu quá nhỏ: drone không đủ lực cất cánh
- Nếu quá lớn: drone nhạy quá, khó điều khiển

---

### 3. **momentConstant** - Hằng số moment xoắn

**Công thức:**
```
Torque (Nm) = momentConstant × Thrust (N)
```

**Tính toán:**
```
Typical Cq/Ct ratio ≈ 0.01 (cho cánh quạt hiệu suất cao)
momentConstant = (Cq/Ct) × Propeller_Diameter
              = 0.01 × 0.254m
              = 0.00254 m
```

**Trong SDF:**
```xml
<momentConstant>0.00254</momentConstant>
```

**Giải thích:**
- Tỷ lệ giữa moment xoắn và lực đẩy
- Moment xoắn gây ra yaw (xoay quanh trục Z)
- Cánh quạt càng lớn, moment càng cao
- X500 hiện tại dùng 0.016 - hơi cao nhưng chấp nhận được

---

### 4. **rotorDragCoefficient** - Hệ số cản rotor

**Công thức:**
```
Drag_Torque (Nm) = rotorDragCoefficient × ω²
```

**Tính toán:**
```
Mechanical Power = Max_Power - I²R losses
                 = 320W - (20² × 0.117)
                 = 273.2W

Estimated drag torque (10% of power at max speed):
Drag_Torque = (0.1 × Mechanical_Power) / Max_ω
            = (0.1 × 273.2) / 1363.87
            = 0.02003 Nm

rotorDragCoefficient = Drag_Torque / ω²
                     = 0.02003 / (1363.87)²
                     = 1.077e-08
```

**Trong SDF:**
```xml
<rotorDragCoefficient>1.07686603e-08</rotorDragCoefficient>
```

**Giải thích:**
- Mô phỏng lực cản khí động học khi rotor quay
- Gây ra moment ngược chiều quay
- Ảnh hưởng đến hiệu suất và nhiệt độ động cơ
- Giá trị nhỏ vì cánh quạt được thiết kế để giảm cản

---

### 5. **timeConstantUp / timeConstantDown** - Hằng số thời gian

**Ý nghĩa:**
- **timeConstantUp:** Thời gian để động cơ tăng tốc từ 0% → 63% tốc độ mục tiêu
- **timeConstantDown:** Thời gian để động cơ giảm tốc từ 100% → 37% tốc độ mục tiêu

**Tính toán:**

#### Electrical time constant:
```
τe = L / R
   = 80μH / 117mΩ  (typical inductance for brushless motor)
   = 0.684 ms
```

#### Mechanical time constant:
```
Phụ thuộc vào quán tính rotor (motor + propeller)
Thực tế đo được: 10-15ms (spin-up), 20-30ms (spin-down)
```

**Trong SDF:**
```xml
<timeConstantUp>0.0125</timeConstantUp>    <!-- 12.5ms -->
<timeConstantDown>0.025</timeConstantDown>  <!-- 25ms -->
```

**Giải thích:**
- **Up < Down:** Tăng tốc nhanh hơn giảm tốc do quán tính khí động học
- Khi động cơ giảm, cánh quạt vẫn quay do không khí đẩy
- Giá trị nhỏ hơn → phản hồi nhanh hơn (nhưng kém thực tế)
- Giá trị lớn hơn → mô phỏng chính xác hơn (nhưng chậm phản hồi)

---

### 6. **rollingMomentCoefficient** - Hệ số moment lăn

**Trong SDF:**
```xml
<rollingMomentCoefficient>1e-06</rollingMomentCoefficient>
```

**Giải thích:**
- Mô phỏng ma sát ổ trục động cơ
- Giá trị rất nhỏ, ít ảnh hưởng trong thực tế
- Thường giữ nguyên giá trị mặc định

---

## Quy trình chuyển đổi từ Datasheet

### Bước 1: Thu thập thông số từ datasheet
- [ ] KV rating
- [ ] Max voltage (số cell pin)
- [ ] Motor resistance
- [ ] Max current
- [ ] Max power
- [ ] Weight
- [ ] Recommended propeller size

### Bước 2: Tính maxRotVelocity
```python
max_rpm = KV × max_voltage
max_rad_s = max_rpm × 2π / 60
```

### Bước 3: Tính motorConstant
```python
# Ước lượng từ yêu cầu hover
hover_rpm = max_rpm × 0.5
hover_rad_s = hover_rpm × 2π / 60
hover_thrust = (total_weight × 9.81) / num_motors

motor_constant = hover_thrust / (hover_rad_s ** 2)
```

### Bước 4: Tính momentConstant
```python
prop_diameter_m = prop_diameter_inch × 0.0254
moment_constant = 0.01 × prop_diameter_m  # Cq/Ct ≈ 0.01
```

### Bước 5: Ước lượng rotorDragCoefficient
```python
mechanical_power = max_power - (max_current**2 × resistance)
drag_torque = (0.1 × mechanical_power) / max_rad_s
rotor_drag_coeff = drag_torque / (max_rad_s ** 2)
```

### Bước 6: Giữ nguyên time constants
```
timeConstantUp = 0.0125s
timeConstantDown = 0.025s
```
(Trừ khi có dữ liệu đo đạc cụ thể từ motor test bench)

---

## Kiểm chứng (Validation)

### Test 1: Thrust-to-Weight Ratio
```python
max_thrust_per_motor = motor_constant × (max_rad_s ** 2)
total_thrust = max_thrust_per_motor × num_motors
twr = total_thrust / (total_weight × 9.81)

# Yêu cầu:
# TWR > 2.0: Excellent - có thể bay aerobatic
# TWR > 1.5: Good - bay ổn định
# TWR < 1.5: Poor - có thể không cất cánh
```

### Test 2: Hover Throttle
```python
# Drone nên hover ở 40-60% throttle
hover_thrust = total_weight × 9.81 / num_motors
hover_omega = sqrt(hover_thrust / motor_constant)
hover_throttle = hover_omega / max_rad_s

# Yêu cầu: 0.4 < hover_throttle < 0.6
```

### Test 3: Mô phỏng thực tế
- Khởi động Gazebo
- Arm motors ở 50% throttle
- Quan sát:
  - Drone nên nâng lên từ từ (hover)
  - Không rung lắc quá mức
  - Phản hồi điều khiển mượt mà

---

## So sánh: Thông số hiện tại vs Khuyến nghị

| Parameter | Current X500 | Calculated | Status |
|-----------|-------------|------------|--------|
| maxRotVelocity | 1000.0 | 1363.9 | ❌ Cần update |
| motorConstant | 8.54858e-06 | 1.05476e-05 | ⚠️ Cần điều chỉnh |
| momentConstant | 0.016 | 0.00254 | ⚠️ Hơi cao |
| rotorDragCoeff | 8.06428e-05 | 1.07687e-08 | ⚠️ Rất cao |
| timeConstantUp | 0.0125 | 0.0125 | ✅ OK |
| timeConstantDown | 0.025 | 0.025 | ✅ OK |

---

## Lưu ý quan trọng

### 1. Giá trị tính toán chỉ là ước lượng
- Cần fine-tuning trong mô phỏng thực tế
- Thử nghiệm nhiều lần để tìm giá trị tối ưu
- So sánh với drone thực nếu có

### 2. Các yếu tố ảnh hưởng
- Kiểu cánh quạt (pitch, số lượng cánh)
- Mật độ không khí (nhiệt độ, độ cao)
- Hiệu suất ESC
- Trọng lượng tổng thể drone

### 3. Quy trình điều chỉnh
1. Bắt đầu với giá trị tính toán
2. Test trong Gazebo
3. Điều chỉnh motorConstant để drone hover đúng
4. Điều chỉnh momentConstant nếu yaw không đúng
5. Điều chỉnh time constants nếu phản hồi không mượt

---

## Tools hỗ trợ

### Script tính toán tự động:
```bash
cd /path/to/Tarot650_base
python3 motor_parameter_calculation.py
```

### Benchmark test trong Gazebo:
```bash
# TODO: Tạo script test tự động
# - Hover test
# - Step response test
# - Yaw response test
```

---

## Tài liệu tham khảo

1. **Gazebo Multicopter Motor Model:**
   - https://github.com/gazebosim/gz-sim/tree/main/src/systems/multicopter_motor_model

2. **Brushless Motor Theory:**
   - KV to Kt conversion
   - Propeller thrust equations
   - Motor dynamics

3. **PX4 SITL Configuration:**
   - Motor mixing
   - Actuator outputs
   - PWM to thrust mapping

4. **T-Motor Documentation:**
   - Motor datasheets
   - Propeller matching guide
   - Performance charts

---

## Tóm tắt

Để chuyển đổi chính xác từ datasheet sang simulation:

1. **maxRotVelocity:** Tính từ KV × Voltage
2. **motorConstant:** Ước lượng từ yêu cầu hover, sau đó fine-tune
3. **momentConstant:** 0.01 × propeller diameter
4. **rotorDragCoeff:** Ước lượng từ motor power loss
5. **timeConstants:** Dùng giá trị điển hình 12.5ms / 25ms
6. **rollingMoment:** Giữ nguyên 1e-06

**Quan trọng nhất:** Luôn kiểm chứng bằng mô phỏng và so sánh với drone thực!
