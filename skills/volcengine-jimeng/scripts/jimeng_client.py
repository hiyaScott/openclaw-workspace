#!/usr/bin/env python3
"""
火山引擎即梦AI客户端
支持图片/视频生成功能
"""

import os
import sys
import json
import time
import hashlib
import hmac
import datetime
import urllib.parse
import requests
from typing import Optional, Dict, Any, List


class JimengClient:
    """火山引擎即梦AI客户端"""
    
    def __init__(self, ak: Optional[str] = None, sk: Optional[str] = None, debug: bool = False):
        """
        初始化客户端
        
        Args:
            ak: Access Key ID，默认从环境变量 JIMENG_AK 读取
            sk: Secret Access Key，默认从环境变量 JIMENG_SK 读取
            debug: 是否开启调试模式
        """
        self.ak = ak or os.getenv('JIMENG_AK')
        self.sk = sk or os.getenv('JIMENG_SK')
        self.debug = debug
        
        if not self.ak or not self.sk:
            raise ValueError("请提供AK/SK或设置环境变量 JIMENG_AK / JIMENG_SK")
        
        self.host = "visual.volcengineapi.com"
        self.region = "cn-north-1"
        self.service = "cv"
    
    def _sign_request(self, action: str, version: str, body_dict: Dict[str, Any]) -> tuple:
        """
        对请求进行签名
        
        Returns:
            (url, headers, body_bytes)
        """
        now = datetime.datetime.utcnow()
        x_date = now.strftime('%Y%m%dT%H%M%SZ')
        short_x_date = x_date[:8]
        
        method = "POST"
        path = "/"
        
        query_params = {
            "Action": action,
            "Version": version
        }
        
        body_bytes = json.dumps(body_dict, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        x_content_sha256 = hashlib.sha256(body_bytes).hexdigest()
        
        signed_headers_list = ["content-type", "host", "x-content-sha256", "x-date"]
        signed_headers_str = ";".join(signed_headers_list)
        
        canonical_headers = (
            f"content-type:application/json\n"
            f"host:{self.host}\n"
            f"x-content-sha256:{x_content_sha256}\n"
            f"x-date:{x_date}\n"
        )
        
        query_string = "&".join([
            f"{k}={urllib.parse.quote(str(v), safe='-_.~')}"
            for k, v in sorted(query_params.items())
        ])
        
        canonical_request = (
            f"{method}\n{path}\n{query_string}\n"
            f"{canonical_headers}\n{signed_headers_str}\n{x_content_sha256}"
        )
        
        if self.debug:
            print("=== Canonical Request ===")
            print(canonical_request)
            print()
        
        hashed_canonical_request = hashlib.sha256(canonical_request.encode()).hexdigest()
        credential_scope = f"{short_x_date}/{self.region}/{self.service}/request"
        string_to_sign = f"HMAC-SHA256\n{x_date}\n{credential_scope}\n{hashed_canonical_request}"
        
        if self.debug:
            print("=== String to Sign ===")
            print(string_to_sign)
            print()
        
        # 密钥派生（SK使用原始base64字符串）
        k_date = hmac.new(self.sk.encode(), short_x_date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        if self.debug:
            print(f"Signature: {signature}")
            print()
        
        authorization = (
            f"HMAC-SHA256 Credential={self.ak}/{credential_scope}, "
            f"SignedHeaders={signed_headers_str}, Signature={signature}"
        )
        
        headers = {
            "Host": self.host,
            "X-Date": x_date,
            "X-Content-Sha256": x_content_sha256,
            "Content-Type": "application/json",
            "Authorization": authorization
        }
        
        url = f"https://{self.host}{path}?{query_string}"
        return url, headers, body_bytes
    
    def _do_request(self, action: str, version: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """执行请求并解析响应"""
        url, headers, body_bytes = self._sign_request(action, version, body)
        
        if self.debug:
            print(f"Request URL: {url}")
            print(f"Request Body: {body_bytes.decode()}")
            print()
        
        try:
            resp = requests.post(url, headers=headers, data=body_bytes, timeout=60)
            
            if self.debug:
                print(f"Response Status: {resp.status_code}")
                print(f"Response Body: {resp.text[:1000]}")
                print()
            
            # 先检查HTTP状态码
            if resp.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {resp.status_code}: {resp.text[:500]}',
                    'status_code': resp.status_code
                }
            
            # 解析JSON响应
            try:
                data = resp.json()
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': f'Invalid JSON response: {resp.text[:500]}',
                    'raw_response': resp.text
                }
            
            # 检查业务错误码
            if 'code' in data and data['code'] != 0:
                error_map = {
                    30403: 'NoFeatAuth - 账号没有该功能权限',
                    30404: 'FeatNotFound - 模型不存在或已下架',
                }
                error_msg = error_map.get(data['code'], data.get('message', 'Unknown error'))
                return {
                    'success': False,
                    'error': f"[{data['code']}] {error_msg}",
                    'raw': data
                }
            
            return {
                'success': True,
                'data': data
            }
            
        except requests.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.RequestException as e:
            return {'success': False, 'error': f'Request failed: {str(e)}'}
    
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        req_key: str = "jimeng_t2i_v40"
    ) -> Dict[str, Any]:
        """
        生成图片
        
        Args:
            prompt: 图片描述
            width: 图片宽度
            height: 图片高度
            seed: 随机种子，-1表示随机
            req_key: 模型标识
        
        Returns:
            {
                'success': bool,
                'image_url': str,  # 成功时返回
                'error': str,      # 失败时返回
                'raw': dict        # 原始响应
            }
        """
        body = {
            "req_key": req_key,
            "res_quota_name": "Untitle",
            "req_json": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "seed": seed
            }
        }
        
        # 尝试不同的Action/Version组合
        combinations = [
            ("LumiSync2AsyncSubmitTask", "2025-06-01"),
        ]
        
        for action, version in combinations:
            result = self._do_request(action, version, body)
            
            if result['success']:
                # 提取图片URL（根据实际响应结构调整）
                data = result['data']
                # TODO: 根据实际响应格式解析图片URL
                return {
                    'success': True,
                    'task_id': data.get('task_id'),
                    'raw': data
                }
            
            # 如果是权限问题，直接返回
            if 'NoFeatAuth' in result.get('error', ''):
                return result
        
        return result
    
    def generate_video(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        req_key: str = "lumi_ty_t2v_test"
    ) -> Dict[str, Any]:
        """
        提交视频生成任务
        
        Args:
            prompt: 视频描述
            width: 视频宽度
            height: 视频高度
            req_key: 模型标识
        
        Returns:
            {
                'success': bool,
                'task_id': str,  # 成功时返回任务ID
                'error': str     # 失败时返回
            }
        """
        body = {
            "req_key": req_key,
            "res_quota_name": "Untitle",
            "req_json": {
                "text": prompt,
                "width": width,
                "height": height
            }
        }
        
        result = self._do_request("LumiSync2AsyncSubmitTask", "2025-06-01", body)
        
        if result['success']:
            data = result['data']
            return {
                'success': True,
                'task_id': data.get('task_id') or data.get('data'),
                'raw': data
            }
        
        return result
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            {
                'success': bool,
                'status': str,  # PENDING/RUNNING/SUCCEEDED/FAILED
                'result': dict, # 成功时的结果
                'error': str    # 失败时的错误信息
            }
        """
        body = {
            "task_id": task_id
        }
        
        # TODO: 实现任务状态查询
        # 需要知道正确的Action和Version
        return {
            'success': False,
            'error': 'Task status query not implemented yet'
        }
    
    def wait_for_video(self, task_id: str, timeout: int = 300, interval: int = 10) -> Optional[str]:
        """
        轮询等待视频生成完成
        
        Args:
            task_id: 任务ID
            timeout: 最大等待时间（秒）
            interval: 轮询间隔（秒）
        
        Returns:
            视频URL或None
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)
            
            if not result['success']:
                print(f"查询失败: {result['error']}")
                return None
            
            status = result.get('status', 'UNKNOWN')
            print(f"任务状态: {status}")
            
            if status == 'SUCCEEDED':
                return result.get('result', {}).get('video_url')
            elif status == 'FAILED':
                print(f"任务失败: {result.get('error')}")
                return None
            
            time.sleep(interval)
        
        print("等待超时")
        return None


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='火山引擎即梦AI客户端')
    parser.add_argument('--ak', help='Access Key ID')
    parser.add_argument('--sk', help='Secret Access Key')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    parser.add_argument('command', choices=['image', 'video', 'test'], help='命令')
    parser.add_argument('--prompt', '-p', default='一只可爱的柴犬', help='提示词')
    parser.add_argument('--width', type=int, default=1024, help='宽度')
    parser.add_argument('--height', type=int, default=1024, help='高度')
    
    args = parser.parse_args()
    
    try:
        client = JimengClient(ak=args.ak, sk=args.sk, debug=args.debug)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    
    if args.command == 'test':
        print("测试连接...")
        result = client.generate_image(prompt=args.prompt, width=512, height=512)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'image':
        print(f"生成图片: {args.prompt}")
        result = client.generate_image(
            prompt=args.prompt,
            width=args.width,
            height=args.height
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == 'video':
        print(f"生成视频: {args.prompt}")
        result = client.generate_video(
            prompt=args.prompt,
            width=args.width,
            height=args.height
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
