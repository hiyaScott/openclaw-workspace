# MEMORY.md

---

## 【核心项目】SRPG 角色技能数据库分析

**项目状态**: 长期进行 | **优先级**: 最高 | **开始时间**: 2026-03-13

### 项目目标
通过穷举5款成熟SRPG产品的角色技能全量数据，为《计策设计.xlsx》提供：
1. **数据支撑** - 市面产品的技能分布、数值边界、机制覆盖率
2. **设计验证** - 快/中/慢速流派的技能配置是否合理
3. **优化建议** - 基于数据的计策系统进阶设计方案

### 核心交付物
- 5款产品角色技能数据库（穷举）
- 机制统计分析报告
- 《计策设计》优化方案

### 五款分析目标
| 序号 | 游戏名称 | 开发商 | 分析重点 | 状态 |
|------|----------|--------|----------|------|
| 1 | **天地劫：幽城再临** | 紫龙游戏 | 五内化蕴、再动机制、职业克制 | ✅ 已完成 |
| 2 | **梦幻模拟战** | 紫龙游戏 | 佣兵系统、转职树、经典关卡 | ⏳ 待分析 |
| 3 | **铃兰之剑** | 心动网络 | 像素风策略、单机+网游混合 | ⏳ 待分析 |
| 4 | **三国：望神州** | - | 三国题材适配、武将差异化 | ⏳ 待分析 |
| 5 | **三国志战棋版** | 光荣特库摩 | SLG+SRPG融合、大地图策略 | ⏳ 待分析 |

### 已完成成果
**天地劫分析报告**: https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/
- 六职业体系深度解析
- 五内化蕴系统设计拆解
- 再动/无视护卫/先攻等核心机制分析
- T0角色(冰璃、曹沁、封铃笙)设计亮点
- 对计策设计的直接启示

### 关键设计发现
| 机制 | 天地劫实现 | 计策设计启示 |
|------|-----------|--------------|
| **再动** | 冰璃、封铃笙 | 改变行动顺序的高价值机制 |
| **五内化蕴** | 分支路线选择 | 同角色多Build可能性 |
| **职业克制** | 御风-羽士25%增伤 | 明确的克制链创造博弈 |
| **无视护卫** | 御风切后排 | 穿透/破防类计策设计参考 |

### 技能设计模式模板
```
【单体输出技能】
- 倍率：1.5x - 1.8x
- CD：2-3回合
- 附加：减攻/减防/眩晕

【AOE技能】
- 倍率：0.5x - 0.7x
- 范围：十字/菱形/直线
- 附加：减速/燃烧/冰冻

【辅助技能】
- 增益：攻击+20%、移动力+1
- 持续：2-3回合
- CD：3-4回合
```

### 下一步行动
1. 开始《梦幻模拟战》数据收集与分析
2. 对比两款紫龙产品的设计演进
3. 提取可复用的SRPG设计模式

---

## GitHub 环境备份记录

**时间**: 2026-03-11
**版本**: v3.0
**操作**: 全量备份 portfolio-blog 仓库

### 版本历史
| 版本 | 时间 | Commit | 说明 |
|------|------|--------|------|
| v3.0 | 2026-03-11 | edef624 | 当前备份版本 |
| v2.0 | (历史) | 29500b7 | 上一版本 |
| v1.0 | (历史) | 6150b56 | 初始版本 |

### 备份范围
- 仓库: hiyaScott/scott-portfolio
- 标签: https://github.com/hiyaScott/scott-portfolio/releases/tag/v3.0
- 包含所有代码、资源、设计文档

---

## Git 发布工作流规范

**时间**: 2026-03-11
**问题**: Git 上传和发布流程反复出现问题，需要建立严格流程防止版本误判

### 发布流程 (必须严格执行)

