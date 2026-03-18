# Minesweeper - 扫雷游戏

## 项目信息
- **引擎**: Godot 4.6.1
- **类型**: 经典扫雷游戏

## 游戏规则
1. 左键点击揭开格子
2. 右键点击标记地雷（插旗）
3. 数字表示周围8格中的地雷数量
4. 揭开所有非地雷格子即可获胜
5. 踩到地雷游戏结束

## 操作说明
- **左键**: 揭开格子
- **右键**: 标记/取消标记地雷
- **R键/重新开始按钮**: 重新开始游戏

## 文件结构
```
minesweeper/
├── project.godot      # 项目配置
├── README.md          # 本文件
├── scenes/
│   ├── main.tscn      # 主场景
│   └── cell.tscn      # 格子场景
└── src/
    ├── game.gd        # 游戏主逻辑
    └── cell.gd        # 格子脚本
```

## 游戏配置
- 网格大小: 10x10
- 地雷数量: 15个

## 运行项目
```bash
cd minesweeper
godot4 --editor
```

## 导出
```bash
# Web导出
godot4 --headless --export-release "Web" ./exports/web/index.html

# Windows导出
godot4 --headless --export-release "Windows Desktop" ./exports/windows/minesweeper.exe
```
