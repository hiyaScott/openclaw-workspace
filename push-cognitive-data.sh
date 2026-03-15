#!/bin/bash
# 自动提交认知监控数据到 GitHub Pages

REPO_DIR="/root/.openclaw/workspace/portfolio-blog"
DATA_FILE="status-monitor/cognitive-data.json"

cd "$REPO_DIR" || exit 1

# 检查文件是否有变化
if git diff --quiet "$DATA_FILE" 2>/dev/null; then
    # 文件无变化
    exit 0
fi

# 添加文件
git add "$DATA_FILE"

# 提交（带时间戳）
git commit -m "chore: 更新认知监控数据 $(date '+%Y-%m-%d %H:%M:%S')"

# 推送（使用 HTTP/1.1 避免超时）
git config http.version HTTP/1.1
git push origin main

# 记录日志
echo "[$(date)] Data pushed to GitHub Pages"