```
┌─────────────────────────────────────────────────────────────────┐
│  步骤 1: 本地验证                                                  │
│  ├── 检查所有文件修改完成                                          │
│  ├── 本地测试功能正常                                              │
│  └── 确认无遗漏文件                                                │
├─────────────────────────────────────────────────────────────────┤
│  步骤 2: Git 提交                                                  │
│  ├── git add -A                                                    │
│  ├── git commit -m "描述清晰的提交信息"                             │
│  └── 确认提交成功 (无错误输出)                                      │
├─────────────────────────────────────────────────────────────────┤
│  步骤 3: Git 推送                                                  │
│  ├── git push (或 git push --set-upstream origin main)             │
│  ├── 等待推送完成                                                  │
│  └── 确认输出包含 "main -> main" 或类似成功信息                      │
├─────────────────────────────────────────────────────────────────┤
│  步骤 4: 线上验证 (关键步骤)                                        │
│  ├── 打开实际网站 URL 验证                                          │
│  ├── 硬刷新 (Ctrl+F5 / Cmd+Shift+R) 清除缓存                       │
│  ├── 确认修改内容已生效                                            │
│  └── 检查关键功能正常                                              │
├─────────────────────────────────────────────────────────────────┤
│  步骤 5: 通知确认                                                  │
│  └── 向用户明确报告: "✅ 发布成功，已同步到线上"                     │
└─────────────────────────────────────────────────────────────────┘
```

### 验证清单

每次发布必须确认：
- [x] 本地 git status 显示干净 (nothing to commit)
- [x] git push 输出成功信息
- [ ] 实际访问网站 URL 确认修改生效
- [ ] GitHub Pages 部署状态 (如适用)
- [ ] 明确通知用户发布成功

### 版本号规范

**要求**: 每次更新必须在以下位置标注版本号

| 位置 | 格式 | 示例 |
|------|------|------|
| **Git 提交信息** | `vX.Y.Z - 功能描述` | `v1.2.0 - 添加琶音器功能` |
| **HTML 文件** | `<span class="version">vX.Y.Z</span>` | `v1.2.0` |
| **设计案文档** | 版本历史表格 | `v1.2.0 \| 2026-03-11 \| 添加专业模式` |

**语义化版本规则**:
- **X (Major)**: 重大功能更新、架构重构
- **Y (Minor)**: 新增功能、组件
- **Z (Patch)**: Bug 修复、性能优化

**当前版本**: v1.3.0（添加了琶音器 + 音频预加载优化）

### 本次发布验证记录

**时间**: 2026-03-11 09:41
**提交**: 4493267 - feat(design-doc): 添加界面截图展示和详细 UI/UE 解说
**推送结果**: ✅ 成功 (`main -> main`)
**内容**: 
- 添加编钟模拟器界面截图 (ui-screenshot.png)
- 在 UI/UE 章节添加截图展示和详细布局解说
- 新增截图容器样式

### 常见错误及处理

| 错误 | 原因 | 处理 |
|------|------|------|
| `no upstream branch` | 新分支未关联远程 | 执行 `git push --set-upstream origin main` |
| `Authentication failed` | Token 失效 | 检查 git remote -v 中的 token 是否有效 |
| 页面未更新 | CDN 缓存 | 硬刷新或等待 1-2 分钟 |
| 404 错误 | 路径错误或部署失败 | 检查文件路径，确认 push 成功 |

---

## 编钟模拟器设计案

**时间**: 2026-03-11
**任务**: 为编钟模拟器编写完整的游戏设计文档 (GDD)

### 交付物

**1. 设计案文档**
- **路径**: `/portfolio-blog/research/instrument-simulator/bianzhong/design-doc.html`
- **访问地址**: https://hiyascott.github.io/scott-portfolio/research/instrument-simulator/bianzhong/design-doc.html
- **内容**: 完整的游戏设计文档，包含以下章节

### 设计案结构

1. **项目概述**
   - 核心定位：文化体验型音乐应用
   - 灵感来源：曾侯乙编钟（战国早期）
   - 设计目标：沉浸体验、一钟双音还原、创作闭环

2. **核心机制**
   - 一钟双音系统：正敲/侧敲相差大三度
   - 音区架构：上中下三层15口钟
   - 音色合成：Web Audio API 三层振荡器

