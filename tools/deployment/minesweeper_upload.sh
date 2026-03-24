#!/bin/bash
# 自动上传扫雷游戏到 GitHub，成功后自删除

REPO="hiyaScott/minesweeper-demo"
TOKEN="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"
LOG_FILE="/root/.openclaw/workspace/minesweeper_upload.log"
WORK_DIR="/root/.openclaw/workspace/minesweeper_export/web"

echo "[$(date)] 开始尝试上传..." >> $LOG_FILE

cd $WORK_DIR || exit 1

# 配置 git
git config http.version HTTP/1.1
git config http.postBuffer 524288000
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999

# 尝试推送
if git push -u origin main --force 2>&1 >> $LOG_FILE; then
    echo "[$(date)] ✅ 上传成功！" >> $LOG_FILE
    
    # 删除 cron 任务
    crontab -l | grep -v "minesweeper_upload" | crontab -
    echo "[$(date)] 已删除自动重试任务" >> $LOG_FILE
    
    # 发送成功通知（通过 OpenClaw 网关）
    curl -s -X POST http://localhost:8080/internal/notify \
        -d "扫雷游戏已成功部署到 GitHub Pages！"
else
    echo "[$(date)] ❌ 上传失败，等待下次重试..." >> $LOG_FILE
    exit 1
fi
