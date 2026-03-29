# Shrimp Jetton 认知负载监控系统
## 完整设计文档 v7.3

**文档版本**: 1.0  
**系统版本**: v7.3  
**创建日期**: 2026-03-28  
**作者**: Scott & Jetton  

---

## 目录

1. [项目概述](#1-项目概述)
2. [设计目标](#2-设计目标)
3. [系统架构](#3-系统架构)
4. [数据流设计](#4-数据流设计)
5. [评分算法](#5-评分算法)
6. [前端设计](#6-前端设计)
7. [任务分类系统](#7-任务分类系统)
8. [部署与运维](#8-部署与运维)
9. [关键决策](#9-关键决策)
10. [扩展指南](#10-扩展指南)

---

## 1. 项目概述

### 1.1 背景

在 OpenClaw AI 助手 (Shrimp Jetton) 的日常协作中，协作者 (Scott) 需要了解 Jetton 的当前工作状态，以便：
- 在系统空闲时派发新任务
- 在系统繁忙时避免打扰
- 了解任务处理进度和预计等待时间

### 1.2 解决方案

开发一个实时认知负载监控系统，通过 Web 页面可视化展示：
- 当前认知负载评分 (0-100)
- 活跃任务队列
- 系统资源占用
- 历史负载趋势

### 1.3 核心价值

| 价值点 | 描述 |
|--------|------|
| **透明度** | 协作者可随时了解系统状态，无需询问 "Are you busy?" |
| **可预测性** | 基于评分和预计等待时间，合理安排任务派发 |
| **可验证性** | 所有数字可交叉验证，建立信任 |
| **无侵入** | 零配置，自动采集，不影响正常工作 |

---

## 2. 设计目标

### 2.1 核心指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **数据延迟** | < 2分钟 | Redis实时数据 |
| **趋势延迟** | 3-5分钟 | CDN回退数据可接受 |
| **可用性** | 99.9% | Redis故障时自动回退CDN |
| **一致性** | 100% | Sessions/Tokens/Task Queue数字一致 |

### 2.2 设计原则

1. **数据与逻辑分离**: 监控数据和页面代码独立仓库管理
2. **渐进增强**: 基础功能无需额外基础设施，高级功能可扩展
3. **体感优先**: 评分算法以人类体感为准，而非纯技术指标
4. **自证可信**: 所有数字可验证，避免 "黑盒" 感

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              cognitive-status.html                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  信息栏      │  │  状态仪表盘  │  │  趋势图      │  │  │
│  │  │  (版本/数据源/│  │  (Score/     │  │  (0.5h/6h/  │  │  │
│  │  │   时间/倒计时)│  │   Sessions/  │  │   12h)      │  │  │
│  │  │              │  │   Tokens)    │  │              │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↑ 30秒轮询                        │
└──────────────────────────┬─────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
    ┌──────▼──────┐                ┌──────▼──────┐
    │   Redis     │◄─────失败─────►│    CDN      │
    │  (实时数据)  │                │  (回退数据)  │
    │  <2分钟延迟  │                │  3-5分钟延迟 │
    └──────┬──────┘                └──────┬──────┘
           │                               │
           └───────────────┬───────────────┘
                           │
┌──────────────────────────┼─────────────────────────────────┐
│                          │         服务端 (Linux)           │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │              cognitive_monitor.py (Python)           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  会话分析    │  │  负载计算    │  │  任务分类    │  │  │
│  │  │  (60秒周期)  │  │  (Mixed Score│  │  (24分类)   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                │
│              ┌────────────┴────────────┐                 │
│              ↓                         ↓                 │
│    ┌─────────────────┐      ┌─────────────────┐         │
│    │  Upstash Redis  │      │  GitHub Pages   │         │
│    │  (实时数据)      │      │  (趋势数据)      │         │
│    └─────────────────┘      └─────────────────┘         │
└───────────────────────────────────────────────────────────┘
```

### 3.2 双仓库架构

#### 架构设计

| 仓库 | 用途 | 内容 | 更新频率 |
|------|------|------|----------|
| `scott-portfolio` | 逻辑仓库 | HTML/JS/CSS 页面代码 | 功能迭代时 |
| `scott-portfolio-data` | 数据仓库 | JSON/JSONL 监控数据 | 每2分钟 |

#### 分离价值

1. **独立生命周期**: 页面改版不影响数据累积
2. **历史清晰**: 主仓库commit历史不被数据污染
3. **回滚安全**: 两个仓库可独立回滚
4. **权限分离**: 可分别设置访问权限

---

## 4. 数据流设计

### 4.1 数据采集流程

```
每分钟
    ↓
读取 /root/.openclaw/agents/main/sessions/*.jsonl
    ↓
分析每个会话:
    - 等待时间 (最后用户消息时间)
    - Token数量 (内容长度估算)
    - 任务标签 (关键词匹配)
    - 任务分类 (24分类系统)
    ↓
计算 Mixed Score
    ↓
写入 Redis (实时)
写入本地文件 (备份)
    ↓
每2分钟
    ↓
推送到 GitHub (Data仓库)
    ↓
GitHub Pages 自动部署
```

### 4.2 数据格式

#### 实时数据 (Redis)

```json
{
  "timestamp": "2026-03-28T13:44:03+00:00",
  "cognitive_score": 37,
  "status_code": "medium",
  "status_text": "🟡 轻负载",
  "suggestion": "30秒内响应",
  "active_sessions": 4,
  "pending_count": 1,
  "processing_count": 2,
  "total_tokens": 252000,
  "total_tokens_formatted": "252.0k",
  "task_queue": [
    {
      "label": "👥 系统监控",
      "status": "🔄 处理中",
      "tokens": 59810,
      "category": "系统",
      "category_icon": "🔧"
    }
  ],
  "score_breakdown": {
    "wait_score": 10,
    "token_score": 0,
    "queue_score": 6,
    "active_score": 8,
    "system_score": 5,
    "processing_bonus": 6,
    "base_score": 29,
    "final_score": 37
  },
  "cpu_percent": 0.5,
  "memory_percent": 54.1
}
```

#### 趋势数据 (JSON Lines)

```jsonl
{"timestamp": "2026-03-28T13:44:03", "score": 37, "sessions": 4, "pending": 1, "processing": 2, "tokens": 252000, "cpu": 0.5, "memory": 54.1}
{"timestamp": "2026-03-28T13:42:03", "score": 28, "sessions": 3, "pending": 0, "processing": 1, "tokens": 198000, "cpu": 0.3, "memory": 52.8}
```

### 4.3 数据一致性保证

**方案1实施**:
- `active_sessions` = `len(task_queue)`
- `total_tokens` = `sum(t.tokens for t in task_queue)`

**验证代码**:
```python
assert data['active_sessions'] == len(data['task_queue'])
assert data['total_tokens'] == sum(t['tokens'] for t in data['task_queue'])
```

---

## 5. 评分算法

### 5.1 Mixed Score v7.1

#### 算法公式

```
Score = min(BaseScore + ProcessingBonus, 100)

BaseScore = WaitScore + TokenScore + QueueScore + ActiveScore + SystemScore

ProcessingBonus = min(ProcessingCount × 3, 10)
```

#### 各项评分详解

##### 1. 等待评分 (WaitScore)

| 等待时间 | 分数 | 说明 |
|----------|------|------|
| ≤ 2分钟 | 0 | 正常响应时间 |
| 2-5分钟 | 10 | 轻微延迟 |
| 5-10分钟 | 15 | 明显延迟 |
| > 10分钟 | 20 | 严重延迟 |

**计算**: `max_wait` = 所有等待中任务的最长等待时间

##### 2. Token评分 (TokenScore)

| 处理中Tokens | 分数 |
|--------------|------|
| 0 | 0 |
| 200k | 5 |
| 400k | 10 |
| 600k | 15 |
| 800k | 20 |
| ≥ 1M | 25 |

**计算**: `processing_tokens` = 所有处理中任务的tokens总和

##### 3. 队列评分 (QueueScore)

| 队列长度 | 分数 | 说明 |
|----------|------|------|
| 0 | 0 | 空闲 |
| 1 | 2 | 轻微负载 |
| 2 | 6 | 中等负载 |
| 3 | 12 | 较高负载 |
| 4 | 20 | 高负载 |
| ≥ 5 | 25 | 严重负载 |

**设计意图**: 非线性增长，突出多任务的影响

##### 4. 活跃评分 (ActiveScore)

| 最近活跃会话数 | 分数 |
|----------------|------|
| 0 | 0 |
| 1 | 2 |
| 2 | 4 |
| 3 | 6 |
| 4 | 8 |
| ≥ 5 | 10 |

**定义**: "最近活跃" = 5分钟内有新消息

##### 5. 系统评分 (SystemScore)

| (CPU% + 内存%) / 20 | 分数 |
|---------------------|------|
| 0-20 | 0-1 |
| 20-40 | 1-2 |
| 40-60 | 2-3 |
| 60-80 | 3-4 |
| 80-100 | 4-5 |
| > 100 | 5-10 |

##### 6. 处理加成 (ProcessingBonus)

| 处理中任务数 | 加成 |
|--------------|------|
| 0 | 0 |
| 1 | 3 |
| 2 | 6 |
| 3 | 9 |
| ≥ 4 | 10 |

### 5.2 负载等级划分

| 分数 | 等级 | 颜色 | 建议 |
|------|------|------|------|
| 0-10 | 空闲 | 🟢 #22c55e | 可立即响应 |
| 11-25 | 轻负载 | 🔵 #3b82f6 | 30秒内响应 |
| 26-50 | 中等 | 🟡 #eab308 | 可派简单任务 |
| 51-75 | 高负载 | 🟠 #f97316 | 建议等待 |
| 76-100 | 繁忙 | 🔴 #ef4444 | 系统忙碌 |

---

## 6. 前端设计

### 6.1 信息栏设计

#### 单行信息展示

```
v7.3 | ● Redis | 13:44:12 | 18s
```

| 元素 | 格式 | 说明 |
|------|------|------|
| 版本号 | `v7.3` | 系统版本 |
| 数据源 | `● Redis` / `● CDN` | 绿色=Redis, 橙色=CDN |
| 数据时间戳 | `HH:MM:SS` | 数据本身的采集时间 |
| 倒计时 | `Xs` | 距离下次刷新秒数 |

#### 倒计时逻辑

```javascript
// 每次成功获取数据后重置
nextRefreshTime = Date.now() + REFRESH_INTERVAL;  // 30秒后

// 每秒更新显示
remaining = ceil((nextRefreshTime - now) / 1000);
```

### 6.2 状态仪表盘

#### 收音机调频设计

```
┌─────────────────────────────────────────────────────┐
│  📻 STATUS TUNER          ┌──────────────────┐     │
│                           │   当前状态        │     │
│   ◀━━━━━━━━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━▶   │
│   0        25        50        75       100         │
│  空闲     轻负载    中等      高负载    繁忙        │
│                                                     │
│               [ 37% 🟡 轻负载 ]                    │
└─────────────────────────────────────────────────────┘
```

#### 核心指标卡片

| 指标 | 值 | 来源 |
|------|-----|------|
| **Sessions** | 4 | `len(task_queue)` |
| **Pending** | 1 | `pending_count` |
| **Processing** | 2 | `processing_count` |
| **Tokens** | 252.0k | `sum(t.tokens for t in task_queue)` |

### 6.3 任务队列设计

#### 单行任务显示

```
[🔧 系统] 心跳监控 | 54.9k token | 处理中
[📝 内容] 文档编写 | 12.3k token | 等待中
[🎮 作品] 游戏开发 | 89.1k token | 已回复
```

#### 状态标识

| 状态 | 标识 | 颜色 |
|------|------|------|
| 处理中 | 🔄 | 黄色 |
| 等待中 | ⏳ | 橙色 |
| 已回复 | ✅ | 绿色 |
| 活跃中 | 💤 | 灰色 |

### 6.4 趋势图设计

#### 时间范围切换

| 按钮 | 范围 | 数据点 |
|------|------|--------|
| 0.5h | 最近30分钟 | ~30个点 |
| 6h | 最近6小时 | ~360个点 |
| 12h | 最近12小时 | ~720个点 |

#### 图表元素

- **折线**: 负载分数变化
- **颜色渐变**: 0-100分对应绿色→黄色→红色
- **平均线**: 虚线显示平均值
- **统计**: 最高/最低/平均分数

---

## 7. 任务分类系统

### 7.1 24分类体系

6大类别 × 每类多关键词 = 24种细分任务类型

#### 分类详情

| 类别 | 图标 | 关键词 | 典型任务 |
|------|------|--------|----------|
| **研究** | 🔬 | 分析、竞品、调研、benchmark、技术选型 | 竞品分析报告、技术方案设计 |
| **作品** | 🎮 | 游戏开发、Godot、Unity、创意工具、前端 | 游戏原型、交互页面、创意demo |
| **开发** | ⚙️ | 后端、API、自动化、DevOps、部署 | API开发、CI/CD配置、脚本编写 |
| **内容** | 📝 | 文档、GDD、写作、文案、教程 | 设计文档、技术博客、使用手册 |
| **系统** | 🔧 | 监控、状态、cron、飞书、通知 | 状态监控、定时任务、消息集成 |
| **其他** | 📦 | (无特定关键词) | 临时任务、杂项 |

### 7.2 分类算法

```python
def classify_task(content):
    """根据内容匹配任务分类"""
    content_lower = content.lower()
    
    # 按优先级匹配
    category_order = ["研究", "作品", "开发", "内容", "系统"]
    
    for category in category_order:
        keywords = TASK_CATEGORIES[category]["keywords"]
        if any(kw in content_lower for kw in keywords):
            return category
    
    return "其他"
```

---

## 8. 部署与运维

### 8.1 环境要求

| 组件 | 要求 |
|------|------|
| **操作系统** | Linux (Ubuntu/CentOS) |
| **Python** | 3.8+ |
| **依赖包** | psutil, json (标准库) |
| **网络** | 可访问 Upstash Redis |
| **存储** | > 100MB (日志和历史数据) |

### 8.2 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/hiyaScott/scott-portfolio.git
cd scott-portfolio/status-monitor
```

#### 2. 安装依赖

```bash
pip3 install psutil
```

#### 3. 配置环境变量

```bash
export UPSTASH_REDIS_REST_URL="https://your-redis.upstash.io"
export UPSTASH_REDIS_REST_TOKEN="your-token"
```

#### 4. 配置定时任务

```bash
crontab -e

# 添加以下行
* * * * * cd /path/to/scott-portfolio/status-monitor && /usr/bin/python3 cognitive_monitor.py >> /var/log/cognitive_monitor.log 2>&1
*/2 * * * * cd /path/to/scott-portfolio && bash status-monitor/cognitive_push_v7.sh >> /var/log/cognitive_health.log 2>&1
```

#### 5. 创建Data仓库

```bash
# 创建新的GitHub仓库: scott-portfolio-data
git clone https://github.com/yourname/scott-portfolio-data.git
mkdir -p scott-portfolio-data/status-monitor
git add .
git commit -m "Initial commit"
git push origin main

# 在GitHub Settings → Pages 启用GitHub Pages
```

### 8.3 监控与告警

#### 日志文件

| 日志 | 路径 | 内容 |
|------|------|------|
| 监控日志 | `/var/log/cognitive_monitor.log` | Python脚本执行记录 |
| 推送日志 | `/var/log/cognitive_health.log` | GitHub推送记录 |

#### 健康检查

```bash
# 检查Redis连接
curl -H "Authorization: Bearer $TOKEN" "$REDIS_URL/get/cognitive.json"

# 检查Data仓库
curl https://yourname.github.io/scott-portfolio-data/status-monitor/cognitive-data.json

# 检查页面
curl https://yourname.github.io/scott-portfolio/status-monitor/cognitive-status.html
```

---

## 9. 关键决策

### 9.1 决策记录

#### Decision 1: 双仓库架构 (2026-03-28)

**背景**: 主仓库commit历史被监控数据污染

**选项**:
- A: 继续单仓库，定期清理历史
- B: 使用独立分支存放数据
- C: **独立Data仓库** ✅

**选择C的原因**:
- 完全分离生命周期
- 独立权限管理
- 历史趋势长期累积

#### Decision 2: Mixed Score算法 (2026-03-28)

**背景**: 简单队列长度无法反映真实负载

**设计**:
- 8因素加权评分
- 非线性增长突出多任务影响
- 体感阈值优化

#### Decision 3: 方案1数据一致性 (2026-03-28)

**背景**: Sessions/Tokens与Task Queue显示不一致

**方案1**:
- Sessions = len(task_queue)
- Tokens = sum(task_queue tokens)

**价值**: 数字可交叉验证，建立信任

### 9.2 权衡与妥协

| 权衡点 | 选择 | 原因 |
|--------|------|------|
| 实时性 vs 成本 | 30秒轮询 | 平衡实时性和API调用成本 |
| 准确性 vs 复杂度 | 估算Token | 无需集成真实Token计数器 |
| 丰富性 vs 性能 | 24分类 | 足够细分又不影响性能 |

---

## 10. 扩展指南

### 10.1 添加新指标

```python
# 1. 在 cognitive_monitor.py 中添加采集逻辑
def get_new_metric():
    return {"new_metric": value}

# 2. 更新数据结构
data["new_metric"] = get_new_metric()

# 3. 在前端添加展示
// updateUI 函数中添加
getEl('newMetricValue').textContent = data.new_metric;
```

### 10.2 自定义评分算法

```python
# 修改 get_cognitive_load 函数
# 调整各项权重或添加新因素

custom_score = (
    wait_score * 0.3 +      # 提高等待权重
    token_score * 0.2 +
    queue_score * 0.2 +
    active_score * 0.1 +
    system_score * 0.1 +
    new_factor * 0.1        # 添加新因素
)
```

### 10.3 集成第三方服务

#### Slack通知

```python
import requests

def notify_slack(score):
    if score > 75:
        requests.post(SLACK_WEBHOOK, json={
            "text": f"⚠️ 高负载警告: {score}%"
        })
```

#### Prometheus指标

```python
from prometheus_client import Gauge

cognitive_score_gauge = Gauge('cognitive_score', 'Current cognitive load score')

def update_metrics(data):
    cognitive_score_gauge.set(data['cognitive_score'])
```

---

## 附录

### A. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v7.0 | 2026-03-XX | 基础框架 |
| v7.1 | 2026-03-28 | Mixed Score算法优化 |
| v7.2 | 2026-03-28 | 24任务分类系统 |
| v7.3 | 2026-03-28 | 架构分离 + 数据一致性方案 |

### B. 参考资源

- **Redis**: https://upstash.com/
- **GitHub Pages**: https://pages.github.com/
- **Canvas API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

### C. 联系信息

- **项目地址**: https://github.com/hiyaScott/scott-portfolio
- **监控页面**: https://hiyascott.github.io/scott-portfolio/status-monitor/cognitive-status.html

---

**文档结束**
