# 妈妈计数器 - 完整设计方案交付 (2026-03-21)

## 完成情况

已为Scott完成妈妈计数器的完整设计方案，基于 **ESP32-Display (1.28寸圆形LCD)**。

---

## 交付物清单

### 1. Web模拟器 ✅
- **链接**: https://hiyascott.github.io/scott-portfolio/research/lab/mama-counter/web-simulator/
- **功能**: 
  - 1.28寸圆形LCD仿真显示
  - 模拟"妈妈"声音触发
  - 实时计数、波形可视化
  - 电池状态、运行时间显示

### 2. 完整设计方案 ✅
- **链接**: https://hiyascott.github.io/scott-portfolio/research/lab/mama-counter/DESIGN.md
- **内容**:
  - 硬件选型 (ESP32-C3-Display + MAX9814)
  - 引脚分配和电路连接图
  - 软件架构和核心算法
  - UI设计和交互逻辑
  - 功耗优化策略
  - 物料清单 (BOM)
  - 开发流程和测试方案

### 3. Arduino源代码 ✅
- **文件**: MamaCounter.ino
- **特性**:
  - 基于 TFT_eSPI 库
  - 圆形屏幕UI适配
  - 声音检测算法
  - 按键交互 (短按/长按)
  - 低功耗模式支持

### 4. 项目主页更新 ✅
- **链接**: https://hiyascott.github.io/scott-portfolio/research/lab/mama-counter/
- **添加**: 快速入口、文件下载、下一步计划

---

## 硬件选型

| 组件 | 型号 | 价格 |
|------|------|------|
| 开发板 | ESP32-C3-Display (1.28寸圆屏) | ~￥55 |
| 麦克风 | MAX9814 | ~￥8 |
| 电池 | 3.7V 500mAh锂电 | ~￥15 |
| 其他 | 按键、线材 | ~￥2 |
| **合计** | | **~￥80** |

### 屏幕规格
- 尺寸: 1.28寸圆形
- 分辨率: 240×240
- 驱动: GC9A01 (SPI)
- 颜色: 65K彩色

---

## 关键技术点

### 1. 声音检测
```cpp
// 峰峰值检测算法
int readMicrophone() {
    int maxVal = 0, minVal = 4095;
    for (int i = 0; i < SAMPLE_SIZE; i++) {
        int val = analogRead(MIC_PIN);
        maxVal = max(maxVal, val);
        minVal = min(minVal, val);
    }
    return maxVal - minVal;
}
```

### 2. 圆形UI绘制
```cpp
// 使用 TFT_eSPI 绘制圆形屏幕UI
tft.setTextDatum(MC_DATUM);  // 中中对齐
tft.drawString(String(count), 120, 120);
tft.drawCircle(120, 120, 110, COLOR_GREEN);
```

### 3. 低功耗策略
- 正常监听: ~50mA
- Deep Sleep: ~50μA
- 目标续航: 24小时+

---

## Git提交

```
ac1cc6b feat: 妈妈计数器完整设计方案 + Web模拟器
```

---

## 后续建议

1. **硬件采购** - 推荐先从淘宝购买ESP32-C3-Display开发板
2. **原型验证** - 在面包板上先测试声音检测阈值
3. **外壳设计** -  Fusion 360设计3D打印外壳，考虑儿童佩戴
4. **实机测试** - 小朋友实际佩戴，优化误触发问题

---

*记录者: Jetton*
*日期: 2026-03-21 19:20*
