#!/bin/bash
# 自毁式下载监控脚本
# 每5分钟检查 task-state.json 中的指定任务状态
# 如果任务完成或失败，自动删除 cron job

TASK_NAME="${1:-godot_templates}"
STATE_FILE="/root/.openclaw/workspace/task-state.json"
CRON_JOB_ID="monitor-download-${TASK_NAME}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查任务: ${TASK_NAME}"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "状态文件不存在，等待下次检查..."
    exit 0
fi

# 读取状态
STATUS=$(cat "$STATE_FILE" | grep -A 5 "\"${TASK_NAME}\"" | grep '"status"' | head -1 | cut -d'"' -f4)

if [[ -z "$STATUS" ]]; then
    echo "未找到任务状态，等待下次检查..."
    exit 0
fi

echo "当前状态: ${STATUS}"

# 如果任务完成或失败，删除 cron job
if [[ "$STATUS" == "completed" ]] || [[ "$STATUS" == "failed" ]]; then
    echo "任务已结束 (${STATUS})，正在清理监控任务..."
    
    # 使用 openclaw cron 删除任务
    curl -s -X POST "http://localhost:8080/api/cron/remove" \
         -H "Content-Type: application/json" \
         -d "{\"jobId\":\"${CRON_JOB_ID}\"}" 2>/dev/null || true
    
    # 同时发送通知
    curl -s -X POST "http://localhost:8080/api/message/send" \
         -H "Content-Type: application/json" \
         -d "{\"channel\":\"feishu\",\"message\":\"✅ 下载任务监控: ${TASK_NAME} 已完成 (${STATUS})，监控任务已自动关闭\"}" 2>/dev/null || true
    
    echo "监控任务已关闭"
else
    echo "任务仍在进行中，5分钟后再次检查..."
fi