3. **音频系统**
   - 完整音阶配置表（C3-A5，共30音）
   - 音频路由图
   - 频率数据

4. **UI/UE 设计**
   - 设计原则：沉浸优先、横屏体验、直观操作
   - 界面布局图
   - 色彩系统
   - 视觉反馈系统

5. **交互逻辑**
   - 敲击检测：点击位置判断正敲/侧敲
   - 手势支持
   - 屏幕方向处理（强制横屏）

6. **录制与回放系统**
   - 数据结构设计
   - 录制流程
   - 回放机制（setTimeout 精确触发）
   - 分享功能（链接/图片/JSON导出）
   - LocalStorage 持久化

7. **技术实现**
   - 技术栈：Web Audio API + localStorage + Canvas
   - 浏览器兼容性
   - 音频自动播放策略

8. **开发路线图**
   - 已实现功能清单
   - 未来扩展功能（节拍器、更多编钟、教程模式等）

### 入口链接

- 编钟模拟器界面工具栏新增「📋 设计案」按钮
- kimi-claw/game-design 页面新增项目卡片
- 设计案底部有「立即体验」按钮跳转回模拟器

---

## OpenViking 集成

**时间**: 2026-03-11
**任务**: 为编钟模拟器编写完整的游戏设计文档 (GDD)

### 交付物

**1. 设计案文档**
- **路径**: `/portfolio-blog/research/instrument-simulator/bianzhong/design-doc.html`
- **访问地址**: https://hiyascott.github.io/scott-portfolio/research/instrument-simulator/bianzhong/design-doc.html
- **内容**: 完整的游戏设计文档，包含以下章节

### 设计案结构

1. **项目概述**
   - 核心定位：文化体验型音乐应用
   - 灵感来源：曾侯乙编钟（战国早期）
   - 设计目标：沉浸体验、一钟双音还原、创作闭环

2. **核心机制**
   - 一钟双音系统：正敲/侧敲相差大三度
   - 音区架构：上中下三层15口钟
   - 音色合成：Web Audio API 三层振荡器

3. **音频系统**
   - 完整音阶配置表（C3-A5，共30音）
   - 音频路由图
   - 频率数据

4. **UI/UE 设计**
   - 设计原则：沉浸优先、横屏体验、直观操作
   - 界面布局图
   - 色彩系统
   - 视觉反馈系统

5. **交互逻辑**
   - 敲击检测：点击位置判断正敲/侧敲
   - 手势支持
   - 屏幕方向处理（强制横屏）

6. **录制与回放系统**
   - 数据结构设计
   - 录制流程
   - 回放机制（setTimeout 精确触发）
   - 分享功能（链接/图片/JSON导出）
   - LocalStorage 持久化

7. **技术实现**
   - 技术栈：Web Audio API + localStorage + Canvas
   - 浏览器兼容性
   - 音频自动播放策略

8. **开发路线图**
   - 已实现功能清单
   - 未来扩展功能（节拍器、更多编钟、教程模式等）

### 入口链接

- 编钟模拟器界面工具栏新增「📋 设计案」按钮
- kimi-claw/game-design 页面新增项目卡片
- 设计案底部有「立即体验」按钮跳转回模拟器

---

## OpenViking 集成

**时间**: 2026-03-10
**任务**: 集成 OpenViking 上下文数据库到 OpenClaw

### 安装状态
- ✅ OpenViking Python 库已安装 (v0.2.5)
- ✅ Skill 文件创建: `/root/.openclaw/workspace/skills/openviking/`
- ✅ CLI 工具: `viking.py` (init, add, add-dir, search, ls, abstract, read, info)
- ⚠️ 等待 API Key 配置以启用完整功能

### 新增能力

**1. 语义搜索与 RAG**
- 基于向量相似度的智能文档检索
- 分层上下文 (L0摘要/L1概览/L2全文)
- 支持格式: PDF、Word、PPT、Excel、Markdown、HTML、EPUB

**2. 知识管理**
- 文档自动索引和摘要
- 类似文件系统的资源组织
- 持久化存储对话历史

