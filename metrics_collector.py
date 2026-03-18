#!/usr/bin/env python3
"""
Kimi Claw 客观状态监控 - 系统指标采集器
每 5 秒自动采集，无法伪造
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

def get_cpu_usage():
    """获取 CPU 使用率"""
    try:
        # 使用 top 获取 CPU
        result = subprocess.run(['top', '-bn1'], capture_output=True, text=True, timeout=2)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Cpu(s)' in line:
                # 解析: %Cpu(s):  5.6 us,  3.4 sy,  0.0 ni, 90.8 id
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

def get_active_sessions():
    """获取活跃会话数"""
    try:
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, text=True, timeout=2
        )
        # 统计 openclaw 相关进程
        lines = result.stdout.split('\n')
        count = 0
        for line in lines:
            if 'openclaw' in line.lower() and 'python' in line.lower():
                count += 1
        return max(count - 1, 0)  # 减去自己
    except:
        return 0

def get_running_subagents():
    """获取运行中的子代理数"""
    try:
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, text=True, timeout=2
        )
        lines = result.stdout.split('\n')
        count = 0
        for line in lines:
            if 'subagent' in line.lower() or 'spawn' in line.lower():
                count += 1
        return count
    except:
        return 0

def calculate_busyness(cpu, memory, sessions, subagents):
    """计算忙碌指数 0-100"""
    # 权重配置
    cpu_weight = 0.25
    memory_weight = 0.15
    sessions_weight = 0.30
    subagents_weight = 0.30
    
    # 会话数映射到 0-100 (每个会话20分，最多5个满负荷)
    sessions_score = min(sessions * 20, 100)
    
    # 子代理映射到 0-100 (每个25分，最多4个满负荷)
    subagents_score = min(subagents * 25, 100)
    
    # 加权计算
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
        return "high", "🔴 高负载"
    elif busyness_score >= 30:
        return "medium", "🟡 中等负载"
    else:
        return "low", "🟢 低负载"

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
        print(f"[ERROR] 更新失败: {e}")
        return False

def main():
    print("=" * 50)
    print("🖥️  Kimi Claw 客观状态监控启动")
    print("=" * 50)
    print(f"采集间隔: 60 秒 (免费版优化)")
    print(f"指标: CPU / 内存 / 会话数 / 子代理数")
    print(f"忙碌指数: 0-100 (自动计算)")
    print("=" * 50)
    
    while True:
        try:
            # 采集指标
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            sessions = get_active_sessions()
            subagents = get_running_subagents()
            
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
                print(f"[{time_str}] {status_text} | 负载:{busyness:5.1f}% | CPU:{cpu:5.1f}% | MEM:{memory:5.1f}% | 会话:{sessions} | 子代理:{subagents}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 更新失败")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
