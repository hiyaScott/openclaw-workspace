# 文件整理方案 v1.0

## 原则
- 核心记忆文件：原地不动
- 其他文件：分类归纳，易于扩展

## 目录结构

```
workspace/
├── 核心文件（原地不动）
│   ├── SOUL.md
│   ├── MEMORY.md
│   ├── IDENTITY.md
│   ├── USER.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── BOOTSTRAP.md
│   ├── RESTORE.md
│   ├── HEARTBEAT.md
│   ├── backup.sh
│   ├── verify-backup.sh
│   └── memory/
│
├── projects/              # 游戏项目
│   ├── card-alchemist/
│   ├── aircraft-war/
│   ├── gravity-slingshot/
│   ├── ...
│   └── rhythm-commander/
│
├── exports/               # 游戏导出文件
│   ├── grid_dominion_v2_exports/
│   └── minesweeper_exports/
│
├── tools/                 # 工具和脚本
│   ├── create_ppt.py
│   ├── add_remaining_sheets.py
│   └── check_cognitive_monitor.sh
│
├── archives/              # 备份和归档
│   ├── backups/
│   └── backup-*.tar.gz
│
└── data/                  # 数据文件（已有）
    └── ...
```

## 待删除文件
- EOF (空文件)
- 损坏的子模块引用

## 执行步骤
1. 创建新目录
2. 移动游戏项目
3. 移动导出文件
4. 移动工具脚本
5. 移动备份文件
6. 清理临时文件
7. 提交 Git
