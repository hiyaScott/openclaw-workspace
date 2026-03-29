# Game AI Design - 参考资料与资源

## 📚 经典书籍

### 核心必读

| 书名 | 作者 | 说明 |
|------|------|------|
| 《AI Game Programming Wisdom 1-4》 | Steve Rabin 等 | 游戏AI编程圣经系列，涵盖从基础到高级的各种技术 |
| 《Programming Game AI by Example》 | Mat Buckland | 实用入门书，包含完整的足球AI示例 |
| 《Artificial Intelligence for Games, 2nd Ed》 | Ian Millington & John Funge | 系统性教材，适合大学课程 |
| 《Behavioral Mathematics for Game AI》 | Dave Mark | Utility AI深度讲解 |

### 进阶阅读

| 书名 | 作者 | 说明 |
|------|------|------|
| 《Game AI Pro》系列 | Steve Rabin 等 | 行业专家合著的进阶内容，有免费在线版 |
| 《Artificial Intelligence: A Modern Approach》 | Russell & Norvig | AI领域经典教材，学术性强 |
| 《Reinforcement Learning: An Introduction》 | Sutton & Barto | 强化学习权威教材 |

---

## 🎥 视频资源

### GDC演讲（Game Developers Conference）

**必看演讲：**

| 标题 | 演讲者 | 主题 |
|------|--------|------|
| "AI Summit: Architecture" 系列 | 多位 | 各种AI架构对比 |
| "The Simplest AI Trick in the Book" | Damian Isla | 简单但有效的AI技巧 |
| "AI Navigation: Past, Present, and Future" | Mikko Mononen | 导航网格技术 |
| "Building the AI for BioShock Infinite" | 2K团队 | 复杂AI系统案例 |
| "The AI of Horizon Zero Dawn" | Guerrilla Games | 开放世界AI |
| "Overwatch AI: Behind the Scenes" | Blizzard | FPS游戏AI |

