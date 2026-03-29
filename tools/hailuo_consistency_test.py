#!/usr/bin/env python3
"""
海螺AI (MiniMax-Hailuo-02) 图生视频 - 角色一致性测试
========================================================
使用DMXAPI调用海螺视频生成，重点测试角色一致性保持

参考图: Robo No.5 角色图
目标: 10秒视频，保持角色外观一致
"""

import requests
import json
import time
import os

API_KEY = os.environ.get("DMXAPI_KEY", "sk-0SIXEK6miUYpDpZYGI3UEsSJMB2ZsY82J2TsGvfU44GSneTo")
API_URL = "https://www.dmxapi.cn/v1/video_generation"

# Robo No.5 角色参考图
CHARACTER_IMAGE = "https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_realistic_front.jpg"

# 10秒视频生成参数
payload = {
    "model": "MiniMax-Hailuo-02",
    "prompt": "A lonely old robot named 'Robo No.5' gently guarding a small potted flower. The robot has a boxy square metal head with orange glowing grid eyes, weathered teal-gray metal body with rust and scratches, hydraulic mechanical arms. Golden hour sunset lighting, warm orange glow. The robot slowly turns its head, eyes blinking softly with warm light. A gentle breeze blows, the flower sways slightly. Cinematic composition, post-apocalyptic wasteland background, 4K quality, film grain texture.",
    "image": CHARACTER_IMAGE,
    "duration": 10,  # 10秒
    "resolution": "1080P"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

print("=" * 60)
print("海螺AI (MiniMax-Hailuo-02) 图生视频 - 角色一致性测试")
print("=" * 60)
print(f"\n参考图: {CHARACTER_IMAGE}")
print(f"时长: 10秒")
print(f"分辨率: 1080P")
print(f"\n提示词:\n{payload['prompt']}\n")
print("-" * 60)

# 提交任务
try:
    print("提交任务...")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    print(f"响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
    
    # 提取task_id
    if "task_id" in data:
        task_id = data["task_id"]
        print(f"✅ 任务已提交 | Task ID: {task_id}")
        
        # 保存任务信息
        output_dir = "/root/.openclaw/workspace/hiyamax-blog-repo/assets/the_147th_day"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(f"{output_dir}/hailuo_task_{task_id}.json", "w") as f:
            json.dump({
                "task_id": task_id,
                "model": "MiniMax-Hailuo-02",
                "duration": 10,
                "character_image": CHARACTER_IMAGE,
                "prompt": payload["prompt"],
                "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_response": data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n任务信息已保存到: {output_dir}/hailuo_task_{task_id}.json")
        print(f"\n下一步: 等待生成完成，查询任务状态")
        print(f"Task ID: {task_id}")
        
    else:
        print("❌ 未找到 task_id")
        print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
