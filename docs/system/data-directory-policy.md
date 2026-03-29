# 认知负载监控 - 数据目录规范

## 问题背景

历史上曾多次出现数据膨胀问题：
- v5.33: cognitive-history.json 膨胀到 1.2GB
- v5.34: trend-data.json 无限增长
- 原因：历史数据未清理、重复数据、日志未轮转

## 规范方案

### 1. 文件大小上限

| 文件 | 最大大小 | 超限处理 |
|------|----------|----------|
| cognitive-data.json | 50KB | 无需处理 |
| trend-data.json | 500KB | 保留最近500条 |
| cognitive-history.jsonl | 5MB | 归档到月份文件 |

### 2. 历史数据归档策略

```
archives/
├── 2026-03/
│   ├── cognitive-history-2026-03-01.jsonl
│   └── cognitive-history-2026-03-15.jsonl
└── 2026-04/
    └── ...
```

- 每月初自动归档上个月的 jsonl 数据
- 当前月数据保留在根目录

### 3. 监控检查清单

每周检查（可自动化）：
```bash
# 检查文件大小
du -sh status-monitor/*.json*

# 检查 Git 仓库大小
git count-objects -vH

# 检查是否有异常大文件
find . -type f -size +50M
```

### 4. 预防措施

1. **自动清理**：监控脚本每月自动归档历史数据
2. **大小告警**：单个文件超过 10MB 时发送通知
3. **Git 忽略**：大日志文件加入 .gitignore（但 data.json 需要推送）

### 5. 已实施的清理

- ✅ v5.34: 清理重复数据，从 1.2GB 降到 4KB
- ✅ v5.35: 移除 cognitive-history.json，改用追加式 jsonl
- ✅ v5.36: 添加数据保留策略（保留最近 N 条）

## 当前状态

| 文件 | 当前大小 | 状态 |
|------|----------|------|
| cognitive-data.json | 4KB | ✅ 正常 |
| trend-data.json | 8KB | ✅ 正常 |
| cognitive-history.jsonl | 1.2MB | ✅ 正常 |

**结论**：当前数据目录健康，规范已生效。
