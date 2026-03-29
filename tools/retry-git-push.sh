#!/bin/bash
# Git推送重试脚本 - 增强版

WORKSPACE="/root/.openclaw/workspace"
STATE_FILE="$WORKSPACE/.git-push-retry-state"
MAX_RETRIES=8

# 设置Git配置以处理大文件推送
export GIT_HTTP_MAX_REQUEST_BUFFER=524288000
export GIT_HTTP_LOW_SPEED_LIMIT=0
export GIT_HTTP_LOW_SPEED_TIME=999999

# 设置Git缓冲区大小
export GIT_BUFFER_SIZE=100000000

# 读取当前状态
if [ -f "$STATE_FILE" ]; then
    RETRY_COUNT=$(cat "$STATE_FILE")
else
    RETRY_COUNT=0
fi

# 检查是否已达到最大重试次数
if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
    echo "[$DATE] 已达到最大重试次数($MAX_RETRIES)，停止重试" >> "$WORKSPACE/push-retry.log"
    echo "FAILED" > "$WORKSPACE/.git-push-result"
    exit 1
fi

# 增加计数
RETRY_COUNT=$((RETRY_COUNT + 1))
echo "$RETRY_COUNT" > "$STATE_FILE"

DATE=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$DATE] 第 $RETRY_COUNT 次尝试推送..." >> "$WORKSPACE/push-retry.log"

# 进入工作目录
cd "$WORKSPACE"

# 配置Git以支持大文件推送
git config http.postBuffer 524288000
git config http.version HTTP/1.1
git config http.maxRequestBuffer 524288000

# 获取当前commit数量，估算包大小
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
echo "[$DATE] 当前仓库共 $COMMIT_COUNT 个commit" >> "$WORKSPACE/push-retry.log"

# 检查是否有大文件
echo "[$DATE] 检查待推送文件大小..." >> "$WORKSPACE/push-retry.log"
git status --short | while read line; do
    file=$(echo "$line" | sed 's/^[^ ]* //')
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 10485760 ]; then  # 大于10MB
            size_mb=$(echo "scale=2; $size / 1048576" | bc 2>/dev/null || echo "$((size / 1048576))")
            echo "[$DATE] 警告: 大文件 $file (${size_mb}MB)" >> "$WORKSPACE/push-retry.log"
        fi
    fi
done

# 尝试推送 - 使用分块推送策略
echo "[$DATE] 开始推送..." >> "$WORKSPACE/push-retry.log"

# 先尝试普通推送
if timeout 300 git push origin master 2>> "$WORKSPACE/push-retry.log"; then
    echo "[$DATE] ✅ 推送成功！" >> "$WORKSPACE/push-retry.log"
    echo "SUCCESS" > "$WORKSPACE/.git-push-result"
    # 清理状态文件
    rm -f "$STATE_FILE"
    exit 0
else
    PUSH_EXIT=$?
    echo "[$DATE] 普通推送失败(退出码: $PUSH_EXIT)，尝试强制推送..." >> "$WORKSPACE/push-retry.log"
    
    # 如果普通推送失败，尝试强制推送
    if timeout 300 git push origin master --force 2>> "$WORKSPACE/push-retry.log"; then
        echo "[$DATE] ✅ 强制推送成功！" >> "$WORKSPACE/push-retry.log"
        echo "SUCCESS" > "$WORKSPACE/.git-push-result"
        rm -f "$STATE_FILE"
        exit 0
    else
        FORCE_EXIT=$?
        echo "[$DATE] ❌ 强制推送也失败(退出码: $FORCE_EXIT)，等待下次重试..." >> "$WORKSPACE/push-retry.log"
        
        # 如果这是第6次或更多，尝试分块推送
        if [ "$RETRY_COUNT" -ge 6 ]; then
            echo "[$DATE] 尝试分块推送策略..." >> "$WORKSPACE/push-retry.log"
            
            # 获取远程分支的最新commit
            REMOTE_COMMIT=$(git rev-parse origin/master 2>/dev/null || echo "")
            LOCAL_COMMIT=$(git rev-parse HEAD)
            
            if [ -n "$REMOTE_COMMIT" ] && [ "$REMOTE_COMMIT" != "$LOCAL_COMMIT" ]; then
                # 计算需要推送的commit数量
                COMMITS_TO_PUSH=$(git rev-list --count "$REMOTE_COMMIT..$LOCAL_COMMIT" 2>/dev/null || echo "0")
                echo "[$DATE] 需要推送 $COMMITS_TO_PUSH 个commit" >> "$WORKSPACE/push-retry.log"
                
                if [ "$COMMITS_TO_PUSH" -gt 1 ]; then
                    # 尝试只推送最近的1个commit
                    echo "[$DATE] 尝试只推送最近1个commit..." >> "$WORKSPACE/push-retry.log"
                    PARENT_COMMIT=$(git rev-parse HEAD~1)
                    if timeout 300 git push origin "$PARENT_COMMIT":master 2>> "$WORKSPACE/push-retry.log"; then
                        echo "[$DATE] ✅ 分块推送第一步成功，下次将继续推送剩余commit" >> "$WORKSPACE/push-retry.log"
                        # 不清理状态文件，下次继续
                        exit 1
                    fi
                fi
            fi
        fi
        
        exit 1
    fi
fi
