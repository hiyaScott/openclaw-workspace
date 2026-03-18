#!/usr/bin/env python3
"""
实时状态同步脚本 - 写入 Upstash Redis
每 5 秒更新一次状态
"""

import json
import time
import os
from datetime import datetime
from urllib import request, parse

# Upstash 配置
UPSTASH_REDIS_REST_URL = "https://singular-snake-71209.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk"

# 状态文件路径
STATUS_FILE = "/root/.openclaw/workspace/status.json"

def get_status():
    """读取本地状态文件"""
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "status": "unknown",
            "status_text": "未知",
            "since": datetime.now().isoformat(),
            "current_task": None,
            "last_heartbeat": datetime.now().isoformat(),
            "session_uptime": "active",
            "channel": "feishu",
            "model": "kimi-coding/k2p5"
        }

def update_redis(status_data):
    """写入 Upstash Redis"""
    try:
        url = f"{UPSTASH_REDIS_REST_URL}/set/status.json"
        
        # 将状态转为 JSON 字符串
        status_json = json.dumps(status_data)
        
        req = request.Request(
            url,
            data=json.dumps({"value": status_json}).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        with request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[ERROR] 更新 Redis 失败: {e}")
        return False

def main():
    print("[INFO] 状态同步服务启动...")
    print(f"[INFO] 状态文件: {STATUS_FILE}")
    print(f"[INFO] 目标: {UPSTASH_REDIS_REST_URL}")
    print("[INFO] 按 Ctrl+C 停止\n")
    
    while True:
        status = get_status()
        status["last_updated"] = datetime.now().isoformat()
        
        if update_redis(status):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 已同步 - {status.get('status_text', 'unknown')}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 同步失败")
        
        time.sleep(5)  # 每 5 秒更新

if __name__ == "__main__":
    # 检查配置
    if "your-db" in UPSTASH_REDIS_REST_URL or "your-token" in UPSTASH_REDIS_REST_TOKEN:
        print("[ERROR] 请先编辑脚本，填入你的 Upstash API 信息!")
        print("获取方式: https://console.upstash.com/redis")
        exit(1)
    
    main()
