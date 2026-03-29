#!/usr/bin/env python3
"""
可灵 v2.6 图生视频 - 生产级调用脚本
=====================================
基于 DMXAPI 的可灵视频生成工具
适用于 AI短剧制作的第三阶段：视频生成

使用方法:
    python kling_video_generator.py --image <图片URL> --prompt <提示词> [--duration 5] [--mode pro]

示例:
    python kling_video_generator.py \
        --image "https://example.com/character.jpg" \
        --prompt "机器人缓缓转头，眼中闪烁温暖光芒，微风轻拂" \
        --duration 5 \
        --mode pro \
        --output ./videos/
"""

import requests
import json
import re
import time
import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# ==================== 配置 ====================
DEFAULT_API_KEY = os.environ.get("DMXAPI_KEY", "")
DEFAULT_OUTPUT_DIR = "./kling_videos"
API_BASE_URL = "https://www.dmxapi.cn/v1/responses"

# ==================== 颜色输出 ====================
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    END = "\033[0m"

def log_info(msg): print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")
def log_success(msg): print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")
def log_warning(msg): print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")
def log_error(msg): print(f"{Colors.RED}[ERR]{Colors.END} {msg}")
def log_progress(msg): print(f"{Colors.CYAN}[...]{Colors.END} {msg}", end="\r")

# ==================== 核心功能 ====================

