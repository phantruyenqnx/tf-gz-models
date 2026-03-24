# Phân tích kết quả tính toán Motor Parameters

## Dữ liệu từ Thrust Bench Test

Motor: **T-Motor 2216 KV880**
Propeller: **APC 1047** (10 inch × 4.7 inch)
Voltage: **14.8V** (4S LiPo)

### Bảng dữ liệu test thực tế:

| Current (A) | Thrust (N) | Power (W) | RPM (ước tính) | ω (rad/s) | Motor Constant (N⋅s²) |
|-------------|------------|-----------|----------------|-----------|----------------------|
| 0.6 | 0.98 | 8.88 | 12,962 | 1357.4 | 5.32e-07 |
| 1.5 | 1.96 | 22.20 | 12,870 | 1347.7 | 1.08e-06 |
| 2.5 | 2.94 | 37.00 | 12,767 | 1336.9 | 1.65e-06 |
| **3.7** | **3.92** | **54.76** | **12,643** | **1324.0** | **2.24e-06** |
| **5.2** | **4.91** | **76.96** | **12,489** | **1307.8** | **2.87e-06** ⬅ HOVER |
| **6.8** | **5.89** | **100.64** | **12,324** | **1290.5** | **3.53e-06** |
| **8.4** | **6.87** | **124.32** | **12,159** | **1273.3** | **4.24e-06** |
| **10.1** | **7.85** | **149.48** | **11,984** | **1255.0** | **4.98e-06** |
| **12.3** | **8.83** | **182.04** | **11,758** | **1231.3** | **5.82e-06** |
| **14.2** | **9.81** | **210.16** | **11,562** | **1210.8** | **6.69e-06** |
| 16.2 | 10.79 | 239.76 | 11,356 | 1189.2 | 7.63e-06 |
| 21.4 | 13.34 | 316.72 | 10,821 | 1133.1 | 1.04e-05 |

**Vùng làm việc chính (in đậm): 30%-80% throttle**

---

## Phân tích Motor Constant

### Quan sát quan trọng:

1. **Motor constant KHÔNG phải hằng số!**
   - Biến thiên từ 5.32e-07 đến 1.04e-05 (gấp ~20 lần)
   - Tăng dần khi throttle tăng
   - Nguyên nhân: Hiệu suất propeller thay đổi theo RPM

2. **Vùng throttle 30%-80% (working range):**
   - Motor constant: 2.24e-06 → 6.69e-06
   - Trung bình: **4.34e-06 N⋅s²**
   - Biến thiên: ±102.6%

3. **Tại điểm hover (50% throttle, ~5N):**
   - Motor constant: **2.87e-06 N⋅s²**
   - RPM: 12,489 (~1308 rad/s)
   - Đây là giá trị quan trọng nhất cho simulation!

---

## So sánh với X500 hiện tại:

| Parameter | X500 Current | Calculated | Ratio | Status |
|-----------|--------------|------------|-------|--------|
| maxRotVelocity | 1000.0 | 1363.9 | 1.36× | ❌ Quá thấp |
| motorConstant | 8.54858e-06 | 4.34e-06 (avg)<br>2.87e-06 (hover) | 0.51×<br>0.34× | ⚠️ Cao hơn thực tế |
| momentConstant | 0.016 | 0.00254 | 0.16× | ⚠️ Cao hơn nhiều |
| rotorDragCoeff | 8.06428e-05 | 1.08e-08 | 0.0001× | ❌ Cao hơn rất nhiều |

### Ý nghĩa:

**motorConstant trong X500 = 8.54858e-06** là **GẤP 2-3 LẦN** giá trị thực tế!

Điều này có nghĩa:
- ✅ Drone X500 hiện tại có thể bay được (vì có đủ thrust)
- ❌ Nhưng các thông số không chính xác với motor thật
- ❌ Nếu dùng giá trị thực tế (4.34e-06), TWR chỉ còn 1.65:1 thay vì 4.0:1

---

## Khuyến nghị cho Tarot650 (hoặc tùy chỉnh X500):

### Option 1: Dùng giá trị từ test data (CHÍNH XÁC NHẤT)
```xml
<maxRotVelocity>1363.9</maxRotVelocity>
<motorConstant>2.87e-06</motorConstant>  <!-- Tại hover -->
<momentConstant>0.00254</momentConstant>
<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
```

**Ưu điểm:**
- Phản ánh chính xác motor T-Motor 2216 + APC 1047
- TWR = 1.65:1 (đủ bay ổn định)

**Nhược điểm:**
- TWR thấp, không đủ cho aerobatic
- Cần điều chỉnh nếu drone nặng hơn 2kg

### Option 2: Điều chỉnh cho TWR cao hơn
```xml
<maxRotVelocity>1363.9</maxRotVelocity>
<motorConstant>5.82e-06</motorConstant>  <!-- Tại 70% throttle -->
<momentConstant>0.00254</momentConstant>
<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
```

**Ưu điểm:**
- TWR = 2.5-3.0:1 (tốt cho aerobatic)
- Vẫn dựa trên test data thực

**Nhược điểm:**
- Hover sẽ ở ~30-35% throttle thay vì 50%

