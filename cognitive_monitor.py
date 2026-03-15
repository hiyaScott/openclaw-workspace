#!/usr/bin/env python3
"""
Shrimp Jetton 认知负载监控 v5.16 - 优化版
- 评分算法优化（只统计活跃任务）
- 检查间隔30秒
- 文件状态缓存减少I/O
"""

import json
import os
import sys
import time
import glob
import psutil
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from collections import OrderedDict

# 配置日志
log_file = '/var/log/cognitive_monitor.log'
logger = logging.getLogger('cognitive_monitor')
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# 从环境变量读取配置，未设置时使用默认值
UPSTASH_REDIS_REST_URL = os.environ.get('UPSTASH_REDIS_REST_URL', 'https://singular-snake-71209.upstash.io')
UPSTASH_REDIS_REST_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN', 'gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk')
WORKSPACE = os.environ.get('COGNITIVE_WORKSPACE', '/root/.openclaw/agents/main/sessions')
DB_PATH = os.environ.get('COGNITIVE_DB_PATH', '/var/lib/cognitive_monitor/history.db')

# 健康检查配置
HEARTBEAT_FILE = os.environ.get('COGNITIVE_HEARTBEAT_FILE', '/var/run/cognitive_monitor_heartbeat.json')
HEARTBEAT_TIMEOUT = int(os.environ.get('COGNITIVE_HEARTBEAT_TIMEOUT', 120))  # 默认120秒超时

def update_heartbeat(status='running', error=None):
    """更新心跳文件，用于自监控"""
    try:
        heartbeat_data = {
            'timestamp': datetime.now().isoformat(),
            'unix_time': int(time.time()),
            'status': status,
            'pid': os.getpid(),
            'hostname': os.uname().nodename,
        }
        if error:
            heartbeat_data['error'] = str(error)
        
        # 写入临时文件后原子重命名，避免读取时损坏
        temp_file = HEARTBEAT_FILE + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(heartbeat_data, f)
        os.rename(temp_file, HEARTBEAT_FILE)
    except Exception as e:
        logger.warning(f"Failed to update heartbeat: {e}")

def check_monitor_health():
    """检查监控服务健康状态（可以被外部调用）"""
    try:
        if not os.path.exists(HEARTBEAT_FILE):
            return {'healthy': False, 'reason': 'heartbeat file not found'}
        
        with open(HEARTBEAT_FILE, 'r') as f:
            heartbeat = json.load(f)
        
        last_time = heartbeat.get('unix_time', 0)
        elapsed = int(time.time()) - last_time
        
        if elapsed > HEARTBEAT_TIMEOUT:
            return {
                'healthy': False, 
                'reason': f'heartbeat timeout ({elapsed}s > {HEARTBEAT_TIMEOUT}s)',
                'last_seen': heartbeat.get('timestamp'),
                'elapsed_seconds': elapsed
            }
        
        return {
            'healthy': True,
            'status': heartbeat.get('status'),
            'pid': heartbeat.get('pid'),
            'last_seen': heartbeat.get('timestamp'),
            'elapsed_seconds': elapsed
        }
    except Exception as e:
        return {'healthy': False, 'reason': f'error reading heartbeat: {e}'}
file_cache = OrderedDict()
CACHE_TTL = 60

# 会话状态跟踪
session_states = {}

def init_database():
    """初始化SQLite数据库"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                score INTEGER NOT NULL,
                pending INTEGER NOT NULL,
                processing INTEGER NOT NULL,
                tokens INTEGER NOT NULL,
                cpu REAL NOT NULL,
                memory REAL NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp)')
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database init error: {e}")

def save_to_database(data):
    """保存数据到本地数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (timestamp, score, pending, processing, tokens, cpu, memory)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['cognitive_score'],
            data['pending_count'],
            data['processing_count'],
            data['total_tokens'],
            data['cpu_percent'],
            data['memory_percent']
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Database save error: {e}")

