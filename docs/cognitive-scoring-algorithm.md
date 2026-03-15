# 认知评分算法文档

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2026-03-15 | 初始版本，Mixed Score算法 |

## 当前版本: v1.0.0

### 算法名称
**Mixed Score Algorithm** (混合评分算法)

### 核心思想
认知负载 = max(等待评分, Token评分) + 处理加成

### 输入参数

| 参数 | 说明 | 单位 |
|------|------|------|
| `pending_count` | 待处理消息数 | 个 |
| `processing_count` | 处理中任务数 | 个 |
| `total_tokens` | 处理中任务Token总量 | 个 |
| `max_wait_seconds` | 最长等待时间 | 秒 |

### 计算步骤

#### 1. 等待评分 (Wait Score)
基于最长等待时间计算，反映用户等待的焦虑程度。

```
if max_wait_seconds == 0:
    wait_score = 0
elif max_wait_seconds < 10:
    wait_score = min(30, 20 + max_wait_seconds)
elif max_wait_seconds < 30:
    wait_score = min(55, 30 + (max_wait_seconds - 10) * 1.25)
elif max_wait_seconds < 60:
    wait_score = min(80, 55 + (max_wait_seconds - 30) * 0.83)
else:
    wait_score = min(95, 80 + (max_wait_seconds - 60) * 0.25)
```

**分段说明：**
- 0-10s: 20-30% (轻微等待)
- 10-30s: 30-55% (明显等待)
- 30-60s: 55-80% (焦虑等待)
- 60s+: 80-95% (严重延迟)

#### 2. Token评分 (Token Score)
基于处理中任务的Token量，反映AI处理内容的复杂度。

```
if total_tokens < 10000:
    token_score = total_tokens / 1000
elif total_tokens < 50000:
    token_score = 10 + (total_tokens - 10000) / 2000
elif total_tokens < 100000:
    token_score = 30 + (total_tokens - 50000) / 2000
else:
    token_score = min(80, 55 + (total_tokens - 100000) / 4000)
```

**参考值：**
- 10k tokens: 10%
- 50k tokens: 30%
- 100k tokens: 50%
- 200k+ tokens: 75-80%

#### 3. 处理加成 (Processing Bonus)
每个处理中任务增加系统负载。

```
processing_bonus = min(15, processing_count * 3)
```

- 每个任务: +3%
- 上限: +15% (5个任务)

#### 4. 最终评分

```
mixed_score = max(wait_score, token_score) + processing_bonus
final_score = min(100, max(0, int(mixed_score)))
```

### 状态阈值

| 分数范围 | 状态 | 颜色 | 建议 |
|----------|------|------|------|
| 0-20% | 🟢 空闲 | 绿色 | 可立即响应 |
| 20-40% | 🔵 低负载 | 蓝色 | 可正常交互 |
| 40-60% | 🟡 中等负载 | 黄色 | 建议简单任务 |
| 60-80% | 🟠 高负载 | 橙色 | 建议等待 |
| 80-100% | 🔴 满载 | 红色 | 建议稍后 |

### 算法优势

1. **双维度评估**: 同时考虑时间和复杂度
2. **非线性增长**: 等待时间越长，权重越高
3. **处理惩罚**: 并发任务越多，响应越慢
4. **边界保护**: 评分始终在 0-100% 之间

### 注意事项

- 评分是**估算值**，非精确测量
- Token只统计**处理中**任务，已完成的不计入
- 等待时间只统计**待处理**消息
