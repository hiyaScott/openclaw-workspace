# GRID.DOMINION - MVP版本

区域控制Roguelike动作游戏的最小可玩版本。

## 游戏简介

在数字世界的边缘，扮演一个觉醒的程序片段（Rogue Process），通过占领网格区域来扩展自己的存在空间，同时抵御系统守护进程（SCANNER）的清除行动。

## MVP功能

✅ 12×12标准房间  
✅ 基础网格占领系统（走过即占领）  
✅ 1种敌人（SCANNER）基础AI（追击玩家）  
✅ 敌人进入领地受伤害机制  
✅ 80%占领率通关判定  
✅ 玩家生命系统（被敌人触碰扣血）  
✅ 基础UI（占领率、生命值）

## 操作说明

| 按键 | 功能 |
|------|------|
| W / ↑ | 向上移动 |
| S / ↓ | 向下移动 |
| A / ← | 向左移动 |
| D / → | 向右移动 |
| R | 重新开始（游戏结束后）|

## 游戏规则

1. **占领网格**：移动到未占领的格子上即可占领它
2. **领地伤害**：敌人进入你占领的区域会持续受到伤害
3. **通关条件**：占领率达到80%即可通关
4. **失败条件**：生命值归零则游戏结束
5. **敌人**：每10秒会生成新的SCANNER敌人，最多同时存在5个

## 技术栈

- Godot 4.x
- GDScript
- 代码图形风格（无需美术资源）

## 文件结构

```
grid_dominion_mvp/
├── project.godot          # 项目配置
├── assets/
│   └── icon.svg           # 项目图标
├── src/
│   ├── grid_system.gd     # 网格系统
│   ├── player.gd          # 玩家控制
│   ├── enemy.gd           # 敌人AI
│   ├── game_manager.gd    # 游戏管理
│   └── ui.gd              # UI控制
└── scenes/
    ├── main.tscn          # 主场景
    ├── grid_system.tscn   # 网格场景
    ├── player.tscn        # 玩家场景
    ├── enemy.tscn         # 敌人场景
    └── ui.tscn            # UI场景
```

## 如何运行

1. 安装 Godot 4.x
2. 打开项目文件夹
3. 运行 `project.godot` 或直接运行 `scenes/main.tscn`

## 后续扩展计划

- [ ] 多种房间类型（迷宫、开放大厅等）
- [ ] 多种敌人类型（PURSUER、BLOCKER等）
- [ ] 技能系统
- [ ] 道具系统
- [ ] 多房间Run结构
- [ ] Boss战
- [ ] Meta-progression（永久升级）
- [ ] 音效和音乐
- [ ] 高级视觉效果

## 开发信息

基于 GRID.DOMINION 游戏设计文档开发。
