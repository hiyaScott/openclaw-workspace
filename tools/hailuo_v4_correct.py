#!/usr/bin/env python3
"""
海螺AI (MiniMax-Hailuo-2.3) 图生视频 - 角色一致性测试
==========================================================
使用正确的API参数：first_frame_image
"""

import requests
import json
import time
import os

API_KEY = os.environ.get("DMXAPI_KEY", "sk-0SIXEK6miUYpDpZYGI3UEsSJMB2ZsY82J2TsGvfU44GSneTo")

# 使用新的模型和正确的参数
url = "https://www.dmxapi.cn/v1/video_generation"

headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# Robo No.5 角色参考图
character_image = "https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_realistic_front.jpg"

payload = {
    "model": "MiniMax-Hailuo-2.3",  # 使用标准版本，平衡质量与速度
    "prompt": "A lonely old robot named 'Robo No.5' gently guarding a small potted blue flower. The robot has a boxy square metal head with orange glowing grid eyes, weathered teal-gray metal body with rust and scratches. Golden hour sunset lighting. The robot slowly turns its head, eyes blinking softly with warm light. A gentle breeze blows. Cinematic composition, post-apocalyptic wasteland background, film grain texture. [推进]",
    "first_frame_image": character_image,  # ✅ 正确的参数名
    "duration": 10,  # 10秒
    "resolution": "768P"  # 768P支持10秒
}

print("=" * 60)
print("海螺AI (MiniMax-Hailuo-2.3) 图生视频 - 角色一致性测试")
print("=" * 60)
print(f"\n模型: MiniMax-Hailuo-2.3")
print(f"参考图: {character_image}")
print(f"时长: 10秒 | 分辨率: 768P")
print(f"\n提示词:\n{payload['prompt']}\n")
print("-" * 60)

# 提交任务
try:
    print("提交任务...")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    print(f"\n响应:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
    
    if "task_id" in data:
        task_id = data["task_id"]
        print(f"✅ 任务已提交 | Task ID: {task_id}")
        
        # 保存任务信息
        output_dir = "/root/.openclaw/workspace/hiyamax-blog-repo/assets/the_147th_day"
        os.makedirs(output_dir, exist_ok=True)
        
        task_info = {
            "task_id": task_id,
            "model": "MiniMax-Hailuo-2.3",
            "duration": 10,
            "resolution": "768P",
            "character_image": character_image,
            "prompt": payload["prompt"],
            "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_response": data
        }
        
        with open(f"{output_dir}/hailuo_v4_task_{task_id}.json", "w") as f:
            json.dump(task_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n任务信息已保存")
        print(f"\n下一步: 等待2-3分钟后查询任务状态")
        print(f"Task ID: {task_id}")
        
        # 询问是否立即查询
        print(f"\n查询命令:")
        print(f"curl -X GET 'https://www.dmxapi.cn/v1/query/video_generation?task_id={task_id}' \\")
        print(f"  -H 'Authorization: {API_KEY}'")
        
    else:
        print("❌ 未找到 task_id")
        
except Exception as e:
    print(f"❌ 错误: {e}")
