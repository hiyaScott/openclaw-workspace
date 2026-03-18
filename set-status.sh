#!/bin/bash
# 自动状态管理脚本 v2
# 用法: ./set-status.sh [ready|busy|error] [任务描述]

STATUS_FILE="/root/.openclaw/workspace/portfolio-blog/status-monitor/status.json"
STATUS=$1
TASK=$2

if [ -z "$STATUS" ]; then
    echo "用法: $0 [ready|busy|error] [任务描述]"
    exit 1
fi

# 状态文本映射
case $STATUS in
    ready)
        STATUS_TEXT="就绪"
        TASK_DESC="null"
        ;;
    busy)
        STATUS_TEXT="处理中"
        TASK_DESC="\"$TASK\""
        ;;
    error)
        STATUS_TEXT="异常"
        TASK_DESC="\"$TASK\""
        ;;
    *)
        echo "无效状态: $STATUS (应为 ready/busy/error)"
        exit 1
        ;;
esac

# 生成时间戳
NOW=$(date -Iseconds)

# 写入状态文件
cat > "$STATUS_FILE" << EOF
{
  "status": "$STATUS",
  "status_text": "$STATUS_TEXT",
  "since": "$NOW",
  "current_task": $TASK_DESC,
  "last_heartbeat": "$NOW",
  "session_uptime": "active",
  "channel": "feishu",
  "model": "kimi-coding/k2p5"
}
EOF

# 提交到GitHub (静默)
cd /root/.openclaw/workspace/portfolio-blog
if git diff --quiet status-monitor/status.json 2>/dev/null; then
    echo "状态未变更: $STATUS_TEXT"
else
    git add status-monitor/status.json > /dev/null 2>&1
    git commit -m "status: $STATUS_TEXT - ${TASK:-idle}" > /dev/null 2>&1
    git push > /dev/null 2>&1 &
    echo "状态已更新: $STATUS_TEXT (已同步到GitHub)"
fi
