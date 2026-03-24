#!/bin/bash
# Cognitive Monitor 系统健康检查脚本
# 用法: ./health-check.sh

echo "=== Cognitive Monitor 系统健康检查 ==="
echo "检查时间: $(date)"
echo ""

ERRORS=0
WARNINGS=0

# 1. 检查符号链接
echo "[1/8] 检查符号链接..."
SYMLINKS=$(find /root/.openclaw/workspace/portfolio-blog -type l ! -path './.git/*' 2>/dev/null)
if [ -n "$SYMLINKS" ]; then
    echo "  ⚠️  警告: 发现符号链接"
    echo "$SYMLINKS" | sed 's/^/    /'
    ((WARNINGS++))
else
    echo "  ✅ 无符号链接"
fi

# 2. 检查大文件
echo "[2/8] 检查大文件(>5MB)..."
LARGE_FILES=$(find /root/.openclaw/workspace/portfolio-blog -type f -size +5M ! -path './.git/*' 2>/dev/null)
if [ -n "$LARGE_FILES" ]; then
    echo "  ⚠️  警告: 发现大文件"
    echo "$LARGE_FILES" | sed 's/^/    /'
    ((WARNINGS++))
else
    echo "  ✅ 无大文件"
fi

# 3. 检查空文件
echo "[3/8] 检查空文件..."
EMPTY_FILES=$(find /root/.openclaw/workspace/portfolio-blog -type f -size 0 ! -path './.git/*' 2>/dev/null)
if [ -n "$EMPTY_FILES" ]; then
    echo "  ⚠️  警告: 发现空文件"
    echo "$EMPTY_FILES" | sed 's/^/    /'
    ((WARNINGS++))
else
    echo "  ✅ 无空文件"
fi

# 4. 检查中文文件名
echo "[4/8] 检查非ASCII文件名..."
NON_ASCII=$(find /root/.openclaw/workspace/portfolio-blog -type f ! -path './.git/*' -print0 2>/dev/null | \
    xargs -0 -I {} sh -c 'echo "{}" | grep -P "[^\x00-\x7F]" || true')
if [ -n "$NON_ASCII" ]; then
    echo "  ⚠️  警告: 发现非ASCII文件名"
    echo "$NON_ASCII" | sed 's/^/    /'
    ((WARNINGS++))
else
    echo "  ✅ 无非ASCII文件名"
fi

# 5. 检查定时任务
echo "[5/8] 检查定时任务..."
if crontab -l 2>/dev/null | grep -q "cognitive"; then
    echo "  ✅ 定时任务已启用"
    echo "  配置:"
    crontab -l | grep "cognitive" | sed 's/^/    /'
else
    echo "  ⚠️  警告: 定时任务未启用"
    ((WARNINGS++))
fi

# 6. 检查熔断器状态
echo "[6/8] 检查熔断器状态..."
if [ -f /tmp/cognitive_circuit_breaker ]; then
    breaker_time=$(cat /tmp/cognitive_circuit_breaker)
    now=$(date +%s)
    elapsed=$((now - breaker_time))
    remaining=$((1800 - elapsed))
    if [ "$remaining" -gt 0 ]; then
        echo "  🔴 熔断器开启中，剩余 $((remaining/60)) 分钟"
        ((WARNINGS++))
    else
        echo "  ✅ 熔断器已过期"
    fi
else
    echo "  ✅ 熔断器关闭"
fi

# 7. 检查最近推送
echo "[7/8] 检查最近推送状态..."
if [ -f /var/log/cognitive_push.log ]; then
    LAST_LOG=$(tail -3 /var/log/cognitive_push.log)
    if echo "$LAST_LOG" | grep -q "✅ 推送成功"; then
        echo "  ✅ 最近推送成功"
    elif echo "$LAST_LOG" | grep -q "❌ 推送失败"; then
        echo "  🔴 最近推送失败"
        ((ERRORS++))
    else
        echo "  ⚠️  无法确定推送状态"
    fi
else
    echo "  ⚠️  无推送日志"
fi

# 8. 检查GitHub Pages状态
echo "[8/8] 检查GitHub Pages远程数据..."
REMOTE_DATA=$(curl -s "https://hiyascott.github.io/scott-portfolio/status-monitor/cognitive-data.json?t=$(date +%s)" 2>/dev/null)
if [ -n "$REMOTE_DATA" ]; then
    REMOTE_TIME=$(echo "$REMOTE_DATA" | jq -r '.timestamp' 2>/dev/null)
    echo "  ✅ 远程数据可访问"
    echo "  最新数据时间: $REMOTE_TIME"
else
    echo "  🔴 无法获取远程数据"
    ((ERRORS++))
fi

echo ""
echo "=== 检查结果 ==="
echo "错误: $ERRORS"
echo "警告: $WARNINGS"

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo "✅ 系统健康"
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo "⚠️  系统有警告，建议关注"
    exit 1
else
    echo "🔴 系统有错误，需要处理"
    exit 2
fi
