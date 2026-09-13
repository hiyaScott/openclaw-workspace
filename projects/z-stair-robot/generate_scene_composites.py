#!/usr/bin/env python3
"""
Z-Stair-Robot 场景合成图生成脚本
基于真实楼梯照片，用即梦AI生成机器人在楼梯上的概念渲染图
"""

import os
import sys
import json
import base64
import hashlib
import hmac
import datetime
import time
import requests
from PIL import Image
from io import BytesIO

# 加载API密钥
sys.path.insert(0, '/root/.openclaw/workspace/skills/ai-shortfilm-pipeline/scripts')
from api_config import get_jimeng_keys

ak, sk = get_jimeng_keys()

# 路径配置
STAIRS_PHOTO = "/root/.openclaw/media/inbound/c4f0050d-dcee-41ef-b52c-233f03d135c7.jpg"
OUTPUT_DIR = "/root/.openclaw/workspace/projects/z-stair-robot/scene-composites"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def resize_and_encode_image(image_path, max_size=1536):
    """压缩图片并转为base64"""
    img = Image.open(image_path)
    # 保持比例，最长边不超过max_size
    ratio = max_size / max(img.width, img.height)
    if ratio < 1:
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # 转为JPEG
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

def sign(ak, sk, action, version, body):
    """火山引擎HMAC-SHA256签名"""
    now = datetime.datetime.utcnow()
    x_date = now.strftime('%Y%m%dT%H%M%SZ')
    short_x_date = x_date[:8]
    host = "visual.volcengineapi.com"
    query = f"Action={action}&Version={version}"
    body_bytes = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    sha256 = hashlib.sha256(body_bytes).hexdigest()
    signed_headers = "content-type;host;x-content-sha256;x-date"
    canonical = f"POST\n/\n{query}\ncontent-type:application/json\nhost:{host}\nx-content-sha256:{sha256}\nx-date:{x_date}\n\n{signed_headers}\n{sha256}"
    k_date = hmac.new(sk.encode(), short_x_date.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, b"cn-north-1", hashlib.sha256).digest()
    k_service = hmac.new(k_region, b"cv", hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    scope = f"{short_x_date}/cn-north-1/cv/request"
    string_to_sign = f"HMAC-SHA256\n{x_date}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    auth = f"HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
    return f"https://{host}/?{query}", {
        "Host": host,
        "X-Date": x_date,
        "X-Content-Sha256": sha256,
        "Content-Type": "application/json",
        "Authorization": auth
    }, body_bytes

def submit_image_task(prompt, image_base64=None, width=1024, height=1024):
    """提交图生图任务"""
    body = {
        "req_key": "jimeng_high_aes_general_v21_L",
        "prompt": prompt,
        "width": width,
        "height": height,
        "return_url": True,
    }
    if image_base64:
        body["image_url"] = f"data:image/jpeg;base64,{image_base64}"
    
    url, headers, body_bytes = sign(ak, sk, "CVSync2AsyncSubmitTask", "2022-08-31", body)
    resp = requests.post(url, headers=headers, data=body_bytes, timeout=30)
    result = resp.json()
    
    if result.get('code') != 10000:
        print(f"提交失败: {result}")
        return None
    return result['data']['task_id']

def get_result(task_id):
    """查询任务结果"""
    body = {
        "req_key": "jimeng_high_aes_general_v21_L",
        "task_id": task_id,
        "req_json": json.dumps({"return_url": True})
    }
    url, headers, body_bytes = sign(ak, sk, "CVSync2AsyncGetResult", "2022-08-31", body)
    resp = requests.post(url, headers=headers, data=body_bytes, timeout=30)
    return resp.json()

def wait_and_download(task_id, output_path, max_wait=120):
    """等待任务完成并下载图片"""
    print(f"  任务ID: {task_id}")
    for i in range(max_wait // 3):
        time.sleep(3)
        result = get_result(task_id)
        status = result.get('data', {}).get('status', 'UNKNOWN')
        print(f"  状态: {status} ({i*3}s)")
        
        if status == 'SUCCEEDED':
            image_urls = result['data'].get('image_urls', [])
            if image_urls:
                img_url = image_urls[0]
                img_resp = requests.get(img_url, timeout=30)
                with open(output_path, 'wb') as f:
                    f.write(img_resp.content)
                print(f"  ✅ 已保存: {output_path}")
                return True
        elif status == 'FAILED':
            print(f"  ❌ 任务失败: {result}")
            return False
    
    print(f"  ⏱️ 超时")
    return False

# ========== 主流程 ==========

print("=" * 50)
print("Z-Stair-Robot 场景合成图生成")
print("=" * 50)

# 1. 编码楼梯照片
print("\n[1/4] 编码楼梯照片...")
stairs_base64 = resize_and_encode_image(STAIRS_PHOTO, max_size=1024)
print(f"  照片已编码 ({len(stairs_base64)//1024}KB)")

# 2. 定义要生成的场景
scenes = [
    {
        "name": "stair-climbing",
        "desc": "楼梯攀爬姿态",
        "prompt": "一台极简工业设计风格的扫楼梯机器人，前后两块扁平的深灰色金属矩形脚垫，中间两根红色电动推杆连杆，呈Z字形攀爬在现代黑白大理石楼梯上。后脚垫水平稳定在下层台阶，前脚垫被送到上层台阶，两根连杆竖直连接两块脚垫。脚垫底部有黑色硅胶防滑垫。科技感产品渲染图，柔和的顶光照明，高质量，8K细节，工业设计摄影风格。",
        "w": 1024, "h": 1024
    },
    {
        "name": "floor-mode",
        "desc": "平地模式",
        "prompt": "一台极简工业设计风格的扫楼梯机器人，前后两块扁平的深灰色金属矩形脚垫水平拼接成一体，中间两根红色电动推杆收缩到最短，连杆与脚垫呈0度水平，整体形成一块长条形的清洁底盘。机器人位于楼梯平台的大理石地面上。科技感产品渲染图，柔和的顶光照明，高质量，8K细节，工业设计摄影风格。",
        "w": 1024, "h": 1024
    },
    {
        "name": "wide-scene",
        "desc": "整体场景",
        "prompt": "一台极简工业设计风格的扫楼梯机器人，前后两块扁平的深灰色金属矩形脚垫，中间两根红色电动推杆连杆，呈Z字形在现代黑白大理石楼梯上攀爬。从稍远的角度拍摄，展示机器人在整段楼梯上的比例感。楼梯有黑色铁艺扶手，白色大理石台阶。科技感产品渲染图，自然光照明，高质量，工业设计摄影风格。",
        "w": 1024, "h": 1024
    }
]

# 3. 生成图片
print(f"\n[2/4] 提交生成任务 ({len(scenes)} 个场景)...")
tasks = []
for scene in scenes:
    print(f"\n  📷 {scene['desc']} ({scene['name']})")
    task_id = submit_image_task(
        prompt=scene['prompt'],
        image_base64=stairs_base64,
        width=scene['w'],
        height=scene['h']
    )
    if task_id:
        output_path = os.path.join(OUTPUT_DIR, f"{scene['name']}.png")
        tasks.append({
            'task_id': task_id,
            'output_path': output_path,
            'desc': scene['desc'],
            'name': scene['name']
        })
    else:
        print(f"  ❌ 提交失败")

# 4. 等待并下载
print(f"\n[3/4] 等待任务完成并下载...")
success_count = 0
for task in tasks:
    print(f"\n  📥 {task['desc']}")
    if wait_and_download(task['task_id'], task['output_path']):
        success_count += 1

print(f"\n[4/4] 完成: {success_count}/{len(tasks)} 张图片生成成功")
print(f"\n输出目录: {OUTPUT_DIR}")

# 列出结果
for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(fpath)
    print(f"  - {f} ({size//1024}KB)")
