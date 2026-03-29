#!/bin/bash
# Git分批推送脚本 - 优化版
# 用于处理大量提交导致的HTTP 408超时问题

WORKSPACE="/root/.openclaw/workspace"
BATCH_SIZE=3

# 设置Git配置以处理大文件推送
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
git config --global http.version HTTP/1.1

cd "$WORKSPACE"

# 获取本地领先远程的提交列表
echo "获取待推送的提交列表..."
mapfile -t COMMITS < <(git log --oneline --reverse origin/master..HEAD | awk '{print $1}')
TOTAL=${#COMMITS[@]}

echo "共有 $TOTAL 个提交需要推送"

if [ $TOTAL -eq 0 ]; then
    echo "没有需要推送的提交"
    rm -f "$WORKSPACE/.git-push-retry-state"
    echo "SUCCESS" > "$WORKSPACE/.git-push-result"
    exit 0
fi

# 计算批次数量
BATCHES=$(( (TOTAL + BATCH_SIZE - 1) / BATCH_SIZE ))
echo "将分 $BATCHES 批推送，每批最多 $BATCH_SIZE 个提交"

# 分批推送
for ((i=0; i<BATCHES; i++)); do
    START=$((i * BATCH_SIZE))
    END=$((START + BATCH_SIZE - 1))
    if [ $END -ge $TOTAL ]; then
        END=$((TOTAL - 1))
    fi
    
    # 获取这一批的提交哈希
    if [ $START -eq $END ]; then
        COMMIT_SPEC="${COMMITS[$START]}"
    else
        COMMIT_SPEC="${COMMITS[$START]}..${COMMITS[$END]}"
    fi
    
    echo ""
    echo "=== 推送第 $((i+1))/$BATCHES 批: 提交 ${COMMITS[$START]} 到 ${COMMITS[$END]} ==="
    
    # 使用 git push 的 --thin 选项减少传输数据
    if timeout 180 git push origin "${COMMITS[$END]}:master" --force 2>&1; then
        echo "✅ 第 $((i+1)) 批推送成功"
    else
        echo "❌ 第 $((i+1)) 批推送失败"
        exit 1
    fi
done

echo ""
echo "=== 所有批次推送完成 ==="

# 清理状态文件
rm -f "$WORKSPACE/.git-push-retry-state"
echo "SUCCESS" > "$WORKSPACE/.git-push-result"

# 最后确保master是最新的
git fetch origin

echo "✅ 推送完成！"
exit 0
