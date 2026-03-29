#!/usr/bin/env python3
"""
Kling v2.6 图生视频 - 完整异步调用脚本
测试目的：验证正确的异步提交流程
作者：Jetton
日期：2026-03-29
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# ============ 配置 ============
API_KEY = os.getenv("DMXAPI_KEY", "your-api-key-here")
BASE_URL = "https://www.dmxapi.cn/v1"
IMAGE_URL = "https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_character.jpg"
PROMPT = "夕阳下的金色光芒中，机器人温柔地守护着一朵发光的蓝色小花，微风轻拂，机器人头部微微转动，眼中闪烁着温暖的光芒，电影级光影，4K画质，柔和焦点"
DURATION = 5  # 秒 (可灵只支持 5 或 10)
OUTPUT_DIR = "/root/.openclaw/workspace/hiyamax-blog-repo/assets/kling_test"

# 轮询配置
POLL_INTERVAL = 30  # 秒
MAX_POLL_ATTEMPTS = 20  # 最多10分钟

# ============ 日志 ============
def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def save_log(content, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    log(f"日志已保存: {filepath}")

# ============ 1. 余额检查 ============
def check_balance():
    """检查账户余额是否充足"""
    log("=" * 50)
    log("步骤 1/4: 检查账户余额")
    log("=" * 50)
    
    # 余额检查端点暂时不可用，跳过直接执行
    log("余额检查端点暂时不可用，跳过此步骤")
    log("继续执行任务提交...")
    return True

# ============ 2. 提交任务 ============
def submit_task():
    """提交视频生成任务"""
    log("=" * 50)
    log("步骤 2/4: 提交视频生成任务")
    log("=" * 50)
    
    payload = {
        "model": "kling-v2-6-image2video",
        "input": PROMPT,
        "image": IMAGE_URL,
        "mode": "pro",
        "duration": DURATION,
        "aspect_ratio": "16:9"
    }
    
    log(f"请求参数:")
    log(f"  模型: {payload['model']}")
    log(f"  时长: {payload['duration']}秒")
    log(f"  模式: {payload['mode']}")
    log(f"  提示词: {payload['input'][:50]}...")
    log(f"  图片: {payload['image']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/responses",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        # 保存完整响应
        save_log(json.dumps(data, indent=2, ensure_ascii=False), "submit_response.json")
        
        # 提取 task_id
        task_id = None
        if "data" in data and isinstance(data["data"], dict):
            task_id = data["data"].get("task_id")
        elif "id" in data:
            task_id = data["id"]
        elif "task_id" in data:
            task_id = data["task_id"]
        
        if not task_id:
            log(f"未能提取 task_id，完整响应: {json.dumps(data, indent=2)}", "ERROR")
            return None
        
        log(f"任务提交成功! Task ID: {task_id}")
        return task_id
        
    except requests.exceptions.RequestException as e:
        log(f"任务提交失败: {e}", "ERROR")
        if hasattr(e, 'response') and e.response:
            log(f"错误响应: {e.response.text}", "ERROR")
            try:
                error_data = e.response.json()
                log(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}", "ERROR")
            except:
                pass
        return None

# ============ 3. 查询状态 ============
def poll_task_status(task_id):
    """轮询查询任务状态"""
    log("=" * 50)
    log("步骤 3/4: 轮询查询任务状态")
    log("=" * 50)
    log(f"Task ID: {task_id}")
    log(f"轮询间隔: {POLL_INTERVAL}秒")
    log(f"最大轮询次数: {MAX_POLL_ATTEMPTS}")
    
    query_payload = {
        "model": "kling-image2video-get",
        "input": task_id,
        "stream": False
    }
    
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        log(f"\n第 {attempt}/{MAX_POLL_ATTEMPTS} 次查询...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/responses",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=query_payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # 保存每次查询结果
            save_log(json.dumps(data, indent=2, ensure_ascii=False), f"poll_{attempt:02d}.json")
            
            # 解析状态 - 适配可灵API响应格式
            status = None
            video_url = None
            error_msg = None
            
            if "data" in data and isinstance(data["data"], dict):
                status = data["data"].get("task_status")
                video_url = data["data"].get("video_url") or data["data"].get("url")
                error_msg = data["data"].get("task_status_msg")
            elif "status" in data:
                status = data["status"]
            
            # 检查输出中的视频URL
            if "output" in data and isinstance(data["output"], list) and len(data["output"]) > 0:
                for item in data["output"]:
                    if isinstance(item, dict):
                        if "video" in item:
                            video_url = item["video"]
                        elif "url" in item:
                            video_url = item["url"]
            
            log(f"  状态: {status}")
            
            if status == "completed" or status == "success":
                log("✓ 任务完成!")
                if video_url:
                    log(f"  视频URL: {video_url[:80]}...")
                    return video_url
                else:
                    log("  警告: 未找到视频URL", "WARN")
                    return None
            
            elif status == "failed" or status == "error":
                log(f"✗ 任务失败: {error_msg or '未知错误'}", "ERROR")
                return None
            
            elif status == "processing" or status == "pending":
                log(f"  任务处理中，{POLL_INTERVAL}秒后重试...")
                time.sleep(POLL_INTERVAL)
            
            else:
                log(f"  未知状态: {status}，继续等待...", "WARN")
                time.sleep(POLL_INTERVAL)
        
        except requests.exceptions.RequestException as e:
            log(f"查询失败: {e}", "ERROR")
            if hasattr(e, 'response') and e.response:
                log(f"错误响应: {e.response.text}", "ERROR")
            time.sleep(POLL_INTERVAL)
    
    log("✗ 轮询超时，任务可能仍在处理中", "ERROR")
    return None

# ============ 4. 下载视频 ============
def download_video(video_url):
    """下载生成的视频"""
    log("=" * 50)
    log("步骤 4/4: 下载视频")
    log("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kling_test_{timestamp}.mp4"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        log(f"开始下载...")
        log(f"URL: {video_url[:80]}...")
        
        response = requests.get(video_url, timeout=120, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        log(f"文件大小: {total_size / 1024 / 1024:.2f} MB")
        
        with open(filepath, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0 and downloaded % (1024 * 1024) == 0:
                        progress = downloaded / total_size * 100
                        log(f"  下载进度: {progress:.1f}%")
        
        log(f"✓ 下载完成: {filepath}")
        
        # 获取文件信息
        file_size = os.path.getsize(filepath)
        log(f"  文件大小: {file_size / 1024:.2f} KB")
        
        return filepath
        
    except Exception as e:
        log(f"✗ 下载失败: {e}", "ERROR")
        return None

# ============ 主流程 ============
def main():
    log("\n" + "=" * 60)
    log("Kling v2.6 图生视频 - 异步调用测试")
    log("=" * 60)
    log(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"输出目录: {OUTPUT_DIR}")
    log("")
    
    # 检查API Key
    if API_KEY == "your-api-key-here":
        log("错误: 请设置 DMXAPI_KEY 环境变量", "ERROR")
        log("示例: export DMXAPI_KEY=your-api-key", "INFO")
        sys.exit(1)
    
    # 步骤1: 余额检查
    if not check_balance():
        log("余额检查失败，终止执行", "ERROR")
        sys.exit(1)
    
    # 步骤2: 提交任务
    task_id = submit_task()
    if not task_id:
        log("任务提交失败，终止执行", "ERROR")
        sys.exit(1)
    
    # 步骤3: 轮询查询
    video_url = poll_task_status(task_id)
    if not video_url:
        log("未能获取视频URL", "ERROR")
        log(f"Task ID: {task_id} - 可稍后手动查询")
        sys.exit(1)
    
    # 步骤4: 下载视频
    filepath = download_video(video_url)
    if not filepath:
        log("视频下载失败", "ERROR")
        sys.exit(1)
    
    # 完成
    log("\n" + "=" * 60)
    log("✓ 全部完成!")
    log("=" * 60)
    log(f"视频文件: {filepath}")
    log(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("")
    log("所有日志和响应保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
