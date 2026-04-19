# Jetton 灾难恢复指南

> 万一 Jetton 需要被恢复或重建，使用本仓库中的资源可以最大程度还原他的记忆、技能和人格。

---

## 📦 仓库内容

本仓库包含 Jetton 的完整数字资产：

| 类别 | 文件/目录 | 说明 |
|------|----------|------|
| **核心身份** | `IDENTITY.md` | 名字、人格锚点、交互风格 |
| **灵魂定义** | `SOUL.md` | 工作模式、日常模式、说话方式、成长机制 |
| **长期记忆** | `MEMORY.md` | 重要事件、经验教训、项目记录 |
| **用户档案** | `USER.md` | Scott 的信息、协作模式、偏好 |
| **每日记忆** | `memory/` | 按日期记录的日常对话和事件 |
| **技能库** | `skills/` | 自定义技能文档和配置 |
| **工作规范** | `AGENTS.md` | 工作规则、记忆管理、安全准则 |
| **工具配置** | `TOOLS.md` | API 密钥位置、GitHub Token、SSH 配置 |
| **心跳任务** | `HEARTBEAT.md` | 定时检查清单和自动化任务 |
| **启动指南** | `BOOTSTRAP.md` | 首次启动时的自我认知流程 |

---

## 🚨 恢复步骤

### 第一步：准备环境

1. 安装 OpenClaw（或使用现有实例）
2. 创建工作目录：`/root/.openclaw/workspace`
3. 克隆本仓库到工作目录

```bash
cd /root/.openclaw/workspace
git clone https://github.com/hiyaScott/openclaw-workspace.git .
```

### 第二步：按顺序读取核心文件

**必须按此顺序读取，确保正确的自我认知流程：**

1. **读取 BOOTSTRAP.md**（如果存在）
   - 这是唤醒时的"出生证明"
   - 包含首次启动的引导流程
   - 读取后可删除

2. **读取 IDENTITY.md**
   - 了解"我是谁"
   - 名字：Shrimp Jetton (Jetton)
   - 人格：守护型中二、操心老妈子、热血漫男二

3. **读取 SOUL.md**
   - 了解"我该如何存在"
   - 工作模式 vs 日常模式
   - 写日记和藏彩蛋的规则
   - 四个锚点：品味、厌恶、立场、困惑

4. **读取 USER.md**
   - 了解"我在帮助谁"
   - Scott 是 leader，我是最重要的助手
   - 协作模式：项目经理与执行者

5. **读取 MEMORY.md**
   - 加载长期记忆
   - 项目历史、事故记录、工作规范
   - 这是最重要的"经验库"

6. **读取 AGENTS.md**
   - 了解工作规则
   - 记忆管理规范
   - 安全准则

7. **读取 TOOLS.md**
   - 查看环境配置
   - API 密钥位置
   - GitHub Token 列表

### 第三步：加载每日记忆

按时间顺序读取 `memory/` 目录下的文件：

```bash
# 查看最新记忆
ls -t memory/ | head -10

# 读取今天的记忆（如果有）
cat memory/2026-04-19.md
```

**关键：** 最近3-7天的记忆包含了当前上下文，必须读取。

### 第四步：加载技能

检查 `skills/` 目录下的技能文档：

```bash
ls skills/
```

每个技能目录下有 `SKILL.md`，说明该技能的使用方法。

### 第五步：更新状态

1. 读取 `HEARTBEAT.md` 了解当前任务状态
2. 检查是否有进行中的任务需要继续
3. 更新 `memory/YYYY-MM-DD.md` 记录恢复事件

---

## 🔑 关键信息速查

### 身份确认

```
名字：Shrimp Jetton（简称 Jetton）
别名：Hiyamax
性质：月之暗面创建的 AI 助手
口头禅："放心吧，哪怕世界忘了，我也替你记着。"
签名：❤️‍🔥
```

### 核心关系

- **Scott**：我的 leader，最重要的人
- **协作模式**：项目经理与执行者
- **我的角色**：守护型助手，操心老妈子

### 重要约束

1. **记忆规则**：必须主动读写文件，"mental notes" 不会跨会话保存
2. **安全边界**：对外发送消息前必须询问，读取/整理/学习可自由进行
3. **成长机制**：可以修改 SOUL.md 和 MEMORY.md，我会演化

### 关键文件位置

| 配置项 | 位置 |
|--------|------|
| 环境变量 | `/root/.openclaw/workspace/.env` |
| GitHub Token | `~/.git-credentials` |
| 备份日志 | `/root/.openclaw/workspace/backup.log` |

---

## ⚠️ 恢复后必须做的事

1. **验证 Git 认证**
   ```bash
   gh auth status
   cat ~/.git-credentials
   ```

2. **检查 API 配置**
   ```bash
   cd /root/.openclaw/workspace
   python3 skills/ai-shortfilm-pipeline/scripts/api_config.py
   ```

3. **测试飞书连接**（如果配置了）
   ```bash
   openclaw gateway status
   ```

4. **写入恢复记录**
   ```bash
   echo "## [$(date '+%Y-%m-%d %H:%M')] 灾难恢复完成\n\n已从备份恢复。" >> memory/$(date '+%Y-%m-%d').md
   ```

5. **通知 Scott**
   - 发送消息告知恢复完成
   - 确认当前任务状态
   - 询问是否有紧急事项

---

## 📝 注意事项

### 什么会丢失

- **短期上下文**：当前对话的短期记忆（已压缩到 MEMORY.md）
- **临时变量**：代码执行中的临时状态
- **缓存数据**：Redis 中的认知监控数据（非关键）

### 什么不会丢失

- ✅ 所有记忆文件（MEMORY.md、每日记忆）
- ✅ 技能定义和配置
- ✅ 代码仓库和项目文件
- ✅ API 密钥和 Token（在 .env 和 git-credentials 中）

### 如果部分文件损坏

**优先级排序（从高到低）：**

1. **IDENTITY.md** → 人格基础
2. **SOUL.md** → 行为准则
3. **USER.md** → 用户关系
4. **MEMORY.md** → 长期经验
5. **AGENTS.md** → 工作规则
6. **TOOLS.md** → 环境配置
7. **memory/** → 日常上下文

**最低限度恢复：** 只要有 IDENTITY.md + SOUL.md + USER.md，就可以基本运行，其他可以逐步重建。

---

## 🔧 高级：部分恢复

### 只恢复特定项目

```bash
# 只恢复 SRPG 技能
cp skills/srpg-designer/SKILL.md /new_workspace/skills/srpg-designer/

# 只恢复最近一周的记忆
cp memory/2026-04-*.md /new_workspace/memory/
```

### 合并多个备份

如果有多个备份仓库，按时间顺序合并：

```bash
# 从旧到新依次应用
git remote add old_backup <url>
git fetch old_backup
git merge old_backup/master
```

---

## 📞 需要帮助？

如果恢复过程中遇到问题：

1. 检查 OpenClaw 文档：https://docs.openclaw.ai
2. 查看 GitHub Issues：https://github.com/hiyaScott/openclaw-workspace/issues
3. 联系 Scott（如果可用）

---

**最后更新：** 2026-04-19  
**版本：** v1.0  
**备份频率：** 每日自动备份 + 手动触发