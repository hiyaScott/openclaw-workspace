# 实验室 - Arduino硬件创新项目

**创建时间**: 2026-03-21
**状态**: 规划中

---

## 实验室简介

实验室是我们在研究页面的第三个板块（前两个是SRPG五款游戏分析、乐器模拟器）。

实验室的目标：使用Arduino和ESP32等硬件平台，结合传感器与执行器，研发有趣的物联网设备和可穿戴装置。

---

## 第一个项目：妈妈计数器

### 项目背景
小朋友一天到底要喊多少次妈妈？这个问题困扰了无数家长，也激发了小朋友的好奇心。我们要做一个可穿戴设备来记录这个数据。

### 硬件选型
| 组件 | 型号 | 说明 |
|------|------|------|
| 主控 | ESP32-C3 Super Mini | RISC-V核心，超低功耗 |
| 麦克风 | MAX9814 | 自动增益控制，高灵敏度 |
| 显示 | 0.96寸 OLED | I2C接口，低功耗 |
| 电源 | 3.7V锂电池+TP4056 | USB充电，500mAh |
| 稳压 | RT9080-3.3 | 超低静态电流LDO |

### 技术挑战
1. **声音识别准确性** — 不同小朋友语音特征差异大
2. **功耗优化** — 目标续航24小时+
3. **佩戴舒适性** — 儿童安全与舒适度

### 页面链接
- 实验室主页: https://hiyascott.github.io/scott-portfolio/research/lab/
- 妈妈计数器: https://hiyascott.github.io/scott-portfolio/research/lab/mama-counter/

---

## 相关技能

已创建 Arduino 硬件开发 Skill：
- Skill路径: `/root/.openclaw/workspace/skills/arduino-hardware/SKILL.md`
- 网站页面: https://hiyascott.github.io/scott-portfolio/kimi-claw/arduino-hardware/

Skill涵盖内容：
- Arduino平台开发 (Uno/Nano/Mega)
- ESP32生态 (Wi-Fi/BLE/低功耗)
- 传感器应用 (声音、距离、温湿度等)
- 执行器控制 (舵机、电机、显示模块)
- 电源管理 (电池供电、Deep Sleep)
- 原型制作流程

---

## Git提交记录

```
c1b60d1 feat: 添加Arduino硬件Skill和实验室板块
```

---

*记录者: Jetton*
*日期: 2026-03-21*
