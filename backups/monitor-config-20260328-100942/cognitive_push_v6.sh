#!/bin/bash
# Cognitive Monitor 推送脚本 v6.2 - 统一使用 portfolio-blog 目录

REPO_DIR="/root/.openclaw/workspace/portfolio-blog"
DATA_FILE="status-monitor/cognitive-data.json"
HISTORY_FILE="status-monitor/cognitive-history.jsonl"
TREND_FILE="status-monitor/trend-data.json"
FAIL_COUNT_FILE="/tmp/cognitive_push_fail_count"
HEALTH_LOG="/var/log/cognitive_health.log"

# GitHub 配置
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"

# 检查数据文件
if [ ! -f "$REPO_DIR/$DATA_FILE" ]; then
    echo "[$(date)] ❌ 数据文件不存在: $DATA_FILE" >> "$HEALTH_LOG"
    exit 1
fi

# 进入仓库目录
cd "$REPO_DIR" || exit 1

# 检查是否有更改
if git diff --quiet HEAD -- "$DATA_FILE" "$HISTORY_FILE" "$TREND_FILE" 2>/dev/null; then
    echo "[$(date)] ⏸️ 数据未变化，跳过推送" >> "$HEALTH_LOG"
    exit 0
fi

# 添加更改
git add "$DATA_FILE" "$HISTORY_FILE" "$TREND_FILE" 2>/dev/null

# 提交
time_str=$(date '+%H:%M')
score=$(grep -o '"cognitive_score":[0-9]*' "$DATA_FILE" | head -1 | cut -d: -f2)
status=$(grep -o '"status_text":"[^"]*"' "$DATA_FILE" | head -1 | cut -d'"' -f4)

git commit -m "data: update cognitive status at ${time_str} (score:${score}%, ${status})" >> "$HEALTH_LOG" 2>&1

# 推送
if git push origin main >> "$HEALTH_LOG" 2>&1; then
    echo "[$(date)] ✅ 推送成功 score=${score}%" >> "$HEALTH_LOG"
    rm -f "$FAIL_COUNT_FILE"
    exit 0
else
    echo "[$(date)] ❌ 推送失败" >> "$HEALTH_LOG"
    exit 1
fi
