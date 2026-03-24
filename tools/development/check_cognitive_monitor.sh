#!/bin/bash
# 认知监控进程检查脚本（轻量级版本）

PID_FILE="/var/run/cognitive_monitor.pid"
SCRIPT="/root/.openclaw/workspace/cognitive_monitor.py"
LOG_FILE="/var/log/cognitive_monitor.log"

# 检查进程是否在运行
check_process() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
            return 0  # 进程在运行
        fi
    fi
    
    # 也检查是否有其他 cognitive_monitor 进程在运行
    if pgrep -f "cognitive_monitor.py" > /dev/null 2>&1; then
        # 进程在运行但没有 pid 文件，重新创建 pid 文件
        pgrep -f "cognitive_monitor.py" | head -1 > "$PID_FILE"
        return 0
    fi
    
    return 1  # 进程未运行
}

# 启动进程
start_process() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 认知监控进程未运行，正在启动..." >> "$LOG_FILE"
    nohup python3 -u "$SCRIPT" >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 进程已启动，PID: $NEW_PID" >> "$LOG_FILE"
}

# 主逻辑
if ! check_process; then
    start_process
fi