**观看渠道：**
- [GDC Vault](https://gdcvault.com/) - 官方视频库（部分免费）
- [GDC YouTube频道](https://www.youtube.com/c/Gdconf) - 免费演讲

### 在线课程

| 平台 | 课程 | 说明 |
|------|------|------|
| Coursera | "Game Theory" | 博弈论基础 |
| Udemy | "Unreal Engine AI with Behavior Trees" | UE行为树实战 |
| YouTube | "AI and Games" 频道 | 游戏AI案例分析 |

---

## 🛠️ 开源项目与工具

### Godot相关

| 项目 | 链接 | 说明 |
|------|------|------|
| **LimboAI** | [GitHub](https://github.com/limbonaut/limboai) | Godot行为树与状态机插件 |
| **Godot Steering Behaviors** | GitHub搜索 | 群体行为实现 |
| **Godot GOAP** | GitHub搜索 | GOAP实现参考 |

### 通用工具

| 工具 | 用途 | 链接 |
|------|------|------|
| **Recast & Detour** | 导航网格生成与寻路 | [GitHub](https://github.com/recastnavigation/recastnavigation) |
| **A* Pathfinding Project** | Unity寻路插件 | [官网](https://arongranberg.com/astar/) |
| **Unity ML-Agents** | 强化学习工具包 | [GitHub](https://github.com/Unity-Technologies/ml-agents) |
| **OpenAI Gym** | 强化学习环境 | [GitHub](https://github.com/openai/gym) |

### 算法实现参考

| 项目 | 说明 |
|------|------|
| [Boids](https://www.red3d.com/cwr/boids/) | Craig Reynolds的原始实现 |
| [GOAP实现](https://github.com/stolk/GPGOAP) | C语言GOAP规划器 |
| [BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP) | C++行为树库 |

---

## 🌐 网站与社区

### 专业网站

| 网站 | URL | 说明 |
|------|-----|------|
| **AIGameDev.com** | aigamedev.com | 游戏AI专业社区（部分内容需会员） |
| **Game AI Pro** | gameaipro.com | 免费在线书籍和文章 |
| **Reddit r/gameai** | reddit.com/r/gameai | 社区讨论 |
| **Gamasutra/Game Developer** | gamedeveloper.com | 游戏开发文章 |

### 博客与个人网站

| 作者 | 网站 | 专长 |
|------|------|------|
| **Dave Mark** | [Intrinsic Algorithm](http://intrinsicalgorithm.com/) | Utility AI专家 |
| **Bobby Anguelov** | [blog.bobbyanguelov.com](http://blog.bobbyanguelov.com) | 游戏架构 |
| **Alex Champandard** | [AIGameDev](https://aigamedev.com) | 行业分析 |

---

## 📖 经典论文

### 群体行为

- **Reynolds, C.W. (1987)** - "Flocks, Herds and Schools: A Distributed Behavioral Model" - Boids算法原始论文
- **Reynolds, C.W. (1999)** - "Steering Behaviors For Autonomous Characters" - 转向行为完整论述

### 规划算法

- **Stefik, M. (1981)** - "Planning with Constraints" - 早期规划研究
- **Nau, D. et al. (2003)** - "SHOP2: An HTN Planning System" - 分层任务网络

### 游戏AI架构

- **Isla, D. (2005)** - "Handling Complexity in the Halo 2 AI" - 分层FSM案例
- **Orkin, J. (2006)** - "Three States and a Plan: The A.I. of F.E.A.R." - GOAP经典案例

---

## 🎮 案例分析

### 优秀AI设计案例

| 游戏 | AI特点 | 技术亮点 |
|------|--------|----------|
| **F.E.A.R.** | 战术AI | GOAP实现，复杂对话系统 |
| **The Last of Us** | 同伴AI | 隐形引导，上下文对话 |
| **Alien: Isolation** | 动态威胁 | 导演系统+多层级AI |
| **Horizon Zero Dawn** | 生态系统 | 机器群落模拟 |
| **Left 4 Dead** | 导演系统 | 动态难度调整 |
| **Dota 2 OpenAI Five** | 强化学习 | 大规模多智能体训练 |

---

## 🔧 调试与开发工具

### Godot调试技巧

```gdscript
# 1. 使用debug_draw插件绘制AI信息
# 2. 开启Visible Collision Shapes查看视野
# 3. 使用Remote场景树实时监控

# 运行时调试绘制示例
func _draw():
    # 绘制视野范围
    draw_arc(Vector2.ZERO, view_distance, -view_angle/2, view_angle/2, 32, Color.red)
    
    # 绘制当前状态
    if Engine.is_editor_hint() or OS.is_debug_build():
        draw_string(get_font(""), Vector2(0, -20), str(State.keys()[current_state]))
```

### 推荐Godot插件

| 插件 | 功能 | 获取方式 |
|------|------|----------|
| **Debug Draw** | 3D/2D调试绘制 | Asset Library |
| **LimboAI** | 行为树编辑器 | GitHub |
| **Visual Profiler** | 性能分析 | 内置 |

---

## 📋 检查清单

### AI设计检查清单

- [ ] 行为是否清晰可预测？
- [ ] 是否有适当的难度曲线？
- [ ] AI是否给玩家反应时间？
- [ ] 失败是否公平且可理解？
- [ ] 是否有足够的视觉/音频反馈？
- [ ] AI是否支持游戏叙事？
- [ ] 性能是否在预算内？
- [ ] 是否容易调试和修改？

---

## 🔄 持续学习建议

1. **每月阅读**：至少一篇GDC演讲或论文
2. **实践项目**：用小demo测试新算法
3. **游戏分析**：拆解喜爱游戏的AI设计
4. **社区参与**：加入Reddit r/gameai或Discord服务器
5. **工具尝试**：每季度尝试一个新工具或框架

---

> 最后更新：2026-03-26
> 
> 如需补充资源或发现链接失效，请更新此文档。
