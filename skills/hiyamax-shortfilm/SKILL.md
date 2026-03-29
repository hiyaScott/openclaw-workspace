# hiyamax AI短片制作技能

> AI短片的完整制作流程与最佳实践

---

## 概述

本技能涵盖从剧本到发布的完整AI短片制作流程，包括：
- 视频生成平台（可灵/海螺）能力对比
- 标准化制作流程
- 角色一致性解决方案

---

## 能力清单

| 能力 | 说明 | 工具 |
|------|------|------|
| 视频平台对比 | 可灵 vs 海螺能力分析 | 文档 |
| 制作流程指导 | 5阶段标准化流程 | 文档+脚本 |
| 角色一致性 | 多种技术方案对比 | API参数 |
| 批量生成脚本 | Python自动化脚本 | tools/ |

---

## 快速开始

### 查看平台对比
```bash
cat docs/ai-video-platform-comparison.md
```

### 查看制作流程
```bash
cat docs/hiyamax-shortfilm-workflow.md
```

### 查看角色一致性方案
```bash
cat docs/character-consistency-solutions.md
```

---

## 标准化流程

```
剧本(飞书) → 角色(即梦) → 视频(海螺API) → 剪辑(FFmpeg) → 发布(GitHub Pages)
```

详细流程见: `docs/hiyamax-shortfilm-workflow.md`

---

## 关键参数速查

### 海螺API - 首尾帧模式
```python
{
    "model": "MiniMax-Hailuo-2.3",
    "first_frame_image": "首帧URL",
    "last_frame_image": "尾帧URL",  # 可选
    "prompt": "场景描述 [运镜]",
    "duration": 10,
    "resolution": "768P"
}
```

### 可灵API - 图生视频
```python
{
    "model": "kling-v2-6-image2video",
    "input": "提示词",
    "image": "图片URL",
    "mode": "pro",
    "duration": 5
}
```

---

## 最佳实践

### 1. 角色一致性 - 三视图方案（重要！）

**问题**: 单张参考图不足以保持AI生成角色的外观一致性

**解决方案**: 基于一个概念设计生成标准三视图，作为所有分镜的统一参考

```
角色设计流程:
1. 确定基础角色概念设计（如V4版本）
2. 使用即梦AI生成三视图:
   - 正视图 (Front View) - 正面T-pose
   - 侧视图 (Side View) - 左侧面
   - 后视图 (Back View) - 背面
3. 后续所有分镜首帧生成时，同时参考三视图
```

**三视图生成Prompt模板**:
```
A vintage robot character design, [front/side/back] view, 
orthographic projection, full body. Round dome head with small antenna, 
weathered teal-gray and golden rusted metal body, orange glowing grid eyes, 
mechanical joints. Clean white background, technical character sheet style, 
3D render, highly detailed
```

**关键要点**:
- 正交投影 (orthographic projection) 确保比例一致
- 统一背景 (clean white background) 避免干扰
- 技术角色表风格 (technical character sheet style)
- 同时上传三视图作为参考比单张图效果更好

### 2. 其他最佳实践
1. **首尾帧模式**: 确保视频首帧角色一致
2. **分辨率**: 768P（10秒）或 1080P（6秒）
3. **运镜**: 使用标准指令如 `[推进]` `[拉远]`
4. **字幕**: 使用Noto Serif CJK字体
5. **发布**: 更新pipeline数据后Git提交

---

## 相关文档

| 文档 | 路径 |
|------|------|
| 平台对比 | `docs/ai-video-platform-comparison.md` |
| 制作流程 | `docs/hiyamax-shortfilm-workflow.md` |
| 角色一致性 | `docs/character-consistency-solutions.md` |

---

## 更新记录

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-03-30 | v1.1 | **重要更新**: 添加角色三视图方案，解决单张参考图一致性不足的问题 |
| 2026-03-29 | v1.0 | 初始版本，包含三篇核心文档 |

---

*技能路径: /root/.openclaw/workspace/skills/hiyamax-shortfilm*
