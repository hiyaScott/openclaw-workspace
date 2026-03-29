# API控制视频AI角色一致性解决方案

> 针对hiyamax AI短片项目的角色一致性技术方案

---

## 问题定义

**核心问题**: 通过API调用视频生成AI时，如何保持角色在不同镜头中的一致性？

**当前限制**:
- 海螺AI网页端有【主体参考】功能，但API不支持
- 可灵API支持首尾帧，但不确定是否有纯参考图模式
- 机器人角色（Robo No.5）不是人类面部，部分方案不适用

---

## 方案对比

### 方案1: 首尾帧模式

#### 原理
使用同一张角色图作为多个视频的首帧，强制AI以该角色开始生成。

#### 实现（海螺API）
```python
{
    "model": "MiniMax-Hailuo-2.3",
    "first_frame_image": "https://.../robo_no5_character.jpg",
    "prompt": "场景描述...",
    "duration": 10
}
```

#### 优点
- ✅ API直接支持
- ✅ 实现简单
- ✅ 首帧角色100%一致

#### 缺点
- ❌ 只有首帧固定，后续画面AI自由发挥
- ❌ 角色可能在视频中变形
- ❌ 不同视频间角色仍可能有差异

#### 效果评分: ⭐⭐⭐⭐

---

### 方案2: 首尾帧控制模式

#### 原理
同时使用首帧和尾帧，精确控制视频的起止状态。

#### 实现（海螺API）
```python
{
    "model": "MiniMax-Hailuo-2.3",
    "first_frame_image": "https://.../robo_no5_character.jpg",
    "last_frame_image": "https://.../robo_no5_realistic_front.jpg",
    "prompt": "场景描述...",
    "duration": 10
}
```

#### 优点
- ✅ API直接支持
- ✅ 起止状态都可控
- ✅ 过渡效果自然

#### 缺点
- ❌ 需要准备尾帧图
- ❌ 中间过程仍由AI控制
- ❌ 需要更多素材准备

#### 效果评分: ⭐⭐⭐⭐⭐（最佳API方案）

---

### 方案3: 详细Prompt描述

#### 原理
在prompt中详细描述角色特征，让AI根据描述生成一致角色。

#### 实现
```python
{
    "model": "MiniMax-Hailuo-2.3",
    "prompt": """A lonely old robot named 'Robo No.5' with specific features:
    - Boxy square metal head with orange glowing grid eyes
    - Weathered teal-gray metal body with rust and scratches  
    - Hydraulic mechanical arms
    - Red warning light on head
    Scene: 暴雨中保护花朵...""",
    "duration": 10
}
```

#### 优点
- ✅ 无需参考图
- ✅ 灵活性高
- ✅ 可描述复杂特征

#### 缺点
- ❌ 一致性依赖AI理解
- ❌ 效果不稳定
- ❌ 需要反复抽卡

#### 效果评分: ⭐⭐⭐

---

### 方案4: 海螺网页端主体参考

#### 原理
使用海螺AI网页端的【主体参考】功能，上传角色图作为参考，不固定首帧。

#### 实现
1. 访问 https://hailuoai.com/video
2. 选择【主体参考】模型
3. 上传角色图
4. 输入prompt生成

#### 优点
- ✅ 最佳角色一致性
- ✅ 角色可在不同姿势/场景保持一致
- ✅ 支持面部表情控制

#### 缺点
- ❌ **API不支持**，需手动操作
- ❌ 无法自动化批量生成
- ❌ 不适合程序化工作流

#### 效果评分: ⭐⭐⭐⭐⭐（最佳整体方案，但无法API化）

---

### 方案5: LoRA微调（可灵）

#### 原理
上传多段视频训练LoRA模型，锁定角色特征。

#### 实现
1. 准备10-20段角色视频
2. 在可灵平台进行LoRA训练
3. 使用训练后的模型生成视频

#### 优点
- ✅ 专业级角色一致性
- ✅ 支持复杂场景
- ✅ 可重复使用

#### 缺点
- ❌ 需要大量训练素材
- ❌ 训练成本高
- ❌ API支持待验证

#### 效果评分: ⭐⭐⭐⭐⭐（专业方案）

---

## hiyamax推荐方案

### 短期方案（当前项目）

| 优先级 | 方案 | 适用场景 |
|--------|------|----------|
| 1 | **首尾帧模式** | API自动化，需要程序化生成 |
| 2 | **首帧固定** | 简单场景，单镜头生成 |
| 3 | **网页端主体参考** | 关键镜头，可手动操作 |

### 长期方案（未来改进）

1. **调研可灵LoRA API** - 是否支持程序化训练
2. **联系DMXAPI** - 询问主体参考参数是否可开放
3. **多平台对比** - 测试Runway/Pika等平台的角色一致性
4. **自建方案** - 考虑ComfyUI工作流自建角色控制

---

## 实施建议

### 针对Robo No.5角色

由于Robo No.5是机器人（非人类面部），需注意：

1. **特征描述要详细**
   - 方头网格眼（核心识别特征）
   - 铁锈青灰色金属身体
   - 红色警示灯

2. **使用写实风格图**
   - 手绘风格可能一致性较差
   - 建议使用即梦生成的写实风格图

3. **多角度素材**
   - 准备正面、侧面、背面图
   - 用于不同场景的镜头生成

### 最佳实践

```python
# 推荐参数组合
{
    "model": "MiniMax-Hailuo-2.3",
    "first_frame_image": "写实风格角色正面图",
    # "last_frame_image": "可选：尾帧图", 
    "prompt": """A lonely old robot 'Robo No.5' with boxy square metal head, 
                 orange glowing grid eyes, weathered teal-gray metal body.
                 [场景描述] [运镜指令]""",
    "duration": 10,
    "resolution": "768P"
}
```

---

## 待解决问题

- [ ] 验证可灵API是否支持纯参考图模式
- [ ] 测试海螺API是否有未文档化的主体参考参数
- [ ] 评估Runway Gen-4的角色一致性能力
- [ ] 调研Pika 2.0的API角色一致性方案
- [ ] 测试ComfyUI+AnimateDiff自建工作流

---

## 参考资源

- [海螺AI主体参考功能教程](https://www.ai-blog.cn/14882.html)
- [MiniMax Hailuo API文档](https://doc.dmxapi.cn/hailuo-img2video.html)
- [可灵AI角色一致性方案](https://www.klingai.com/)

---

*文档版本: v1.0*
*更新日期: 2026-03-29*
*状态: 持续更新中*
