#!/bin/bash
# Jetton 自动备份脚本 v1.0
# 用法: ./backup.sh 或添加到 crontab: 0 3 * * * /root/.openclaw/workspace/backup.sh

set -e

WORKSPACE="/root/.openclaw/workspace"
BACKUP_LOG="$WORKSPACE/backup.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始备份..." | tee -a "$BACKUP_LOG"

cd "$WORKSPACE"

# 检查git状态
if [ ! -d ".git" ]; then
    echo "[$DATE] 错误: 不是git仓库" | tee -a "$BACKUP_LOG"
    exit 1
fi

# 添加所有更改
git add -A

# 检查是否有更改
if git diff --cached --quiet; then
    echo "[$DATE] 没有更改，跳过备份" | tee -a "$BACKUP_LOG"
    exit 0
fi

# 提交
git commit -m "backup: $DATE" || true

# 推送到主仓库
if git push origin master 2>> "$BACKUP_LOG"; then
    echo "[$DATE] ✅ 备份成功" | tee -a "$BACKUP_LOG"
else
    echo "[$DATE] ⚠️ 推送失败，已本地提交" | tee -a "$BACKUP_LOG"
fi

# 可选：创建本地快照（保留最近5个）
# SNAPSHOT_DIR="$HOME/jetton-snapshots"
# mkdir -p "$SNAPSHOT_DIR"
# tar czf "$SNAPSHOT_DIR/jetton-${DATE// /_}.tar.gz" \
#     "$WORKSPACE/MEMORY.md" \
#     "$WORKSPACE/USER.md" \
#     "$WORKSPACE/SOUL.md" \
#     "$WORKSPACE/IDENTITY.md" \
#     "$WORKSPACE/memory/" \
#     "$WORKSPACE/skills/"
# 
# # 只保留最近5个快照
# ls -t "$SNAPSHOT_DIR"/jetton-*.tar.gz | tail -n +6 | xargs rm -f 2>/dev/null || true

echo "[$DATE] 备份完成" | tee -a "$BACKUP_LOG"
