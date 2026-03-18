#!/usr/bin/env python3
"""
Kimi Claw 客观状态监控 v4.0 - 基于 OpenClaw 真实状态
从 sessions_list 获取准确数据
"""

import json
import time
import os
import subprocess
from datetime import datetime
from urllib import request

# Upstash 配置
UPSTASH_REDIS_REST_URL = "https://singular-snake-71209.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk"

def get_openclaw_sessions():
    """获取真实的 OpenClaw 活跃会话数"""
    try:
        # 检查进程中的会话文件
        result = subprocess.run(
            ['ls', '-la', '/root/.openclaw/workspace/'],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.split('\n')
        
        # 统计 .jsonl 会话文件
        session_count = 0
        subagent_count = 0
        
        for line in lines:
            if '.jsonl' in line:
                session_count += 1
            if 'subagent' in line.lower():
                subagent_count += 1
        
        return session_count, subagent_count
    except:
        return 0, 0

def get_cpu_usage():
    """获取 CPU 使用率"""
    try:
        result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=2)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Cpu(s)' in line:
                parts = line.split(',')
                idle_part = [p for p in parts if 'id' in p]
                if idle_part:
                    idle = float(idle_part[0].strip().split()[0])
                    return round(100 - idle, 1)
    except:
        pass
    return 0.0

def get_memory_usage():
    """获取内存使用率"""
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        total = 0
        available = 0
        for line in lines:
            if 'MemTotal:' in line:
                total = int(line.split()[1])
            elif 'MemAvailable:' in line:
                available = int(line.split()[1])
        if total > 0:
            used = total - available
            return round((used / total) * 100, 1)
    except:
        pass
    return 0.0

def calculate_busyness(cpu, memory, sessions, subagents):
    """计算忙碌指数 - 会话权重提高"""
    # 调整权重：会话更重要
    cpu_weight = 0.20
    memory_weight = 0.15
    sessions_weight = 0.45  # 提高会话权重
    subagents_weight = 0.20
    
    # 每个会话 25 分（4个会话就满负荷）
    sessions_score = min(sessions * 25, 100)
    
    # 每个子代理 25 分
    subagents_score = min(subagents * 25, 100)
    
    score = (
        cpu * cpu_weight +
        memory * memory_weight +
        sessions_score * sessions_weight +
        subagents_score * subagents_weight
    )
    
    return round(score, 1)

def determine_status(busyness_score):
    """根据忙碌指数确定状态"""
    if busyness_score >= 70:
        return "high", "🔴 高负载 - 建议等待"
    elif busyness_score >= 30:
        return "medium", "🟡 中等负载 - 谨慎派活"
    else:
        return "low", "🟢 低负载 - 可派活"

def update_redis(metrics):
    """更新 Redis"""
    try:
        url = f"{UPSTASH_REDIS_REST_URL}/set/metrics.json"
        req = request.Request(
            url,
            data=json.dumps({"value": json.dumps(metrics)}).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Status Error] 更新失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🖥️  Shrimp Jetton 客观状态监控 v4.0")
    print("=" * 60)
    print(f"采集间隔: 60 秒")
    print(f"指标: CPU / 内存 / 活跃会话 / 子代理")
    print(f"会话权重: 45% (核心指标)")
    print("=" * 60)
    
    while True:
        try:
            # 采集指标
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            sessions, subagents = get_openclaw_sessions()
            
            # 计算忙碌指数
            busyness = calculate_busyness(cpu, memory, sessions, subagents)
            status_code, status_text = determine_status(busyness)
            
            # 构建数据
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu,
                "memory_percent": memory,
                "active_sessions": sessions,
                "running_subagents": subagents,
                "busyness_score": busyness,
                "status_code": status_code,
                "status_text": status_text
            }
            
            # 更新 Redis
            if update_redis(metrics):
                time_str = datetime.now().strftime("%H:%M:%S")
                print(f"[{time_str}] {status_text} | 负载:{busyness:5.1f}% | 会话:{sessions} | 子代理:{subagents}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 更新失败")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