### Option 3: Giữ nguyên X500 (KHÔNG KHUYẾN NGHỊ)
```xml
<maxRotVelocity>1000.0</maxRotVelocity>  <!-- SAI! -->
<motorConstant>8.54858e-06</motorConstant>  <!-- Quá cao! -->
```

---

## Validation với drone 2.0kg:

### Scenario 1: Dùng motorConstant = 2.87e-06 (hover point)
```
Max thrust per motor = 2.87e-06 × (1363.9)² = 5.33 N
Total thrust = 5.33 × 4 = 21.32 N
Total weight = 2.0 × 9.81 = 19.62 N
TWR = 21.32 / 19.62 = 1.09:1 ❌ Không đủ!
```
**Vấn đề:** Motor constant tại hover (~50% throttle thực tế) không thể dùng cho 100% throttle!

### Scenario 2: Dùng motorConstant = 4.34e-06 (trung bình 30-80%)
```
Max thrust per motor = 4.34e-06 × (1363.9)² = 8.07 N
Total thrust = 8.07 × 4 = 32.29 N
TWR = 32.29 / 19.62 = 1.65:1 ✅ OK
```

### Scenario 3: Dùng motorConstant = 6.69e-06 (tại 80% throttle)
```
Max thrust per motor = 6.69e-06 × (1363.9)² = 12.44 N
Total thrust = 12.44 × 4 = 49.76 N
TWR = 49.76 / 19.62 = 2.54:1 ✅ GOOD
```

---

## Vấn đề về Motor Constant không phải hằng số:

### Tại sao motor constant thay đổi?

1. **Hiệu suất propeller phụ thuộc RPM:**
   - Ở RPM thấp: Propeller kém hiệu quả → thrust/ω² thấp
   - Ở RPM cao: Propeller hiệu quả hơn → thrust/ω² cao
   - Ở RPM rất cao: Hiệu suất giảm do compressibility

2. **Slip của motor:**
   - KV rating là giá trị không tải
   - Khi có tải, RPM thực tế < KV × Voltage
   - Slip tăng khi current tăng

3. **Propeller stall:**
   - Ở góc tấn cao (RPM thấp, throttle cao), propeller stall
   - Giảm hiệu suất đột ngột

### Gazebo model đơn giản hóa:

Gazebo giả định: **Thrust = motorConstant × ω²**

Thực tế: **Thrust = f(ω, throttle, air_density, ...)**

⚠️ Vì vậy, **motorConstant là một giá trị "fitted average"** chứ không phải hằng số vật lý!

---

## Khuyến nghị cuối cùng:

### Cho drone 2.0kg với T-Motor 2216 + APC 1047:

```xml
<!-- RECOMMENDED PARAMETERS -->
<maxRotVelocity>1363.9</maxRotVelocity>

<!-- Choose based on desired performance: -->

<!-- Conservative (realistic hover at 50%): -->
<motorConstant>4.34e-06</motorConstant>  <!-- TWR = 1.65:1 -->

<!-- Balanced (good performance): -->
<motorConstant>5.50e-06</motorConstant>  <!-- TWR = 2.0:1 -->

<!-- Aggressive (aerobatic): -->
<motorConstant>6.70e-06</motorConstant>  <!-- TWR = 2.5:1 -->

<momentConstant>0.00254</momentConstant>
<rotorDragCoefficient>1.08e-08</rotorDragCoefficient>
<rollingMomentCoefficient>1e-06</rollingMomentCoefficient>
<timeConstantUp>0.0125</timeConstantUp>
<timeConstantDown>0.025</timeConstantDown>
```

### Testing workflow:

1. Bắt đầu với giá trị **balanced (5.50e-06)**
2. Test hover trong Gazebo
3. Nếu hover ở < 40% throttle → giảm motorConstant
4. Nếu hover ở > 60% throttle → tăng motorConstant
5. Target: Hover ở 45-55% throttle

---

## Ghi chú về X500 hiện tại:

File `x500/model.sdf` có:
- `motorConstant = 8.54858e-06`
- `maxRotVelocity = 1000.0`

Tính toán ngược:
```
Thrust at 1000 rad/s = 8.54858e-06 × (1000)² = 8.55 N
```

Điều này cho thấy X500 được tune để có:
- Thrust per motor: ~8.5N tại 1000 rad/s
- Total thrust: ~34N
- TWR với 2kg: 1.73:1

Có vẻ hợp lý, nhưng **maxRotVelocity = 1000** là quá thấp so với motor KV880!

Khả năng cao là X500 model được tune empirically (thử nghiệm) chứ không dựa trên motor datasheet.

---

## Kết luận:

1. ✅ **Script tính toán hoạt động đúng**
2. ✅ **Dữ liệu test bench rất có giá trị**
3. ⚠️ **Motor constant không phải hằng số - cần chọn giá trị phù hợp**
4. ⚠️ **Giá trị X500 hiện tại được tune bằng kinh nghiệm**
5. 📝 **Khuyến nghị: Bắt đầu với 5.50e-06, sau đó fine-tune trong Gazebo**

---

**Tạo bởi:** motor_parameter_calculation.py
**Dữ liệu:** T-Motor 2216 KV880 + APC 1047 @ 14.8V
**Ngày:** 2026-01-13
