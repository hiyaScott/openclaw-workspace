# GitHub 目录与网页结构关联说明

**生成时间**: 2026-03-18  
**主站**: https://hiyascott.github.io/scott-portfolio/

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub 仓库结构                          │
├─────────────────────────────────────────────────────────────┤
│ hiyaScott/scott-portfolio/                                  │
│ ├── index.html                    → 网站首页                │
│ ├── games/                        → 经典游戏区              │
│ ├── projects/games/               → 完整游戏项目            │
│ ├── research/                     → 研究项目                │
│ │   ├── srpg-analysis/                                        │
│ │   ├── instrument-simulator/                                 │
│ │   └── game-design/            → 游戏设计方法论            │
│ ├── status-monitor/               → 认知负载监控            │
│ └── tools/                        → 工具箱                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     网页导航结构                            │
├─────────────────────────────────────────────────────────────┤
│ 🏠 首页 (/)                                                 │
│ ├── 🐱 Jetton 能力图谱 → /kimi-claw/                        │
│ ├── 🔬 研究项目 → /research/                                │
│ │   ├── 📊 SRPG分析 → /research/srpg-analysis/              │
│ │   ├── 🎹 乐器模拟器 → /research/instrument-simulator/     │
│ │   └── 📝 游戏设计 → /research/game-design/ (新增)         │
│ ├── 🎮 作品 → /games/                                       │
│ │   └── [更多] → /projects/games/                           │
│ └── 🛠️ 工具 → /tools/                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、详细映射表

### 2.1 首页 (index.html)

| GitHub 路径 | 网页URL | 内容 |
|-------------|---------|------|
| `index.html` | `/` | 首页，四大板块入口 |
| `kimi-claw/` | `/kimi-claw/` | Jetton 能力图谱 |

**首页四大板块**:
```
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  🐱 Jetton  │ │  🔬 研究    │ │  🎮 作品    │ │  🛠️ 工具   │
│  能力图谱   │ │  项目       │ │  游戏       │ │  箱        │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
   /kimi-claw/    /research/     /games/          /tools/
```

---

### 2.2 研究项目 (/research/)

| GitHub 路径 | 网页URL | 内容 |
|-------------|---------|------|
| `research/srpg-analysis/` | `/research/srpg-analysis/` | SRPG五款游戏分析 |
| `research/instrument-simulator/` | `/research/instrument-simulator/` | 编钟+古琴模拟器 |
| `research/game-design/` | `/research/game-design/` | **游戏设计方法论** (新增) |

**game-design 目录结构** (来自 game-design-portfolio):
```
research/game-design/
├── 10-designs.md          → 10个游戏设计案
├── scoring.md             → TOP 5评分标准
└── TODO.md                → 开发任务清单
```

---

### 2.3 游戏作品

#### 经典游戏区 (/games/)
简单、轻量的经典游戏

| GitHub 路径 | 网页URL | 来源 |
|-------------|---------|------|
| `games/mama-counter-app/` | `/games/mama-counter-app/` | mama-counter 仓库 |
| `games/minesweeper/` | `/games/minesweeper/` | minesweeper-demo 仓库 |
| `games/aircraft-war/` | `/games/aircraft-war/` | aircraft-war 仓库 |
| `games/snake/` | `/games/snake/` | snake-game 仓库 |
| `games/who-is-spy/` | `/games/who-is-spy/` | 原有 |

#### 完整游戏项目 (/projects/games/)
复杂、完整的游戏原型

| GitHub 路径 | 网页URL | 类型 | 来源 |
|-------------|---------|------|------|
| `projects/games/color-symphony/` | `/projects/games/color-symphony/` | 音乐节奏 | game-design-portfolio |
| `projects/games/time-slice/` | `/projects/games/time-slice/` | 策略动作 | game-design-portfolio |
| `projects/games/word-alchemy/` | `/projects/games/word-alchemy/` | 文字解谜 | game-design-portfolio |
| `projects/games/word-alchemy-2/` | `/projects/games/word-alchemy-2/` | 文字解谜 | 原有 |
| `projects/games/bot-coder/` | `/projects/games/bot-coder/` | 编程学习 | 原有 |
| ... (共24+个游戏) | ... | ... | 原有 |

