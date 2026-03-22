# Arduino 硬件开发技能

> 嵌入式系统与物联网硬件开发专业能力。涵盖 Arduino、ESP32 平台开发，传感器与执行器应用，低功耗设计，以及可穿戴设备原型制作。

---

## 核心能力

- **Arduino 平台开发** — ATmega328P 系列单片机编程
- **ESP32 生态** — Wi-Fi/蓝牙双模芯片，低功耗物联网应用
- **传感器应用** — 声音、温度、加速度、距离等各类传感器
- **执行器控制** — 舵机、电机、继电器、显示模块
- **电源管理** — 电池供电、低功耗模式、续航优化
- **原型制作** — 从面包板到 PCB，从概念到实物

---

## 开发平台

### Arduino 系列

| 型号 | 核心 | 特点 | 适用场景 |
|------|------|------|----------|
| Arduino Uno | ATmega328P | 经典入门，文档丰富 | 学习、原型验证 |
| Arduino Nano | ATmega328P | 体积小巧，引脚全 | 可穿戴、嵌入式 |
| Arduino Mega | ATmega2560 | 54个I/O口 | 复杂项目、多传感器 |

### ESP32 系列

| 型号 | 主频 | 内存 | 无线 | 特点 |
|------|------|------|------|------|
| ESP32-WROOM | 240MHz | 520KB SRAM | Wi-Fi + BLE | 经典款，生态成熟 |
| ESP32-S3 | 240MHz | 512KB SRAM | Wi-Fi + BLE 5 | AI加速，USB原生 |
| ESP32-C3 | 160MHz | 400KB SRAM | Wi-Fi + BLE 5 | RISC-V核心，低成本 |

**选型建议**：
- 需要 Wi-Fi/蓝牙 → 选 ESP32
- 纯本地控制、超低功耗 → 选 Arduino Nano + 外围模块
- 可穿戴/电池供电 → ESP32 Deep Sleep 模式

---

## 传感器应用

### 声音检测

**KY-037 高感度麦克风模块**
- 工作电压：3.3V - 5V
- 输出：模拟量 (AO) + 数字量 (DO)
- 灵敏度可调（板载电位器）
- 应用：声音触发、噪音监测、语音唤醒

```cpp
const int micPin = A0;    // 模拟输出接A0
const int ledPin = 13;    // LED指示

void setup() {
    pinMode(ledPin, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int soundLevel = analogRead(micPin);
    Serial.println(soundLevel);
    
    if (soundLevel > 500) {  // 阈值可调整
        digitalWrite(ledPin, HIGH);
        delay(100);
        digitalWrite(ledPin, LOW);
    }
    delay(10);
}
```

**MAX9814 麦克风模块（带AGC）**
- 自动增益控制，适应不同音量环境
- 增益可调：40dB / 50dB / 60dB
- 适合：语音识别、音频录制

### 距离检测

**HC-SR04 超声波传感器**
```cpp
const int trigPin = 9;
const int echoPin = 10;

float getDistance() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    float duration = pulseIn(echoPin, HIGH);
    return duration * 0.034 / 2;  // cm
}
```

### 其他常用传感器

| 传感器 | 功能 | 接口 | 应用 |
|--------|------|------|------|
| DHT11/22 | 温湿度 | 单总线 | 环境监测 |
| MPU6050 | 加速度+陀螺仪 | I2C | 姿态检测 |
| BH1750 | 光照强度 | I2C | 自动亮度 |
| MQ-135 | 空气质量 | 模拟 | 气体检测 |

---

## 执行器控制

### 舵机 (Servo)

**SG90 微型舵机**
- 工作电压：4.8V - 6V
- 控制信号：PWM，50Hz，0.5ms-2.5ms脉宽
- 角度范围：0° - 180°
- 扭矩：1.8kg/cm

**ESP32Servo 库使用**
```cpp
#include <ESP32Servo.h>

Servo myServo;
const int servoPin = 13;

void setup() {
    myServo.setPeriodHertz(50);           // 50Hz标准舵机频率
    myServo.attach(servoPin, 500, 2500);  // 500-2500μs脉宽范围
    myServo.write(90);                     // 初始位置中间
}

void loop() {
    myServo.write(0);    delay(1000);
    myServo.write(90);   delay(1000);
    myServo.write(180);  delay(1000);
}
```

**多舵机控制注意**：
- ESP32 有 16 个 PWM 通道，可同时控制多路舵机
- 大扭矩舵机需外接电源，不可直接使用开发板供电
- 舵机启动电流大，多个同时转动可能造成电压跌落

### 直流电机

**L298N 电机驱动板**
- 双H桥，可同时驱动2个直流电机
- 输入电压：5V - 35V
- 输出电流：2A（峰值3A）

