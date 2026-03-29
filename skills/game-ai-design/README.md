# Game AI Design - 游戏AI设计

游戏AI系统设计完整指南，涵盖从基础状态机到高级群体AI的完整知识体系。

## 📚 文档结构

```
game-ai-design/
├── SKILL.md                    # 主技能文档（3000+字）
├── README.md                   # 本文件
├── examples/
│   └── godot/
│       ├── npc_patrol_fsm.gd   # FSM巡逻AI示例
│       ├── behavior_tree.gd    # 行为树框架
│       ├── enemy_ai_bt.gd      # 行为树使用示例
│       ├── line_of_sight.gd    # 视线检测系统
│       ├── flock_agent.gd      # 群体AI代理
│       └── flock_manager.gd    # 群体管理器
└── references/
    └── resources.md            # 参考资料汇总
```

## 🎯 内容概览

### 1. 游戏AI概述
- 游戏AI与学术AI的区别
- 可玩性优先于真实感
- AI难度曲线设计

### 2. NPC行为系统
- **有限状态机（FSM）**：简单、高效、易于调试
- **行为树（Behavior Trees）**：模块化、层次化
- **GOAP**：目标导向的自动规划
- **Utility AI**：基于效用的模糊决策

### 3. 决策系统对比
| 系统 | 适用场景 | 复杂度 | 灵活性 |
|------|----------|--------|--------|
| FSM | 简单敌人 | 低 | 低 |
| 行为树 | 复杂Boss | 中 | 中 |
| GOAP | 策略游戏 | 高 | 高 |
| Utility AI | 模拟游戏 | 高 | 高 |

### 4. Godot实现示例
- ✅ 完整FSM巡逻AI
- ✅ 行为树框架（Sequence/Selector/Decorator）
- ✅ 视线检测与记忆系统
- ✅ 群集行为（Boids算法）

### 5. 高级话题
- 群体AI与Boids算法
- 强化学习入门
- 动态难度调整（DDA）

## 🚀 快速开始

1. **阅读SKILL.md** 获取理论知识
2. **查看examples/godot/** 获取实践代码
3. **参考references/resources.md** 深入学习

## 🔧 Godot版本

所有示例代码适用于 **Godot 4.x**

## 📖 使用建议

- 从FSM开始，适合简单AI
- 复杂角色使用行为树
- 需要自动规划时考虑GOAP
- 模拟类游戏推荐Utility AI

## 📚 核心参考资料

- 《AI Game Programming Wisdom》系列
- GDC演讲视频
- Game AI Pro（免费在线）

---

> 💡 **核心原则**：游戏AI追求的是"有趣"，而非"真实"。