**游戏分类体系**:
```
作品总览页 (/projects/games/index.html)
├── 🎵 音乐节奏类
│   ├── 编钟模拟器
│   ├── 节奏指挥官
│   ├── 节奏跑酷
│   └── 🌈 颜色交响曲 (新增)
│
├── ⚔️ 策略动作类 (新增分类)
│   └── ⏱️ 时间切片
│
├── 🧩 物理解谜类
├── ⚡ 反应挑战类
├── 🧠 记忆策略类
├── 🎨 创意工具类
│   ├── 像素画板
│   ├── 热力膨胀
│   ├── ...
│   ├── 🔤 词语炼金 (新增，初代)
│   └── 🔤 词语炼金 2
│
├── 🎉 多人派对类
├── 💻 编程学习类
└── ⚛️ 量子物理类
```

---

### 2.4 工具箱 (/tools/)

| GitHub 路径 | 网页URL | 内容 |
|-------------|---------|------|
| `tools/file-transfer.html` | `/tools/file-transfer.html` | 文件传输 |
| `tools/temp-pages.html` | `/tools/temp-pages.html` | 临时页面 |
| `status-monitor/` | `/status-monitor/cognitive-status.html` | 认知负载监控 |

---

## 三、整合映射

### 3.1 本次整合内容

| 原仓库 | 原URL | 整合后位置 | 新URL |
|--------|-------|-----------|-------|
| game-design-portfolio | /games/color-symphony/ | scott-portfolio/projects/games/color-symphony/ | 同上 |
| game-design-portfolio | /games/time-slice/ | scott-portfolio/projects/games/time-slice/ | 同上 |
| game-design-portfolio | /games/word-alchemy/ | scott-portfolio/projects/games/word-alchemy/ | 同上 |
| game-design-portfolio | /10-designs.md | scott-portfolio/research/game-design/10-designs.md | /research/game-design/ |
| mama-counter | / | scott-portfolio/games/mama-counter-app/ | /games/mama-counter-app/ |
| minesweeper-demo | / | scott-portfolio/games/minesweeper/ | /games/minesweeper/ |
| aircraft-war | / | scott-portfolio/games/aircraft-war/ | /games/aircraft-war/ |
| snake-game | / | scott-portfolio/games/snake/ | /games/snake/ |

---

## 四、清理后GitHub结构

### 4.1 保留的仓库 (3个)

```
hiyaScott/
├── scott-portfolio/          🌟 主站 (整合全部Web内容)
│   ├── games/                → 经典游戏
│   ├── projects/games/       → 完整游戏 (24+个)
│   ├── research/             → 研究项目
│   │   ├── srpg-analysis/
│   │   ├── instrument-simulator/
│   │   └── game-design/      → 设计方法论
│   ├── status-monitor/       → 认知负载监控
│   └── tools/                → 工具箱
│
├── openclaw-workspace/       🤖 Jetton记忆+配置备份
└── jetton-monitor/           💻 桌面应用 (独立项目)
```

### 4.2 已整合的仓库 (5个)

这些仓库建议添加归档说明后保留，或删除：

```
~ game-design-portfolio      → 内容已整合至 scott-portfolio
~ mama-counter               → 内容已整合至 scott-portfolio/games/
~ minesweeper-demo           → 内容已整合至 scott-portfolio/games/
~ aircraft-war               → 内容已整合至 scott-portfolio/games/
~ snake-game                 → 内容已整合至 scott-portfolio/games/
```

---

## 五、URL访问路径速查

### 主要入口
| 页面 | URL |
|------|-----|
| 首页 | https://hiyascott.github.io/scott-portfolio/ |
| 游戏总览 | https://hiyascott.github.io/scott-portfolio/projects/games/ |
| 研究项目 | https://hiyascott.github.io/scott-portfolio/research/ |

### 新增游戏
| 游戏 | URL |
|------|-----|
| 颜色交响曲 | https://hiyascott.github.io/scott-portfolio/projects/games/color-symphony/ |
| 时间切片 | https://hiyascott.github.io/scott-portfolio/projects/games/time-slice/ |
| 词语炼金(初代) | https://hiyascott.github.io/scott-portfolio/projects/games/word-alchemy/ |

### 新增设计文档
| 文档 | URL |
|------|-----|
| 10个设计案 | https://github.com/hiyaScott/scott-portfolio/blob/main/research/game-design/10-designs.md |
| 评分标准 | https://github.com/hiyaScott/scott-portfolio/blob/main/research/game-design/scoring.md |

---

## 六、维护建议

1. **新增游戏**: 统一放入 `projects/games/`，更新 `index.html`
2. **新增研究**: 放入 `research/`，在首页添加入口
3. **不再新建独立仓库**: 所有Web内容归入 scott-portfolio
4. **定期归档**: 每季度检查备份目录，清理过时文件