"""
AI生成工具调用示例
展示如何使用存储在.env中的API密钥进行图片/视频生成
"""
import requests
import json
import time
import base64
from pathlib import Path

# 导入配置模块
import sys
sys.path.insert(0, str(Path(__file__).parent))
from api_config import get_dmxapi_token, get_jimeng_keys


# ==================== 海螺视频生成示例 ====================
def hailuo_image_to_video(image_url: str, prompt: str, duration: int = 6, resolution: str = "768P"):
    """
    使用海螺生成视频（图生视频）
    
    Args:
        image_url: 首帧图片URL
        prompt: 视频描述（支持运镜指令）
        duration: 视频时长（秒），默认6
        resolution: 分辨率，768P或1080P
    
    Returns:
        dict: 包含task_id和状态信息
    """
    token = get_dmxapi_token()
    
    url = "https://www.dmxapi.cn/v1/video_generation"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "prompt": prompt,
        "first_frame_image": image_url,
        "duration": duration,
        "resolution": resolution
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    if result.get("base_resp", {}).get("status_code") == 0:
        return {
            "success": True,
            "task_id": result["task_id"],
            "message": "任务已提交"
        }
    else:
        return {
            "success": False,
            "error": result.get("base_resp", {}).get("status_msg", "未知错误")
        }


def query_hailuo_task(task_id: str, max_retries: int = 30, interval: int = 10):
    """
    查询海螺视频生成任务状态
    
    Args:
        task_id: 任务ID
        max_retries: 最大重试次数
        interval: 查询间隔（秒）
    
    Returns:
        dict: 任务状态和文件信息
    """
    token = get_dmxapi_token()
    
    url = f"https://www.dmxapi.cn/v1/query/video_generation?task_id={task_id}"
    headers = {"Authorization": token}
    
    for i in range(max_retries):
        response = requests.get(url, headers=headers)
        result = response.json()
        
        status = result.get("status")
        
        if status == "Success":
            return {
                "success": True,
                "status": "completed",
                "file_id": result["file_id"],
                "video_width": result.get("video_width"),
                "video_height": result.get("video_height")
            }
        elif status == "Failed":
            return {
                "success": False,
                "status": "failed",
                "error": "任务生成失败"
            }
        
        print(f"[{i+1}/{max_retries}] 任务处理中，{interval}秒后重试...")
        time.sleep(interval)
    
    return {
        "success": False,
        "status": "timeout",
        "error": "查询超时"
    }


def download_hailuo_video(file_id: str, task_id: str, output_path: str = "output.mp4"):
    """
    下载海螺生成的视频
    
    Args:
        file_id: 文件ID
        task_id: 任务ID
        output_path: 保存路径
    
    Returns:
        bool: 是否下载成功
    """
    token = get_dmxapi_token()
    
    url = "https://www.dmxapi.cn/v1/files/retrieve"
    params = {"file_id": file_id, "task_id": task_id}
    headers = {"Authorization": token}
    
    # 获取下载链接
    response = requests.get(url, params=params, headers=headers)
    result = response.json()
    
    if result.get("base_resp", {}).get("status_code") != 0:
        print(f"获取下载链接失败: {result}")
        return False
    
    download_url = result["file"]["download_url"]
    
    # 下载视频
    video_response = requests.get(download_url)
    with open(output_path, "wb") as f:
        f.write(video_response.content)
    
    print(f"视频已保存: {output_path}")
    return True


# ==================== 完整工作流示例 ====================
def generate_video_workflow(image_url: str, prompt: str, output_path: str = "output.mp4"):
    """
    完整的视频生成工作流（提交→查询→下载）
    
    Args:
        image_url: 首帧图片URL
        prompt: 视频描述
        output_path: 输出文件路径
    
    Returns:
        bool: 是否成功
    """
    print("=" * 50)
    print("开始视频生成")
    print("=" * 50)
    
    # 1. 提交任务
    print("\n[1/3] 提交任务...")
    submit_result = hailuo_image_to_video(image_url, prompt)
    
    if not submit_result["success"]:
        print(f"提交失败: {submit_result.get('error')}")
        return False
    
    task_id = submit_result["task_id"]
    print(f"✅ 任务已提交，ID: {task_id}")
    
    # 2. 查询任务
    print("\n[2/3] 等待生成完成...")
    query_result = query_hailuo_task(task_id)
    
    if not query_result["success"]:
        print(f"生成失败: {query_result.get('error')}")
        return False
    
    file_id = query_result["file_id"]
    print(f"✅ 生成完成，文件ID: {file_id}")
    
    # 3. 下载视频
    print("\n[3/3] 下载视频...")
    if download_hailuo_video(file_id, task_id, output_path):
        print("✅ 全部完成！")
        return True
    else:
        print("❌ 下载失败")
        return False


# ==================== 主函数 ====================
if __name__ == "__main__":
    # 检查API配置
    print("检查API配置...")
    from api_config import APIConfig
    APIConfig.print_status()
    
    # 示例调用（取消注释使用）
    # generate_video_workflow(
    #     image_url="https://example.com/image.jpg",
    #     prompt="A robot gently holds a flower [推进], then looks at it with soft eyes [固定].",
    #     output_path="robot_video.mp4"
    # )
