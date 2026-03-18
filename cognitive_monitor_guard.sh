#!/bin/bash
# 认知监控进程守护脚本
# 如果进程崩溃，自动重启

LOG_FILE="/var/log/cognitive_monitor.log"
PID_FILE="/var/run/cognitive_monitor.pid"
SCRIPT="/root/.openclaw/workspace/cognitive_monitor.py"

check_and_restart() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            # 进程正常运行
            return 0
        fi
    fi
    
    # 进程不存在，需要重启
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 认知监控进程未运行，正在重启..." >> "$LOG_FILE"
    
    # 启动进程
    nohup python3 -u "$SCRIPT" >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 进程已重启，PID: $NEW_PID" >> "$LOG_FILE"
}

# 主循环
while true; do
    check_and_restart
    sleep 30
done
