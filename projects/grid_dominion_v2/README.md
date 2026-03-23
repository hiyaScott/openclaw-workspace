# GRID.DOMINION v2.0

## 项目信息
- **引擎**: Godot 4.6.1
- **类型**: 区域控制Roguelike动作游戏
- **版本**: 2.0 (重新编写)

## 核心玩法
1. 使用 WASD 移动角色
2. 走过格子自动占领（变为绿色）
3. 占领80%格子即可通关
4. 空格键冲刺，冷却3秒
5. 敌人在你的领地内会持续掉血
6. 使用技能 Q/E/R 攻击/防御/加速

## 操作说明
| 按键 | 功能 |
|------|------|
| W/A/S/D | 移动 |
| 空格 | 冲刺（3秒冷却） |
| Q | 区域爆破 - 对周围敌人造成伤害（8秒冷却） |
| E | 护盾 - 5秒无敌（15秒冷却） |
| R | 加速 - 移动速度翻倍5秒（12秒冷却） |

## 文件结构
```
grid_dominion_v2/
├── project.godot          # 项目配置
├── export_presets.cfg     # 导出配置
├── README.md              # 本文件
├── scenes/
│   ├── main.tscn          # 主场景
│   └── enemy.tscn         # 敌人场景
└── src/
    ├── main.gd            # 主脚本
    ├── game_manager.gd    # 游戏管理
    ├── grid_system.gd     # 网格系统
    ├── player.gd          # 玩家控制
    ├── enemy.gd           # 敌人AI
    ├── enemy_manager.gd   # 敌人生成
    ├── skill_system.gd    # 技能系统
    ├── damage_number.gd   # 伤害数字
    ├── particle_effects.gd # 粒子特效
    └── ui.gd              # UI界面
```

## 游戏特性
- ✅ 网格占领系统
- ✅ 敌人AI（会逃离领地）
- ✅ 领地伤害机制
- ✅ 3个主动技能
- ✅ 伤害数字显示
- ✅ 粒子特效
- ✅ 游戏状态管理
- ✅ UI界面

## 导出配置
项目已配置以下导出预设：
- Web (HTML5)
- Windows Desktop

## 运行项目
```bash
cd grid_dominion_v2
godot4 --editor
```

## 版本迭代计划

### v2.0 (当前)
- [x] 基础网格系统
- [x] 玩家移动和占领
- [x] 敌人AI和领地伤害
- [x] 游戏状态管理
- [x] UI界面
- [x] 技能系统 (Q/E/R)
- [x] 伤害数字
- [x] 粒子特效

### v2.1 (计划中)
- [ ] 多种敌人类型
- [ ] 道具/升级系统
- [ ] 音效和音乐
- [ ] 领地等级系统

### v2.2 (计划中)
- [ ] 多个关卡
- [ ] Boss战
- [ ] 成就系统
- [ ] 排行榜