### 显示模块

| 模块 | 分辨率 | 接口 | 特点 |
|------|--------|------|------|
| SSD1306 OLED | 128×64 | I2C/SPI | 小巧、低功耗 |
| ST7735 TFT | 160×128 | SPI | 彩色、性价比高 |
| LCD1602 | 16×2字符 | I2C/并行 | 经典、易用 |

---

## 低功耗设计

### ESP32 睡眠模式

| 模式 | 电流消耗 | 唤醒源 | 特点 |
|------|----------|--------|------|
| Active | 80-240mA | - | 全速运行 |
| Modem-Sleep | 20-30mA | 定时器/中断 | CPU运行，射频关闭 |
| Light-Sleep | 0.8-1.2mA | 多种 | RAM保持，快速唤醒 |
| Deep-Sleep | 10-150μA | GPIO/定时器/触摸 | 仅RTC运行 |
| Hibernation | 5μA | GPIO/定时器 | 最低功耗 |

**Deep Sleep 示例**
```cpp
#include <esp_sleep.h>

void setup() {
    Serial.begin(115200);
    
    // 配置定时唤醒（每10秒）
    esp_sleep_enable_timer_wakeup(10 * 1000000);
    
    // 配置GPIO唤醒（GPIO33上升沿）
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_33, 1);
    
    Serial.println("进入Deep Sleep...");
    esp_deep_sleep_start();
}

void loop() {
    // Deep Sleep模式下不会执行到这里
}
```

**低功耗设计要点**：
1. **关闭不需要的外设** — Wi-Fi、蓝牙、ADC等
2. **降低CPU频率** — `setCpuFrequencyMhz(80)`
3. **使用外部中断** — 代替轮询检测
4. **优化传感器供电** — 用MOSFET控制传感器电源
5. **选择低静态电流LDO** — 如 TPS7A05 (250nA IQ)

### 电池供电估算

**续航时间 = 电池容量(mAh) / 平均电流(mA)**

| 场景 | 平均电流 | 1000mAh电池续航 |
|------|----------|-----------------|
| 持续运行 | 100mA | 10小时 |
| 间歇唤醒(1分钟) | 5mA | 8天 |
| Deep Sleep | 50μA | 2年 |

---

## 典型项目架构

### 可穿戴设备（如妈妈计数器）

```
硬件架构：
┌─────────────────────────────────────┐
│  ESP32-C3 主控                      │
│  - 低功耗模式管理                    │
│  - 音频信号处理                      │
│  - 数据存储与上传                    │
└─────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    ↓                   ↓
┌──────────┐     ┌──────────┐
│ MAX9814  │     │  OLED    │
│ 麦克风   │     │  显示屏  │
│ 检测"妈妈"│     │ 显示计数  │
└──────────┘     └──────────┘
    │
    ↓
┌──────────┐
│  按键    │
│ 手动触发 │
└──────────┘
```

**电源方案**：
- 3.7V锂电池 + TP4056充电模块
- 或者 2×AA电池 + 升压模块

---

## 开发工具链

### Arduino IDE
1. 安装 ESP32 开发板支持：
   - 文件 → 首选项 → 附加开发板管理器网址
   - 添加：`https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
2. 工具 → 开发板 → 开发板管理器 → 搜索"ESP32" → 安装

### PlatformIO（推荐）
- VSCode 插件
- 更好的库管理、智能提示、调试支持

### 常用库

| 库名 | 功能 | 安装 |
|------|------|------|
| ESP32Servo | 舵机控制 | 库管理器搜索 |
| Adafruit SSD1306 | OLED驱动 | 库管理器搜索 |
| DHT sensor library | 温湿度 | 库管理器搜索 |
| ArduinoJson | JSON解析 | 库管理器搜索 |

---

## 调试技巧

### 串口监视器
- 波特率要与代码中 `Serial.begin()` 一致
- ESP32 通常用 115200

### 常见问题

| 问题 | 可能原因 | 解决 |
|------|----------|------|
| 舵机抖动 | 电源不足 | 外接5V电源 |
| 传感器读数异常 | 接地不稳 | 检查GND连接 |
| 无法上传程序 | 串口被占用 | 关闭串口监视器 |
| Deep Sleep无法唤醒 | 唤醒源未配置 | 检查唤醒配置 |

---

## 扩展阅读

- [ESP32 Arduino 核心文档](https://docs.espressif.com/projects/arduino-esp32/)
- [Arduino 官方文档](https://www.arduino.cc/reference/en/)
- [TinyML 入门](https://www.tinyml.org/) — 在微控制器上运行机器学习

---

*技能版本: v1.0*
*更新日期: 2026-03-21*