def save_to_local_file(data):
    """保存到本地JSON文件（供GitHub Pages使用）"""
    try:
        # 构建输出路径（相对于脚本位置）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'portfolio-blog', 'status-monitor')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, 'cognitive-data.json')
        
        # 写入JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"Data saved to {output_file}")
    except Exception as e:
        logger.warning(f"Local file save error: {e}")

def get_history_from_db(minutes):
    """从数据库获取历史数据 - 30秒原始数据点，不进行分钟聚合"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        since = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        cursor.execute('''
            SELECT timestamp, score, pending, processing, tokens
            FROM history
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (since,))
        rows = cursor.fetchall()
        conn.close()
        
        # 直接返回30秒间隔的原始数据点
        result = []
        for row in rows:
            ts = datetime.fromisoformat(row[0])
            result.append({
                'timestamp': ts.strftime('%H:%M:%S'),
                'score': row[1],
                'pending': row[2],
                'processing': row[3],
                'tokens': row[4]
            })
        return result
    except Exception as e:
        logger.warning(f"Database query error: {e}")
        return []

def get_cached_file_info(file_path):
    """获取带缓存的文件信息"""
    now = time.time()
    if file_path in file_cache:
        info, cache_time = file_cache[file_path]
        if now - cache_time < CACHE_TTL:
            return info
    
    try:
        stat = os.stat(file_path)
        info = {'mtime': stat.st_mtime, 'size': stat.st_size}
        file_cache[file_path] = (info, now)
        if len(file_cache) > 30:
            file_cache.popitem(last=False)
        return info
    except OSError as e:
        logger.debug(f"File stat error for {file_path}: {e}")
        return {'mtime': 0, 'size': 0}

def analyze_session_quick(file_path, file_info):
    """快速分析会话状态，只读取最后几行"""
    now = time.time()
    
    try:
        # 只读取最后100KB避免大文件问题，同时确保捕获足够上下文
        with open(file_path, 'rb') as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 102400))  # 100KB
            content = f.read().decode('utf-8', errors='ignore')
            lines = [l for l in content.split('\n') if l.strip()]
        
        if not lines:
            return None
        
        messages = len(lines)
        tool_count = content.count('"tool_calls"') + content.count('"tool_use"')
        
        # 查找最后一条消息的角色（包括tool角色）
        last_user_idx = -1
        last_assistant_idx = -1
        last_tool_idx = -1
        last_timestamp = None
        
        for i, line in enumerate(reversed(lines)):
            idx = len(lines) - 1 - i
            if '"role":' in line or '"role" :' in line:
                if '"user"' in line and last_user_idx == -1:
                    last_user_idx = idx
                elif '"assistant"' in line and last_assistant_idx == -1:
                    last_assistant_idx = idx
                elif '"tool"' in line and last_tool_idx == -1:
                    last_tool_idx = idx
            
            # 提取最后的时间戳
            if last_timestamp is None and '"timestamp":' in line:
                try:
                    d = json.loads(line)
                    last_timestamp = d.get('timestamp', '')
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON parse error in timestamp extraction: {e}")
                    pass
        
        # 判断状态：基于最近的角色和活动
        is_waiting = False
        is_processing = False
        has_recent_tool = False
        wait_sec = 0
        
        # 获取最后活跃的角色索引
        last_role_idx = max(last_user_idx, last_assistant_idx, last_tool_idx)
        
        # 如果有工具调用且时间很近（5分钟内），标记为处理中
        mtime_age = now - file_info['mtime']
        if tool_count > 0 and mtime_age < 300:
            has_recent_tool = True
        
        # 判断逻辑：
        # 1. 如果最后一条是user → 等待中
        # 2. 如果最后一条是tool/assistant 且有活跃工具调用 → 处理中
        # 3. 如果文件最近更新（<30秒）且有工具 → 处理中
        if last_user_idx == last_role_idx and last_user_idx != -1:
            is_waiting = True
            wait_sec = mtime_age
        elif (last_tool_idx > last_assistant_idx or has_recent_tool or mtime_age < 30) and tool_count > 0:
            is_processing = True
        elif last_assistant_idx == last_role_idx and mtime_age < 60:
            # 最近刚回复，可能还在处理后续
            is_processing = True
        
        # 估算Token（简化）
        tokens = messages * 150 + tool_count * 300
        
        # 会话类型
        is_group = '"chat_type":"group"' in content or '"groupId"' in content
        
        # 活跃度评分（基于文件修改时间和工具调用）
        activity_score = 0
        if mtime_age < 30:
            activity_score = 10  # 最近30秒活跃
        elif mtime_age < 300:
            activity_score = 5   # 最近5分钟活跃
        elif mtime_age < 600:
            activity_score = 2   # 最近10分钟活跃
        
        return {
            'messages': messages,
            'tokens': tokens,
            'tool_count': tool_count,
            'is_waiting': is_waiting,
            'is_processing': is_processing,
            'has_recent_tool': has_recent_tool,
            'wait_sec': wait_sec,
            'is_group': is_group,
            'last_mtime': file_info['mtime'],
            'mtime_age': mtime_age,
            'activity_score': activity_score,
            'last_role': 'user' if last_user_idx == last_role_idx else ('tool' if last_tool_idx == last_role_idx else 'assistant')
        }
    except Exception as e:
        logger.warning(f"Quick analyze error {file_path}: {e}")
        return None

def get_session_label(content, file_path):
    """根据会话内容生成具体任务描述"""
    content_lower = content.lower()
    
    # 提取最近的用户消息作为任务提示
    try:
        lines = content.split('\n')
        recent_messages = []
        for line in reversed(lines[-50:]):  # 看最近50行
            if '"role": "user"' in line or '"role":"user"' in line:
                try:
                    data = json.loads(line)
                    msg = data.get('content', '')
                    if msg and len(msg) > 5:
                        recent_messages.append(msg[:100])  # 截取前100字符
                        if len(recent_messages) >= 3:
                            break
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON parse error in message extraction: {e}")
                    pass
        task_hint = ' '.join(recent_messages).lower()
    except Exception as e:
        logger.warning(f"Error extracting recent messages: {e}")
        task_hint = ''
    
    # SRPG相关 - 具体识别哪款游戏和做什么
    if any(k in content for k in ['srpg', '战棋', '天地劫', '梦幻模拟', '铃兰之剑', '角色技能', '五内化蕴', '计策']):
        if '天地劫' in content:
            return '🟢 SRPG: 天地劫数据分析'
        elif '梦幻模拟' in content or '梦战' in content:
            if '数据' in content or '收集' in content:
                return '🟢 SRPG: 梦幻模拟战数据收集'
            return '🟢 SRPG: 梦幻模拟战研究'
        elif '铃兰之剑' in content:
            return '🟢 SRPG: 铃兰之剑数据分析'
        elif '三国' in content and ('望神州' in content or '三国志' in content):
            return '🟢 SRPG: 三国战棋分析'
        elif '计策' in content or 'phase3' in task_hint:
            return '🟢 SRPG: 计策系统设计'
        elif '数据' in content or '数据库' in content:
            return '🟢 SRPG: 数据库整理'
        elif '分析' in content or '统计' in content:
            return '🟢 SRPG: 机制分析'
        return '🟢 SRPG: 战棋研究'
    
    # 编钟/乐器相关
    elif any(k in content for k in ['编钟', '和弦', '琶音', '烧绳子', '音频', 'music', 'chord']):
        if '烧绳子' in content or '动画' in content:
            return '🔵 编钟: 烧绳子动画修复'
        elif '和弦' in content or 'chord' in content_lower:
            return '🔵 编钟: 和弦系统开发'
        elif 'midi' in content_lower or '导入' in content:
            return '🔵 编钟: MIDI导入功能'
        return '🔵 编钟: 乐器模拟器开发'
    
    # 音频/Wwise相关
    elif any(k in content for k in ['wwise', '音效', 'sound', 'audio']):
        if 'wwise' in content_lower:
            return '🔵 音频: Wwise集成研究'
        return '🔵 音频: 音效设计'
    
    # 游戏开发/Godot
    elif any(k in content for k in ['godot', 'build', '导出', '部署', 'grid dominion']):
        if '导出' in content or 'build' in content_lower:
            return '🔴 开发: 游戏导出打包'
        elif 'grid' in content_lower or 'dominion' in content_lower:
            return '🔴 开发: Grid Dominion开发'
        return '🔴 开发: 游戏开发'
    
    # Git/代码相关
    elif any(k in content for k in ['git', 'commit', 'push', 'github', '发布']):
        if 'push' in content_lower or '发布' in content:
            return '🔴 Git: 代码推送发布'
        return '🔴 Git: 代码管理'
    
    # 设计文档
    elif any(k in content for k in ['设计案', 'gdd', '策划', '游戏设计', '机制']):
        if '编钟' in content:
            return '🟡 设计: 编钟设计案'
        return '🟡 设计: 游戏设计文档'
    
    # 飞书相关
    elif any(k in content for k in ['飞书', 'feishu', 'bitable']):
        if '文档' in content:
            return '🟡 飞书: 文档处理'
        return '🟡 飞书: 数据操作'
    
    # 文件传输
    elif any(k in content for k in ['文件传输', '上传', '下载', '备份']):
        if '传输' in content or 'upload' in content_lower:
            return '🟡 文件: 传输服务'
        return '🟡 文件: 文件操作'
    
    # 状态监控/系统
    elif any(k in content for k in ['状态', '监控', 'metrics', '负载', '认知']):
        if '认知' in content or 'cognitive' in task_hint:
            return '🟢 系统: 认知监控优化'
        elif '监控' in content:
            return '🟢 系统: 监控服务'
        return '🟢 系统: 系统维护'
    
    # 数学/教育
    elif any(k in content for k in ['数学', '奥数', '题目', '解题']):
        return '🟡 教育: 数学题目解答'
    
    # 根据最近消息内容判断
    elif task_hint:
        if any(k in task_hint for k in ['创建', '生成', 'build']):
            return '🟡 任务: 创建/生成内容'
        elif any(k in task_hint for k in ['修复', 'bug', '问题']):
            return '🔴 任务: Bug修复'
        elif any(k in task_hint for k in ['分析', '研究']):
            return '🟢 任务: 分析研究'
    
    # 根据文件路径判断
    if 'spawn' in file_path.lower():
        return '🟡 后台: 子代理任务'
    elif 'sub' in file_path.lower():
        return '🟡 后台: 后台处理'
    
    return '🟢 对话: 一般对话'

def get_active_sessions():
    """获取活跃会话列表"""
    pattern = os.path.join(WORKSPACE, "*.jsonl")
    files = glob.glob(pattern)
    
    sessions = []
    now = time.time()
    
    for f in files:
        info = get_cached_file_info(f)
        if info['mtime'] == 0:
            continue
        
        # 只保留最近10分钟的活跃文件
        if now - info['mtime'] < 600:
            analysis = analyze_session_quick(f, info)
            if analysis:
                analysis['file'] = f
                sessions.append(analysis)
    
    return sessions

def calculate_score(sessions):
    """优化评分算法 - 基于活跃任务和文件活跃度"""
    pending_count = sum(1 for s in sessions if s.get('is_waiting'))
    processing_count = sum(1 for s in sessions if s.get('is_processing'))
    recent_active_count = sum(1 for s in sessions if s.get('mtime_age', 999) < 300)  # 5分钟内活跃
    total_tool_calls = sum(s.get('tool_count', 0) for s in sessions)
    
    # 活跃度总评分
    total_activity = sum(s.get('activity_score', 0) for s in sessions)
    
    # 等待时间评分
    max_wait = 0
    if pending_count > 0:
        max_wait = max((s.get('wait_sec', 0) for s in sessions if s.get('is_waiting')), default=0)
    
    # 处理中任务的Token
    processing_tokens = sum(s.get('tokens', 0) for s in sessions if s.get('is_processing'))
    
    # 计算预计响应时间 (秒)
    estimated_response = 0
    if processing_count > 0:
        # 每个处理中任务预估30-60秒，取决于token量
        base_time = processing_count * 30
        token_time = min(60, processing_tokens / 50000 * 30)  # 每50k tokens加最多30秒
        estimated_response = int(base_time + token_time)
    elif pending_count > 0:
        # 排队等待，每排队1个加15秒
        estimated_response = pending_count * 15
    
    # 基础评分 (0-50分) - 基于活跃会话数和工具调用
    base_score = min(50, recent_active_count * 10 + total_tool_calls * 2 + total_activity)
    
    # 等待时间加成 (0-30分)
    if max_wait < 60:
        wait_score = max_wait * 0.25
    elif max_wait < 300:
        wait_score = 15 + (max_wait - 60) * 0.0625
    else:
        wait_score = min(30, 30)
    
    # Token负载加成 (0-20分)
    token_score = min(20, processing_tokens / 5000)
    
    # 空闲保底
    if pending_count == 0 and processing_count == 0 and recent_active_count == 0:
        return 5, {
            'wait_score': 0, 'token_score': 0, 'base_score': 0,
            'active_sessions': 0, 'recent_active': 0, 'tool_calls': 0,
            'estimated_response': 0
        }
    
    final_score = min(100, base_score + wait_score + token_score)
    
    return int(final_score), {
        'wait_score': int(wait_score),
        'token_score': int(token_score),
        'base_score': int(base_score),
        'active_sessions': len(sessions),
        'recent_active': recent_active_count,
        'tool_calls': total_tool_calls,
        'pending': pending_count,
        'processing': processing_count,
        'estimated_response': estimated_response
    }

def get_status_text(score):
    """调整后的阈值"""
    if score >= 65:
        return "high", "🔴 高负载", "建议等待"
    elif score >= 45:
        return "medium", "🟡 中等负载", "建议简单任务"
    elif score >= 25:
        return "low", "🔵 轻负载", "30秒内响应"
    else:
        return "idle", "🟢 空闲", "立即响应"

def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m"
    else:
        return f"{int(seconds/3600)}h"

def update_redis(data):
    """更新Redis，带重试"""
    for attempt in range(3):
        try:
            url = f"{UPSTASH_REDIS_REST_URL}/set/cognitive.json"
            headers = {"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}", "Content-Type": "application/json"}
            response = requests.post(url, json={"value": json.dumps(data)}, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Redis update failed: {e}")
    return False

def main():
    logger.info("🧠 Cognitive Monitor v5.17 - Stock Chart Edition Started")
    logger.info(f"PID: {os.getpid()}, Check interval: 30s")
    
    # 初始化数据库
    init_database()
    
    start_time = time.time()
    cycle = 0
    
    while True:
        try:
            cycle += 1
            
            # 获取活跃会话
            sessions = get_active_sessions()
            
            # 计算评分
            score, breakdown = calculate_score(sessions)
            code, text, suggestion = get_status_text(score)
            
            # 构建任务队列（显示更多细节）
            task_queue = []
            for s in sessions:
                status_parts = []
                if s.get('is_waiting'):
                    status_parts.append(f"⏳ wait {format_duration(s.get('wait_sec', 0))}")
                if s.get('is_processing'):
                    status_parts.append("🔄 processing")
                if s.get('has_recent_tool'):
                    status_parts.append(f"🔧 tools:{s.get('tool_count', 0)}")
                if not status_parts:
                    age = s.get('mtime_age', 999)
                    if age < 300:
                        status_parts.append(f"📝 active ({format_duration(age)} ago)")
                    else:
                        status_parts.append("✅ idle")
                
                # 读取文件内容以生成智能标签
                try:
                    with open(s['file'], 'rb') as f:
                        f.seek(0, 2)
                        size = f.tell()
                        f.seek(max(0, size - 51200))  # 50KB
                        content = f.read().decode('utf-8', errors='ignore')
                    label = get_session_label(content, s['file'])
                except Exception as e:
                    logger.debug(f"Error generating session label for {s['file']}: {e}")
                    label = '🟢 对话处理'
                
                task_queue.append({
                    'label': label,
                    'name': os.path.basename(s['file'])[:8],
                    'status': ' | '.join(status_parts),
                    'tokens': s.get('tokens', 0),
                    'last_role': s.get('last_role', '?')
                })
            
            # 系统指标
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory().percent
            except Exception as e:
                logger.warning(f"Error getting system metrics: {e}")
                cpu, mem = 0, 0
            
            # 计算格式化值
            total_tokens = sum(s.get('tokens', 0) for s in sessions)
            estimated_response = breakdown.get('estimated_response', 0)
            
            # 格式化函数
            def format_tokens(n):
                if n >= 1000000:
                    return f"{n/1000000:.1f}M"
                elif n >= 1000:
                    return f"{n/1000:.1f}k"
                return str(n)
            
            def format_duration_short(seconds):
                if seconds < 60:
                    return f"{int(seconds)}s"
                elif seconds < 3600:
                    return f"{int(seconds/60)}m"
                else:
                    return f"{int(seconds/3600)}h"
            
            # 构建数据
            data = {
                "timestamp": datetime.now().isoformat(),
                "cognitive_score": score,
                "score_breakdown": breakdown,
                "status_code": code,
                "status_text": text,
                "suggestion": suggestion,
                "active_sessions": len(sessions),
                "recent_active_count": breakdown.get('recent_active', 0),
                "total_tool_calls": breakdown.get('tool_calls', 0),
                "pending_count": breakdown.get('pending', 0),
                "processing_count": breakdown.get('processing', 0),
                "total_tokens": total_tokens,
                "total_tokens_formatted": format_tokens(total_tokens),
                "estimated_response": estimated_response,
                "estimated_response_formatted": format_duration_short(estimated_response) if estimated_response > 0 else "Now",
                "task_queue": task_queue,
                "cpu_percent": cpu,
                "memory_percent": mem,
                "monitor_uptime": int(time.time() - start_time),
                "monitor_cycles": cycle
            }
            
            # 保存到本地数据库
            save_to_database(data)
            
            # 添加历史数据到Redis（5m/15m/1h）
            data['history_5m'] = get_history_from_db(5)
            data['history_15m'] = get_history_from_db(15)
            data['history_1h'] = get_history_from_db(60)
            
            # 更新Redis
            if update_redis(data):
                ts = datetime.now().strftime("%H:%M:%S")
                bd = breakdown
                logger.info(f"[{ts}] Score:{score}% {text} "
                           f"(sessions:{bd.get('active_sessions',0)}, recent:{bd.get('recent_active',0)}, "
                           f"tools:{bd.get('tool_calls',0)}, pending:{bd.get('pending',0)}, proc:{bd.get('processing',0)})")
                
                # 同时保存到本地文件（供GitHub Pages使用）
                save_to_local_file(data)
                
                # 更新心跳（自监控）
                update_heartbeat(status='running')
            
        except Exception as e:
            logger.error(f"Cycle error: {e}", exc_info=True)
            update_heartbeat(status='error', error=e)
        
        # 30秒间隔
        time.sleep(30)

if __name__ == "__main__":
    main()