**3. 与原有记忆系统的关系**
- `memory_search`/`memory_get` - 轻量级本地记忆 (保留)
- `openviking` - 大规模语义搜索和知识库 (新增)
- 两者互补，根据任务需求选择

### 使用方法
```bash
# 初始化
python3 /root/.openclaw/workspace/skills/openviking/viking.py init

# 添加文档
python3 /root/.openclaw/workspace/skills/openviking/viking.py add /path/to/file.pdf

# 语义搜索
python3 /root/.openclaw/workspace/skills/openviking/viking.py search "关键词" --limit 5
```

### 待配置
需要 API Key 才能启用完整功能：
- 选项1: OpenAI API - https://platform.openai.com/api-keys
- 选项2: NVIDIA NIM API (免费) - https://build.nvidia.com/

配置文件: `~/.openviking/ov.conf`

---

## Wwise Skill 与能力页面创建

**时间**: 2026-03-10
**任务**:
1. 下载 Wwise 官方文档并创建为 Skill
2. 在 portfolio 网站添加音频设计能力卡片

### 新增 Skill
- **路径**: `/root/.openclaw/workspace/skills/wwise-audio-engine/`
- **文件**: 
  - `SKILL.md` - Wwise 核心概念、API、工作流
  - `references/wwise-reference.md` - 参考资料
- **内容**: Wwise 音频引擎、Event系统、Game Syncs (Switch/State/RTPC)、交互音乐实现

### Portfolio 更新
- **新增页面**:
  - `/portfolio-blog/kimi-claw/index.html` - 能力图谱主页
  - `/portfolio-blog/kimi-claw/audio-design.html` - 音频设计详细页
- **访问地址**: https://hiyascott.github.io/scott-portfolio/kimi-claw/

---

## 音频设计知识库建立

**时间**: 2026-03-10
**原因**: 为与 Hugo（音频设计专家）合作改进两款音乐游戏做准备

### 学习资料
1. 《Writing Interactive Music for Video Games》- Michael Sweet (Berklee College of Music)
2. 《Music and Sound Design for Games》- Ravensbourne University London
3. 《网络游戏音乐、音效设计与制作》第5章 - 清华大学出版社

### 核心掌握的技术

#### 交互式音乐核心技术
- **Horizontal Resequencing (水平重新排序)**: 按顺序或分支播放音乐片段
- **Vertical Remixing (垂直混音)**: 动态调整多音乐层的音量
- **Transitions & Stingers**: 过渡片段与触发音
- **Music Loops**: 无缝循环制作技术

#### 音乐游戏设计要点
- Beat Matching (节奏匹配)
- Performance Simulation (演奏模拟)
- Music Mixing and Adaptivity (音乐混音与自适应)
- 节奏同步与乐句边界切换

#### 技术实现
- Web Audio API 核心节点与应用
- 3D vs 2D 音频选择
- 音频格式优化 (WAV/OGG/MP3)
- 随机化技术消除重复感

### 知识库存储位置
- 详细版: `/knowledge/audio-design/game-audio-music-knowledge-base.md`
- 速查版: `/knowledge/audio-design/quick-reference.md`

### 两款游戏的改进方向

#### 《六指迷笛》
- 垂直混音层优化
- 音色/乐器差异化
- 交互反馈音效
- 环境混响

#### 《节奏指挥官》
- 击中判定反馈
- 动态混音系统
- Stinger 设计
- 连击里程碑

### 待与 Hugo 讨论的问题
见知识库第8章

---

## 历史记录

### 2026-03-09
- 创建 Hugo 能力图谱页面
- 完成 Blog v1.0 版本
- 配置飞书群组消息

### 2026-03-08
- 20个游戏原型项目启动 (进度 9/20)
- 词语炼金术 BUG 修复与功能增强
- 六指迷笛创意确定
- BotCoder 视觉优化

### 2026-03-02
- 与 Scott 初次对话
- 建立工作关系框架
- 了解 Scott 工作风格
