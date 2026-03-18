#!/bin/bash
cd /root/openclaw/skills

# 下载 Agent Reach
echo "[1/2] 下载 Agent Reach..."
if git clone --depth 1 https://github.com/suhanoves/agent_reach.git 2>/dev/null; then
    echo "✅ Agent Reach 下载成功"
else
    echo "❌ Agent Reach 下载失败"
fi

# 下载 Skill Vetter  
echo "[2/2] 下载 Skill Vetter..."
if git clone --depth 1 https://github.com/openclaw/skill_vetter.git 2>/dev/null; then
    echo "✅ Skill Vetter 下载成功"
else
    echo "❌ Skill Vetter 下载失败"
fi

echo "完成"
