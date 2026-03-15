#!/usr/bin/env python3
"""
认知监控服务健康检查脚本
检查 cognitive_monitor.py 是否正常运行
"""

import os
import sys
import json

HEARTBEAT_FILE = '/var/run/cognitive_monitor_heartbeat.json'
HEARTBEAT_TIMEOUT = 120  # 秒

def check_health():
    """检查监控服务健康状态"""
    try:
        if not os.path.exists(HEARTBEAT_FILE):
            return {
                'healthy': False, 
                'status': 'error',
                'message': '❌ 心跳文件不存在，监控服务可能已停止',
                'timestamp': None
            }
        
        with open(HEARTBEAT_FILE, 'r') as f:
            heartbeat = json.load(f)
        
        import time
        last_time = heartbeat.get('unix_time', 0)
        elapsed = int(time.time()) - last_time
        status = heartbeat.get('status', 'unknown')
        
        if status == 'error':
            return {
                'healthy': False,
                'status': 'error',
                'message': f'⚠️ 监控服务运行出错: {heartbeat.get("error", "unknown error")}',
                'timestamp': heartbeat.get('timestamp'),
                'elapsed_seconds': elapsed
            }
        
        if elapsed > HEARTBEAT_TIMEOUT:
            return {
                'healthy': False,
                'status': 'timeout',
                'message': f'🔴 监控服务心跳超时 ({elapsed}s > {HEARTBEAT_TIMEOUT}s)，可能已挂死',
                'timestamp': heartbeat.get('timestamp'),
                'elapsed_seconds': elapsed
            }
        
        return {
            'healthy': True,
            'status': 'running',
            'message': f'✅ 监控服务运行正常，上次更新: {elapsed}s前',
            'pid': heartbeat.get('pid'),
            'hostname': heartbeat.get('hostname'),
            'timestamp': heartbeat.get('timestamp'),
            'elapsed_seconds': elapsed
        }
    except Exception as e:
        return {
            'healthy': False,
            'status': 'error',
            'message': f'❌ 检查健康状态时出错: {e}',
            'timestamp': None
        }

if __name__ == '__main__':
    result = check_health()
    
    # 输出JSON格式
    if len(sys.argv) > 1 and sys.argv[1] == '--json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 输出人类可读格式
        print(result['message'])
        if result.get('pid'):
            print(f"   PID: {result['pid']}")
        if result.get('timestamp'):
            print(f"   时间: {result['timestamp']}")
    
    # 退出码：健康=0，不健康=1
    sys.exit(0 if result['healthy'] else 1)
