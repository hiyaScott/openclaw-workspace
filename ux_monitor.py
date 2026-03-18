#!/usr/bin/env python3
"""
Shrimp Jetton 用户体验监控 v6.0
核心指标：响应延迟 + 待处理队列 + 认知深度
"""

import json
import os
import time
import glob
from datetime import datetime
from urllib import request

UPSTASH_REDIS_REST_URL = "https://singular-snake-71209.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk"

def get_session_files():
    """获取活跃会话"""
    pattern = "/root/.openclaw/agents/main/sessions/*.jsonl"
    files = glob.glob(pattern)
    
    active = []
    for f in files:
        try:
            stat = os.stat(f)
            if time.time() - stat.st_mtime < 300:  # 5分钟内活跃
                active.append({
                    'file': f,
                    'name': os.path.basename(f),
                    'mtime': stat.st_mtime
                })
        except:
            pass
    return active

def analyze_responsiveness(file_path):
    """分析响应延迟 - 关键指标"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            return {'status': 'idle', 'last_response_sec': 0, 'pending': 0}
        
        # 获取最后两条消息的时间
        last_msg = json.loads(lines[-1])
        prev_msg = json.loads(lines[-2])
        
        last_role = last_msg.get('role', '')
        last_time = last_msg.get('timestamp', '')
        
        # 如果最后一条是 user 消息，说明在等待回复
        if last_role == 'user':
            # 计算等待时间
            try:
                wait_time = time.time() - os.path.getmtime(file_path)
                return {
                    'status': 'waiting_response',
                    'wait_sec': int(wait_time),
                    'pending': 1
                }
            except:
                return {'status': 'unknown', 'wait_sec': 0, 'pending': 0}
        
        # 如果最后一条是 assistant，说明已回复
        return {'status': 'responded', 'wait_sec': 0, 'pending': 0}
        
    except Exception as e:
        return {'status': 'error', 'wait_sec': 0, 'pending': 0}

def calculate_user_experience_score(sessions):
    """计算用户体验评分 - 核心是响应速度"""
    
    total_pending = 0       # 待回复消息数
    max_wait_time = 0      # 最长等待时间
    busy_sessions = 0      # 忙碌会话数
    
    session_details = []
    
    for sess in sessions:
        resp = analyze_responsiveness(sess['file'])
        
        # 判断任务类型
        fname = sess['name'].lower()
        if 'subagent' in fname:
            task_type = "🤖 后台任务"
        elif 'cron' in fname:
            task_type = "⏰ 定时任务"
        elif 'feishu' in fname and 'group' in fname:
            task_type = "👥 群聊对话"
        elif 'feishu' in fname:
            task_type = "💬 私聊对话"
        else:
            task_type = "💭 一般对话"
        
        # 状态判断
        if resp['status'] == 'waiting_response':
            wait_time = resp.get('wait_sec', 0)
            total_pending += 1
            max_wait_time = max(max_wait_time, wait_time)
            busy_sessions += 1
            
            # 等待时间分级
            if wait_time > 120:
                urgency = "🔴 等待超2分钟"
            elif wait_time > 60:
                urgency = "🟡 等待超1分钟"
            else:
                urgency = "⏳ 等待中"
            
            session_details.append({
                'name': task_type,
                'status': urgency,
                'wait_sec': wait_time
            })
        else:
            session_details.append({
                'name': task_type,
                'status': "✅ 已回复/空闲",
                'wait_sec': 0
            })
    
    # 用户体验评分 (0-100) - 基于响应延迟
    # 核心逻辑：等待时间越长，评分越低
    
    if total_pending == 0:
        ux_score = 10  # 空闲
        ux_label = "🟢 空闲"
        ux_desc = "当前无待处理消息，可立即响应"
    elif max_wait_time < 30:
        ux_score = 30
        ux_label = "🟡 轻负载"
        ux_desc = f"{total_pending}个对话在等待，预计30秒内响应"
    elif max_wait_time < 90:
        ux_score = 60
        ux_label = "🟠 中负载"
        ux_desc = f"{total_pending}个对话在等待，预计1-2分钟响应"
    elif max_wait_time < 180:
        ux_score = 85
        ux_label = "🔴 高负载"
        ux_desc = f"{total_pending}个对话在等待超3分钟，建议稍后"
    else:
        ux_score = 95
        ux_label = "⛔ 超负荷"
        ux_desc = f"{total_pending}个对话在等待超5分钟，强烈建议等待"
    
    return {
        'ux_score': ux_score,
        'ux_label': ux_label,
        'ux_desc': ux_desc,
        'pending_count': total_pending,
        'max_wait_sec': max_wait_time,
        'total_sessions': len(sessions),
        'session_details': session_details
    }

def update_redis(data):
    """更新 Redis"""
    try:
        url = f"{UPSTASH_REDIS_REST_URL}/set/ux_status.json"
        req = request.Request(
            url,
            data=json.dumps({"value": json.dumps(data)}).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Error] {e}")
        return False

def main():
    print("=" * 70)
    print("👤 Shrimp Jetton 用户体验监控 v6.0")
    print("=" * 70)
    print("核心指标: 响应延迟 + 待处理队列")
    print("评分逻辑: 等待时间越长 → 评分越高 → 越忙碌")
    print("=" * 70)
    
    while True:
        try:
            sessions = get_session_files()
            ux = calculate_user_experience_score(sessions)
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "ux_score": ux['ux_score'],
                "ux_label": ux['ux_label'],
                "ux_desc": ux['ux_desc'],
                "pending_count": ux['pending_count'],
                "max_wait_sec": ux['max_wait_sec'],
                "total_sessions": ux['total_sessions'],
                "session_details": ux['session_details']
            }
            
            if update_redis(data):
                time_str = datetime.now().strftime("%H:%M:%S")
                wait_str = f"{ux['max_wait_sec']}秒" if ux['max_wait_sec'] > 0 else "0秒"
                print(f"[{time_str}] {ux['ux_label']} | 评分:{ux['ux_score']:2d} | 待处理:{ux['pending_count']} | 最长等待:{wait_str}")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    main()
