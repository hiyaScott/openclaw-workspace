#!/usr/bin/env python3
"""
查询海螺AI视频生成结果
"""

import requests
import json
import time
import os

API_KEY = os.environ.get("DMXAPI_KEY", "sk-0SIXEK6miUYpDpZYGI3UEsSJMB2ZsY82J2TsGvfU44GSneTo")
TASK_ID = "381844753273267"
API_URL = f"https://www.dmxapi.cn/v1/video_generation?task_id={TASK_ID}"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

print(f"查询任务: {TASK_ID}")
print("-" * 60)

# 轮询查询
max_attempts = 30
for attempt in range(max_attempts):
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print(f"\n[{attempt+1}/{max_attempts}] {time.strftime('%H:%M:%S')}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查是否完成
        if "status" in data and data["status"] == "completed":
            print("\n" + "=" * 60)
            print("✅ 视频生成完成！")
            if "video_url" in data:
                print(f"视频URL: {data['video_url']}")
            break
        elif "status" in data and data["status"] == "failed":
            print("\n❌ 任务失败")
            break
        else:
            print(f"状态: {data.get('status', 'unknown')}, 等待10秒...")
            
    except Exception as e:
        print(f"错误: {e}")
    
    time.sleep(10)

print("\n查询结束")
