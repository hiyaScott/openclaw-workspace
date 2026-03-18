#!/bin/bash
# 恢复测试脚本 - 验证备份是否完整

echo "=== Jetton 恢复测试 ==="
echo ""

WORKSPACE="/root/.openclaw/workspace"
ERRORS=0

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $2"
        return 0
    else
        echo "❌ $2 - 缺失: $1"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        count=$(find "$1" -type f 2>/dev/null | wc -l)
        echo "✅ $2 ($count 个文件)"
        return 0
    else
        echo "❌ $2 - 缺失: $1"
        ((ERRORS++))
        return 1
    fi
}

echo "【P0 - 核心记忆】"
check_file "$WORKSPACE/MEMORY.md" "长期记忆"
check_file "$WORKSPACE/USER.md" "用户信息"
check_file "$WORKSPACE/SOUL.md" "灵魂定义"
check_file "$WORKSPACE/IDENTITY.md" "身份定义"
check_file "$WORKSPACE/AGENTS.md" "工作规则"

echo ""
echo "【P1 - 重要数据】"
check_dir "$WORKSPACE/memory" "每日记忆"
check_dir "$WORKSPACE/skills" "自定义技能"
check_file "$WORKSPACE/TOOLS.md" "工具配置"
check_file "$WORKSPACE/HEARTBEAT.md" "心跳任务"
check_file "$WORKSPACE/RESTORE.md" "恢复指南"

echo ""
echo "【Git 状态】"
cd "$WORKSPACE"
if [ -d ".git" ]; then
    echo "✅ Git 仓库已初始化"
    echo "   远程仓库: $(git remote get-url origin 2>/dev/null || echo '未设置')"
    echo "   当前分支: $(git branch --show-current 2>/dev/null || echo '未知')"
    echo "   未提交更改: $(git status --porcelain 2>/dev/null | wc -l) 个文件"
else
    echo "⚠️  不是 Git 仓库"
fi

echo ""
echo "【会话历史】"
SESSION_DIR="/root/.openclaw/agents/main/sessions"
if [ -d "$SESSION_DIR" ]; then
    count=$(find "$SESSION_DIR" -name "*.jsonl" 2>/dev/null | wc -l)
    size=$(du -sh "$SESSION_DIR" 2>/dev/null | cut -f1)
    echo "✅ 会话历史 ($count 个文件, $size)"
else
    echo "⚠️  会话目录不存在"
fi

echo ""
echo "=========================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ 所有核心文件存在，备份完整！"
else
    echo "❌ 发现 $ERRORS 个缺失的核心文件"
    exit 1
fi
