---
name: game-design
description: 游戏设计核心方法论，涵盖核心循环构建、GDD文档编写、玩家心理分析、难度平衡与成长路径规划。强调通过快速原型验证与持续迭代发现真正乐趣。
---

# 游戏设计

## 概述

游戏设计是创造互动体验的艺术与科学，涵盖从概念构思到完整设计案的完整流程。优秀的游戏设计需要理解玩家心理、构建引人入胜的核心循环、平衡挑战与奖励。

## 核心能力

### 1. 核心循环设计 (Core Loop)

**30秒测试法则**：
```
ACTION → Player does something
FEEDBACK → Game responds  
REWARD → Player feels good
REPEAT
```

**典型循环示例**：

| 类型 | 核心循环 |
|------|----------|
| Platformer | Run → Jump → Land → Collect |
| Shooter | Aim → Shoot → Kill → Loot |
| Puzzle | Observe → Think → Solve → Advance |
| RPG | Explore → Fight → Level → Gear |

### 2. 游戏设计文档 (GDD)

**必备章节**：

| 章节 | 内容 |
|------|------|
| **Pitch** | 一句话描述游戏核心概念 |
| **Core Loop** | 30秒游戏循环说明 |
| **Mechanics** | 系统如何工作 |
| **Progression** | 玩家如何进阶 |
| **Art Style** | 视觉方向 |
| **Audio** | 音频方向 |

**最佳实践**：
- 保持文档活力（定期更新）
- 可视化辅助沟通
- 从简单开始，逐步扩展

### 3. 玩家心理分析

**Bartle玩家类型**：

| 类型 | 驱动因素 |
|------|----------|
| **Achiever** | 目标、完成度 |
| **Explorer** | 探索、发现秘密 |
| **Socializer** | 社交互动、社区 |
| **Killer** | 竞争、支配 |

**奖励机制设计**：

| 机制 | 效果 | 使用场景 |
|------|------|----------|
| **Fixed** | 可预测 | 里程碑奖励 |
| **Variable** | 上瘾性 | 战利品掉落 |
| **Ratio** | 基于努力 | 刷怪游戏 |

### 4. 难度平衡

**心流状态 (Flow State)**：
```
Too Hard → Frustration → Quit
Too Easy → Boredom → Quit
Just Right → Flow → Engagement
```

**平衡策略**：
- **Dynamic** - 根据玩家技能动态调整
- **Selection** - 让玩家选择难度
- **Accessibility** - 为所有玩家提供选项

### 5. 成长系统设计

**进阶类型**：

| 类型 | 示例 |
|------|------|
| **Skill** | 玩家技术提升 |
| **Power** | 角色变强 |
| **Content** | 解锁新区域 |
| **Story** | 剧情推进 |

**节奏原则**：
- 早期胜利（快速吸引）
- 逐步增加挑战
- 强度间穿插休息
- 有意义的抉择

## 设计反模式

| ❌ 不要 | ✅ 要 |
|---------|-------|
| 孤立设计 | 持续测试 |
| 先打磨再验证 | 先原型再迭代 |
| 强迫单一玩法 | 允许玩家表达 |
| 过度惩罚 | 奖励进步 |

## 设计流程

### 阶段1：概念与原型
1. 头脑风暴核心概念
2. 制作可玩原型
3. 验证核心乐趣
4. 快速迭代调整

### 阶段2：垂直切片
1. 选择代表性关卡
2. 完整实现所有系统
3. 展示最终品质
4. 团队对齐目标

### 阶段3：全面制作
1. 扩展内容
2. 平衡与调优
3. 持续测试反馈
4.  polish与优化

## 工具推荐

- **原型**：纸笔、Figma、Balsamiq
- **关卡设计**：Tiled、Unity、Unreal
- **数值平衡**：Excel/Google Sheets
- **文档协作**：Confluence、Notion

## 参考资源

- [The Art of Game Design - Jesse Schell](https://www.schellgames.com/art-of-game-design/)
- [Rules of Play - Katie Salen & Eric Zimmerman](https://mitpress.mit.edu/9780262240451/rules-of-play/)
- [Game Design Workshop - Tracy Fullerton](https://www.amazon.com/Game-Design-Workshop-Techniques-Playcentric/dp/1138098778)
- [GDC Vault Design Talks](https://www.gdcvault.com/free/design)
