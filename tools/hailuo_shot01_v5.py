#!/usr/bin/env python3
"""
海螺AI 图生视频 - 镜头01重制版（仅首帧）
============================================
使用MiniMax-Hailuo-2.3模型，first_frame_image参数
首帧: robo_no5_character.jpg (手绘风格)
"""

import requests
import json
import time
import os

API_KEY = os.environ.get("DMXAPI_KEY", "sk-0SIXEK6miUYpDpZYGI3UEsSJMB2ZsY82J2TsGvfU44GSneTo")

url = "https://www.dmxapi.cn/v1/video_generation"

headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# 首帧图片 - 手绘风格角色图
first_frame = "https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_character.jpg"

# 镜头01的提示词
payload = {
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "A lonely old robot named 'Robo No.5' gently guarding a small potted blue flower. The robot has a boxy square metal head with orange glowing grid eyes, weathered teal-gray metal body with rust and scratches. Golden hour sunset lighting. The robot slowly turns its head, eyes blinking softly with warm light. A gentle breeze blows. Cinematic composition, post-apocalyptic wasteland background, film grain texture. [推进]",
    "first_frame_image": first_frame,
    "duration": 10,
    "resolution": "768P"
}

print("=" * 60)
print("海螺AI 图生视频 - 镜头01重制版（仅首帧）")
print("=" * 60)
print(f"\n模型: MiniMax-Hailuo-2.3")
print(f"首帧: robo_no5_character.jpg (手绘风格)")
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
            "mode": "first_frame_only",
            "duration": 10,
            "resolution": "768P",
            "first_frame": first_frame,
            "prompt": payload["prompt"],
            "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "note": "镜头01重制版：仅首帧，手绘风格角色图",
            "api_response": data
        }
        
        with open(f"{output_dir}/hailuo_shot01_v5_task_{task_id}.json", "w") as f:
            json.dump(task_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n任务信息已保存")
        print(f"\n等待生成完成...")
        
        # 轮询查询
        print(f"\n开始轮询查询 (最多30次)...")
        for i in range(30):
            time.sleep(15)
            try:
                query_url = f"https://www.dmxapi.cn/v1/query/video_generation?task_id={task_id}"
                query_response = requests.get(query_url, headers=headers, timeout=30)
                query_data = query_response.json()
                
                status = query_data.get("status")
                print(f"[{i+1}/30] {time.strftime('%H:%M:%S')} - 状态: {status}")
                
                if status == "Success":
                    file_id = query_data.get("file_id")
                    print(f"\n✅ 视频生成完成!")
                    print(f"File ID: {file_id}")
                    
                    # 获取下载链接
                    download_url = f"https://www.dmxapi.cn/v1/files/retrieve?file_id={file_id}&task_id={task_id}"
                    download_response = requests.get(download_url, headers=headers, timeout=30)
                    download_data = download_response.json()
                    
                    if "file" in download_data and "download_url" in download_data["file"]:
                        video_url = download_data["file"]["download_url"]
                        print(f"视频URL: {video_url}")
                        
                        # 下载视频
                        video_path = f"{output_dir}/hailuo_shot01_v5_10s.mp4"
                        print(f"\n下载视频...")
                        video_response = requests.get(video_url, timeout=120)
                        with open(video_path, "wb") as f:
                            f.write(video_response.content)
                        
                        file_size = os.path.getsize(video_path) / (1024 * 1024)
                        print(f"✅ 视频已保存: {video_path} ({file_size:.1f}MB)")
                        
                        # 更新任务信息
                        task_info["status"] = "completed"
                        task_info["file_id"] = file_id
                        task_info["video_url"] = video_url
                        task_info["local_path"] = video_path
                        task_info["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        with open(f"{output_dir}/hailuo_shot01_v5_task_{task_id}.json", "w") as f:
                            json.dump(task_info, f, indent=2, ensure_ascii=False)
                        
                        print(f"\n{'='*60}")
                        print(f"任务完成! Task ID: {task_id}")
                        print(f"视频文件: hailuo_shot01_v5_10s.mp4")
                        print(f"{'='*60}")
                        
                        break
                    
                elif status == "Failed":
                    print(f"\n❌ 任务失败")
                    break
                    
            except Exception as e:
                print(f"查询错误: {e}")
                continue
        else:
            print(f"\n⏰ 达到最大查询次数，请稍后手动查询")
            print(f"Task ID: {task_id}")
        
    else:
        print("❌ 未找到 task_id")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