class KlingVideoGenerator:
    """可灵视频生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": api_key
        }
    
    def submit_task(self, image_url: str, prompt: str, duration: int = 5, mode: str = "pro") -> dict:
        """
        提交视频生成任务
        
        Args:
            image_url: 参考图片URL
            prompt: 视频生成提示词
            duration: 视频时长(5或10秒)
            mode: 生成模式(std/pro)
        
        Returns:
            dict: 包含task_id的任务信息
        """
        if duration not in [5, 10]:
            raise ValueError("duration只能是5或10秒")
        
        payload = {
            "model": "kling-v2-6-image2video",
            "input": prompt,
            "image": image_url,
            "duration": duration,
            "mode": mode
        }
        
        log_info(f"提交任务: {prompt[:50]}...")
        log_info(f"  时长: {duration}秒 | 模式: {mode}")
        
        try:
            response = requests.post(API_BASE_URL, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"API返回错误: {data.get('message')}")
            
            task_id = data["data"]["task_id"]
            log_success(f"任务已提交 | Task ID: {task_id}")
            
            return {
                "task_id": task_id,
                "status": data["data"].get("task_status"),
                "created_at": data["data"].get("created_at")
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
    
    def query_result(self, task_id: str, timeout: int = 300) -> dict:
        """
        流式查询任务结果
        
        Args:
            task_id: 任务ID
            timeout: 最长等待时间(秒)
        
        Returns:
            dict: 包含视频URL的结果
        """
        payload = {
            "model": "kling-text2video-get",
            "input": task_id,
            "stream": True
        }
        
        log_info(f"查询任务状态: {task_id}")
        log_progress("等待生成完成...")
        
        start_time = time.time()
        final_result = None
        
        try:
            response = requests.post(
                API_BASE_URL, 
                headers=self.headers, 
                json=payload, 
                stream=True,
                timeout=timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        data_str = line_text[6:]
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            json_data = json.loads(data_str)
                            
                            # 检查是否完成
                            if json_data.get("type") == "response.completed":
                                final_result = json_data
                                break
                                
                            # 更新进度显示
                            resp = json_data.get("response", {})
                            status = resp.get("status", "")
                            if status == "in_progress":
                                elapsed = int(time.time() - start_time)
                                log_progress(f"生成中... 已等待 {elapsed} 秒")
                                
                        except json.JSONDecodeError:
                            continue
            
            if not final_result:
                raise Exception("未收到完整响应")
            
            # 解析视频URL
            return self._parse_video_url(final_result)
            
        except requests.exceptions.Timeout:
            raise Exception(f"查询超时(>{timeout}秒)，请稍后手动查询")
        except Exception as e:
            raise Exception(f"查询失败: {e}")
    
    def _parse_video_url(self, result: dict) -> dict:
        """从响应中解析视频URL"""
        try:
            output = result.get("response", {}).get("output", [])
            if not output:
                raise Exception("响应中无output数据")
            
            text_content = output[0].get("content", [{}])[0].get("text", "")
            
            # 提取视频URL
            url_match = re.search(r'(https?://[^\s]+\.mp4[^\s]*)', text_content)
            if not url_match:
                raise Exception("未找到视频URL")
            
            video_url = url_match.group(1)
            video_url = re.sub(r'[\n\r].*$', '', video_url)
            
            # 提取时长
            duration_match = re.search(r'时长[:：]\s*([\d.]+)', text_content)
            duration = float(duration_match.group(1)) if duration_match else 0
            
            log_success("视频生成完成！")
            
            return {
                "video_url": video_url,
                "duration": duration,
                "task_id": result.get("response", {}).get("id", "")
            }
            
        except Exception as e:
            raise Exception(f"解析结果失败: {e}")
    
    def download_video(self, video_url: str, output_path: str) -> str:
        """下载视频到本地"""
        log_info(f"下载视频...")
        
        try:
            response = requests.get(video_url, stream=True, timeout=120)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            log_progress(f"下载进度: {percent:.1f}%")
            
            file_size = os.path.getsize(output_path)
            log_success(f"视频已保存: {output_path} ({file_size/1024/1024:.1f} MB)")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"下载失败: {e}")


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(
        description="可灵 v2.6 图生视频生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础用法
  python kling_video_generator.py -i "https://example.com/img.jpg" -p "女孩微笑"
  
  # 完整参数
  python kling_video_generator.py \\
      --image "https://example.com/robot.jpg" \\
      --prompt "机器人缓缓转头，眼中闪烁温暖光芒" \\
      --duration 10 \\
      --mode pro \\
      --output ./my_videos/ \\
      --filename robot_shot01.mp4
        """
    )
    
    parser.add_argument("-i", "--image", required=True, help="参考图片URL")
    parser.add_argument("-p", "--prompt", required=True, help="视频生成提示词")
    parser.add_argument("-d", "--duration", type=int, default=5, choices=[5, 10], 
                       help="视频时长(5或10秒，默认5)")
    parser.add_argument("-m", "--mode", default="pro", choices=["std", "pro"],
                       help="生成模式(std=标准, pro=高品质，默认pro)")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                       help=f"输出目录(默认: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("-f", "--filename", default=None,
                       help="输出文件名(默认: 自动生成)")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY,
                       help="DMXAPI密钥(也可设置DMXAPI_KEY环境变量)")
    parser.add_argument("--no-download", action="store_true",
                       help="只生成不下载，仅返回URL")
    
    args = parser.parse_args()
    
    # 验证API Key
    if not args.api_key:
        log_error("未提供API Key！请设置 --api-key 或 DMXAPI_KEY 环境变量")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    if args.filename:
        output_path = output_dir / args.filename
    else:
        timestamp = int(time.time())
        output_path = output_dir / f"kling_{timestamp}.mp4"
    
    # 初始化生成器
    generator = KlingVideoGenerator(args.api_key)
    
    try:
        # 提交任务
        print("=" * 60)
        print("可灵 v2.6 图生视频生成")
        print("=" * 60)
        
        task = generator.submit_task(
            image_url=args.image,
            prompt=args.prompt,
            duration=args.duration,
            mode=args.mode
        )
        
        # 查询结果
        print()
        result = generator.query_result(task["task_id"])
        
        print()
        log_info(f"视频URL: {result['video_url'][:80]}...")
        log_info(f"时长: {result['duration']}秒")
        
        # 下载视频
        if not args.no_download:
            print()
            generator.download_video(result["video_url"], str(output_path))
        
        print()
        print("=" * 60)
        log_success("全部完成！")
        print("=" * 60)
        
        # 输出结果JSON
        output_info = {
            "task_id": task["task_id"],
            "video_url": result["video_url"],
            "duration": result["duration"],
            "local_path": str(output_path) if not args.no_download else None
        }
        
        # 保存信息文件
        info_path = output_path.with_suffix('.json')
        with open(info_path, 'w') as f:
            json.dump(output_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n任务信息已保存: {info_path}")
        
    except KeyboardInterrupt:
        print("\n")
        log_warning("用户中断")
        sys.exit(0)
    except Exception as e:
        log_error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
