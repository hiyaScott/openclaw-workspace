# 象棋大师 (Xiangqi Master) - Godot版

中国象棋教学游戏，借鉴多邻国学习模式。

## 功能特性

### 1. 10个关卡数据
- 认识马 - 学习马走日的基本规则
- 绊马脚 - 学习绊马脚的规则
- 马走四方 - 学习马的四个方向走法
- 吃子练习 - 学习用马吃子
- 吃子进阶 - 练习吃对方的炮
- 躲避危险 - 从车威胁下逃脱
- 连续移动 - 走两步到达目标
- 连续吃子 - 两步吃掉两个子
- 移动+吃子 - 先移动再吃子
- 终极挑战 - 三步连续操作

### 2. 音效系统
使用 Godot AudioStreamPlayer 合成音效：
- 选择音效 - 短促的高音
- 移动音效 - 中等音调
- 吃子音效 - 低音，稍长
- 成功音效 - 上升音阶 C5-E5-G5-C6
- 错误音效 - 下降音调
- 点击音效 - 短促

### 3. 局结算界面
多邻国风格底部横幅：
- 绿色背景，顶部绿色边框
- 左侧显示 ✓ 图标和随机成功文本（"泰裤辣！"、"太棒了！"等）
- 右侧操作按钮（重玩、分享）
- 底部大绿色"继续"按钮，带阴影效果

### 4. 提示标记系统
- 精确提示（precise）：虚线绿色圆圈
- 模糊提示（vague）：淡黄色圆点
- 文字提示（text）：无标记
- 无提示（none）：无标记

### 5. Max形象显示
- 使用现有素材 max_character.jpg
- 左下角显示Max头像
- 对话框气泡显示提示信息

## 项目结构

```
xiangqi_master_godot/
├── assets/
│   └── max_character.jpg    # Max角色图片
├── data/levels/
│   ├── level_1.json         # 认识马
│   ├── level_2.json         # 绊马脚
│   ├── level_3.json         # 马走四方
│   ├── level_4.json         # 吃子练习
│   ├── level_5.json         # 吃子进阶
│   ├── level_6.json         # 躲避危险
│   ├── level_7.json         # 连续移动
│   ├── level_8.json         # 连续吃子
│   ├── level_9.json         # 移动+吃子
│   └── level_10.json        # 终极挑战
├── scenes/
│   ├── main.tscn            # 主场景
│   └── piece.tscn           # 棋子场景
├── src/
│   ├── board.gd             # 棋盘逻辑
│   ├── game_manager.gd      # 游戏管理器
│   ├── hint_marker.gd       # 提示标记
│   ├── ju_success_panel.gd  # 局结算界面
│   ├── main.gd              # 主脚本
│   ├── max_character.gd     # Max角色
│   ├── move_indicator.gd    # 移动指示器
│   ├── piece.gd             # 棋子脚本
│   └── sound_manager.gd     # 音效管理器
├── export_presets.cfg       # 导出配置
└── project.godot            # 项目配置
```

## 导出版本

### Windows版本
- 位置：`/root/.openclaw/workspace/xiangqi_master_godot_exports/windows/`
- 文件：
  - `xiangqi_master.exe` (约100MB)
  - `xiangqi_master.pck` (约160KB)

## 运行方式

### Windows
直接双击运行 `xiangqi_master.exe`

### 开发环境
1. 安装 Godot 4.6+
2. 打开项目文件夹
3. 运行或导出

## 操作说明

1. 点击红马选择棋子
2. 点击绿色圆点指示器移动
3. 吃掉黑方棋子
4. 完成目标位置即可过关
5. 点击"提示"按钮获取帮助
6. 点击"重置"按钮重新开始当前局

## 技术栈

- Godot Engine 4.6.1
- GDScript
- 程序化音效生成
