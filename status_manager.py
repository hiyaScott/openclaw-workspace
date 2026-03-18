#!/usr/bin/env python3
"""
Kimi Claw 状态管理模块
用于在各种场景下更新状态到 Redis
"""

import json
import os
from datetime import datetime
from urllib import request

# Upstash 配置
UPSTASH_REDIS_REST_URL = "https://singular-snake-71209.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk"

class StatusManager:
    """状态管理器 - 统一控制状态更新"""
    
    def __init__(self):
        self.url = UPSTASH_REDIS_REST_URL
        self.token = UPSTASH_REDIS_REST_TOKEN
    
    def _update_redis(self, status_data):
        """更新 Redis 状态"""
        try:
            url = f"{self.url}/set/status.json"
            req = request.Request(
                url,
                data=json.dumps({"value": json.dumps(status_data)}).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[Status Error] 更新失败: {e}")
            return False
    
    def set_busy(self, task_description):
        """设置为忙碌状态"""
        status = {
            "status": "busy",
            "status_text": "处理中",
            "current_task": task_description,
            "since": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "session_uptime": "active",
            "channel": "feishu",
            "model": "kimi-coding/k2p5"
        }
        if self._update_redis(status):
            print(f"🟡 状态: 处理中 - {task_description}")
            return True
        return False
    
    def set_ready(self):
        """设置为就绪状态"""
        status = {
            "status": "ready",
            "status_text": "就绪",
            "current_task": "等待指令",
            "since": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "session_uptime": "active",
            "channel": "feishu",
            "model": "kimi-coding/k2p5"
        }
        if self._update_redis(status):
            print("🟢 状态: 就绪 - 等待指令")
            return True
        return False

# 全局实例
status = StatusManager()

if __name__ == "__main__":
    # 测试
    status.set_busy("测试子代理任务")
    input("按回车设置为就绪...")
    status.set_ready()
