# GitHub 工程环境优化方案

**制定时间**: 2026-03-18  
**目标**: 清理根目录混乱，统一项目结构  
**涉及仓库**: scott-portfolio, mama-counter, minesweeper-demo, aircraft-war, snake-game, game-design-portfolio

---

## 一、当前问题诊断

### 1.1 根目录混乱现状

```
hiyaScott/                    ← GitHub根目录
├── scott-portfolio/          ✅ 主站（已规范）
├── openclaw-workspace/       ✅ Jetton记忆备份
├── jetton-monitor/           ✅ 桌面应用（独立项目）
├── minesweeper-demo/         ❌ 应合并到games
├── mama-counter/             ❌ 应合并到games
├── aircraft-war/             ❌ 应合并到games
├── snake-game/               ❌ 应合并到games
└── game-design-portfolio/    ⚠️ 待确认
```

### 1.2 问题分析

| 问题 | 影响 |
|------|------|
| 4个Web游戏独立成仓 | 根目录臃肿，难以维护，分散流量 |
| game-design-portfolio | 疑似早期版本或独立项目，需确认 |
| 缺少统一入口 | 访客无法发现全部游戏 |

---

## 二、优化方案

### 2.1 整合策略

**4个Web游戏 → 合并到 scott-portfolio**

```
合并后结构:
scott-portfolio/
├── projects/games/           ← 原有20+游戏
│   ├── bot-coder/
│   ├── word-alchemy-2/
│   └── ...
│
└── games/                    ← 新增4个游戏
    ├── mama-counter/         ← 从独立仓库迁移
    ├── minesweeper/          ← 从minesweeper-demo迁移
    ├── aircraft-war/         ← 从独立仓库迁移
    └── snake/                ← 从snake-game迁移
```

### 2.2 详细操作步骤

#### Step 1: 本地整合4个游戏

```bash
cd /root/.openclaw/workspace/portfolio-blog/games/

# 1. 妈妈计数器
git clone --depth 1 https://github.com/hiyaScott/mama-counter.git
mv mama-counter mama-counter-app

# 2. 扫雷
git clone --depth 1 https://github.com/hiyaScott/minesweeper-demo.git
mv minesweeper-demo minesweeper

# 3. 飞机大战
git clone --depth 1 https://github.com/hiyaScott/aircraft-war.git

# 4. 贪吃蛇
git clone --depth 1 https://github.com/hiyaScott/snake-game.git
mv snake-game snake
```

#### Step 2: 更新导航和入口

修改 `portfolio-blog/games/index.html`:
- 添加4个新游戏的卡片
- 分类标签：休闲经典

修改 `portfolio-blog/index.html`:
- 首页「作品」区块添加4个新游戏入口

#### Step 3: GitHub 仓库处理

**方案A：保留并归档（推荐）**
```bash
# 为每个仓库添加说明
# 在 mama-counter/README.md 顶部添加：
"""
⚠️ 本项目已迁移至 [scott-portfolio](https://hiyascott.github.io/scott-portfolio/games/mama-counter/)

此仓库保留用于历史参考，不再维护。
"""
```

**方案B：直接删除**
```bash
# 在GitHub网页上删除仓库
# Settings → Danger Zone → Delete this repository
```

#### Step 4: 确认 game-design-portfolio

```bash
# 检查内容
git clone --depth 1 https://github.com/hiyaScott/game-design-portfolio.git
ls game-design-portfolio/

# 如果是早期版本 → 删除
# 如果是独立内容 → 保留并添加说明
```

---

## 三、整合后的完整目录结构

```
hiyaScott/                           ← GitHub根目录（清理后）
│
├── scott-portfolio/                 ✅ 主站仓库
│   ├── games/                       ← Web游戏合集
│   │   ├── mama-counter-app/        ← 妈妈计数器
│   │   ├── minesweeper/             ← 扫雷
│   │   ├── aircraft-war/            ← 飞机大战
│   │   ├── snake/                   ← 贪吃蛇
│   │   └── who-is-spy/              ← 原有游戏
│   │
│   ├── projects/games/              ← 复杂游戏项目
│   │   ├── bot-coder/
│   │   ├── rhythm-commander/
│   │   └── ... (20+个)
│   │
│   ├── research/                    ← 研究项目
│   ├── status-monitor/              ← 认知负载监控
│   └── ...
│
├── openclaw-workspace/              ✅ Jetton记忆
└── jetton-monitor/                  ✅ 桌面应用

（以下仓库将被归档或删除）
~ minesweeper-demo/                  → 合并到scott-portfolio
~ mama-counter/                      → 合并到scott-portfolio
~ aircraft-war/                      → 合并到scott-portfolio
~ snake-game/                        → 合并到scott-portfolio
~ game-design-portfolio/             → 待确认
```

---

## 四、与网页结构的对应关系

### 4.1 导航映射

| 网页位置 | 本地路径 | GitHub仓库 |
|----------|----------|------------|
| 首页「作品」卡片 | `index.html` | scott-portfolio |
| 游戏总览页 | `games/index.html` | scott-portfolio/games/ |
| 复杂游戏项目 | `projects/games/` | scott-portfolio/projects/games/ |
| 妈妈计数器 | `games/mama-counter-app/` | 从mama-counter迁移 |
| 扫雷 | `games/minesweeper/` | 从minesweeper-demo迁移 |
| 飞机大战 | `games/aircraft-war/` | 从aircraft-war迁移 |
| 贪吃蛇 | `games/snake/` | 从snake-game迁移 |

### 4.2 分类体系

```
游戏总览页 (games/index.html)
├── 🎵 音乐节奏类
│   ├── 编钟模拟器
│   ├── 节奏指挥官
│   └── 节奏跑酷
│
├── 🧩 物理解谜类
│   ├── 引力弹弓
│   └── ...
│
├── 🎮 经典休闲类          ← 新增分类
│   ├── 扫雷 (minesweeper)
│   ├── 贪吃蛇 (snake)
│   ├── 飞机大战 (aircraft-war)
│   └── 妈妈计数器 (mama-counter)
│
└── ... 其他分类
```

---

## 五、关于"忘记整合"的说明

您提到的**妈妈计数器**之前询问我记不清位置——确实如此。

**原因**:
1. 这些游戏是**独立的GitHub仓库**，不在我的本地工作区
2. 我的记忆基于 `portfolio-blog/` 目录，未包含独立仓库
3. 从未执行过将这些仓库整合到主站的流程

**解决**: 本次优化将彻底解决此问题，所有Web游戏统一归入 scott-portfolio。

---

## 六、执行检查清单

- [ ] Step 1: 克隆4个游戏到本地games目录
- [ ] Step 2: 更新 games/index.html 添加4个新游戏卡片
- [ ] Step 3: 更新首页 index.html 添加作品入口
- [ ] Step 4: 本地测试验证4个游戏正常运行
- [ ] Step 5: 推送到 scott-portfolio
- [ ] Step 6: 确认 game-design-portfolio 内容
- [ ] Step 7: 归档/删除5个独立仓库
- [ ] Step 8: 更新 MEMORY.md 记录本次重构

---

## 七、预期结果

**清理前**: 9个仓库，根目录混乱  
**清理后**: 3个核心仓库，结构清晰

```
清理后GitHub首页:
├── scott-portfolio          🌟 主要作品站
├── openclaw-workspace       🤖 Jetton记忆
└── jetton-monitor           💻 桌面应用

（其他仓库已归档或删除）
```