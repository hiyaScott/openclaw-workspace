#!/usr/bin/env python3
"""
Shrimp Jetton 认知负载监控 v7.1 - 体感优化版
更新：
- v7.1: 优化评分算法，降低敏感度，让1个pending任务不显示为"轻负载"
- v7.0: 改进活跃会话检测
- v6.2: 最近5分钟内有活动的会话显示为"活跃中"，task_queue更准确
- v5.35: 状态显示改为"最后活跃时间"替代"等待时间"，更准确反映会话状态
- v5.34: 从Redis迁移到本地JSON Lines存储，添加自动归档
"""

import json
import os
import time
import glob
import psutil
import re
import subprocess
from datetime import datetime, timezone
from urllib import request

UPSTASH_REDIS_REST_URL = "https://singular-snake-71209.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAARYpAAIncDE2NmRhOGU0OWFhZWM0N2I4OGZlMGZkNGM5NjdjMTI5NnAxNzEyMDk"
WORKSPACE = "/root/.openclaw/agents/main/sessions"
# v5.36: 数据目录迁移到独立仓库
DATA_FILE = "/root/.openclaw/workspace/portfolio-blog/status-monitor/cognitive-data.json"
HISTORY_FILE = "/root/.openclaw/workspace/portfolio-blog/status-monitor/cognitive-history.jsonl"
ARCHIVE_DIR = "/root/.openclaw/workspace/portfolio-blog/status-monitor/archives"

# v5.34: 历史数据保留配置
HISTORY_RETENTION_DAYS = 7  # 7天热数据
ARCHIVE_RETENTION_MONTHS = 12  # 保留12个月归档

# ============================================================================
# v7.2: 六大任务分类系统
# ============================================================================
TASK_CATEGORIES = {
    "研究": {
        "icon": "🔬",
        "keywords": [
            "分析", "竞品", "调研", "研究", "benchmark", "对比",
            "方案设计", "架构设计", "技术选型", "可行性", "评估",
            "数据挖掘", "模式识别", "趋势分析", "报告"
        ],
        "description": "数据分析、竞品调研、技术方案设计"
    },
    "作品": {
        "icon": "🎮",
        "keywords": [
            "游戏开发", "游戏设计", "交互页面", "创意工具", "前端开发",
            "godot", "unity", "unreal", "游戏引擎", "关卡设计", "gdd",
            "ascii", "短剧", "短片", "动画", "视觉", "美术", "特效"
        ],
        "description": "游戏开发、交互页面、创意工具、前端开发"
    },
    "开发": {
        "icon": "⚙️",
        "keywords": [
            "后端", "api", "自动化", "脚本", "基建", "devops",
            "部署", "ci/cd", "github actions", "docker", "服务器",
            "数据库", "缓存", "消息队列", "微服务", "网关"
        ],
        "description": "后端服务、API开发、自动化脚本、技术基建"
    },
    "内容": {
        "icon": "📝",
        "keywords": [
            "文档", "设计文档", "分析报告", "知识整理", "文档编写",
            "剧本", "写作", "文案", "博客", "教程", "手册",
            "gdd", "策划案", "故事", "剧情", "叙事"
        ],
        "description": "设计文档、分析报告、知识整理、文档编写"
    },
    "系统": {
        "icon": "🔧",
        "keywords": [
            "监控", "状态", "负载", "定时任务", "cron", "heartbeat",
            "系统维护", "运维", "日志", "告警", "备份", "恢复",
            "飞书", "消息", "通知", "集成"
        ],
        "description": "飞书对话、状态监控、定时任务、系统维护"
    },
    "其他": {
        "icon": "📦",
        "keywords": [],
        "description": "临时任务、待分类事项、杂项"
    }
}

def classify_task(content):
    """
    v7.2: 智能任务分类
    根据内容匹配六大任务分类
    """
    content_lower = content.lower()
    
    # 按优先级匹配（研究 > 作品 > 开发 > 内容 > 系统 > 其他）
    category_order = ["研究", "作品", "开发", "内容", "系统"]
    
    for category in category_order:
        cat_data = TASK_CATEGORIES[category]
        for keyword in cat_data["keywords"]:
            if keyword.lower() in content_lower:
                return {
                    "category": category,
                    "icon": cat_data["icon"],
                    "description": cat_data["description"]
                }
    
    # 默认返回其他
    return {
        "category": "其他",
        "icon": TASK_CATEGORIES["其他"]["icon"],
        "description": TASK_CATEGORIES["其他"]["description"]
    }

# ============================================================================
# 扩展的关键词到标签映射 - v5.23
# ============================================================================
KEYWORD_TAGS = {
    # 系统监控类
    '监控': '系统监控',
    '状态': '系统监控', 
    '负载': '系统监控',
    'cognitive': '系统监控',
    'redis': '系统监控',
    'upstash': '系统监控',
    
    # SRPG/战棋研究类
    '战棋': '战棋研究',
    'srpg': '战棋研究',
    'tactics': '战棋研究',
    '梦幻模拟战': '战棋数据',
    '天地劫': '战棋数据',
    '铃兰之剑': '战棋数据',
    '三国志': '战棋数据',
    '三国': '战棋数据',
    '望神州': '战棋数据',
    '战棋版': '战棋数据',
    
    # 数据类
    '数据库': '数据整理',
    '数据收集': '数据整理',
    '数据分析': '数据整理',
    '数据': '数据处理',
    
    # 技能/角色设计
    '技能': '技能设计',
    '英雄': '角色数据',
    '角色': '角色数据',
    '英灵': '角色数据',
    '武将': '角色数据',
    '计策': '计策设计',
    '策略': '计策设计',
    
    # 游戏设计类
    '游戏设计': '游戏设计',
    'gdd': '游戏设计',
    '关卡': '关卡设计',
    '数值': '数值设计',
    '剧情': '剧情设计',
    '故事': '剧情设计',
    'ui': 'UI设计',
    '界面': 'UI设计',
    'ux': 'UX设计',
    '交互': 'UX设计',
    
    # 技术开发类
    'godot': 'Godot开发',
    '游戏引擎': '引擎开发',
    '引擎': '引擎开发',
    '导出': '游戏导出',
    '打包': '游戏导出',
    'build': '构建打包',
    '构建': '构建打包',
    '编译': '构建打包',
    
    # 游戏项目类
    '象棋': '象棋游戏',
    '中国象棋': '象棋游戏',
    '编钟': '编钟模拟',
    '乐器': '乐器模拟',
    '音频': '音频设计',
    '音效': '音频设计',
    '音乐': '音乐设计',
    'wwise': 'Wwise音频',
    'fmod': 'FMOD音频',
    
    # 版本控制/CI类
    'github': 'GitHub操作',
    'git': '代码版本',
    'push': '代码提交',
    'commit': '代码提交',
    'pr': 'PR审查',
    'pull request': 'PR审查',
    'merge': '代码合并',
    'workflow': 'CI/CD',
    'actions': 'CI/CD',
    'ci': 'CI/CD',
    'cd': 'CI/CD',
    '部署': '部署发布',
    'release': '版本发布',
    
    # 飞书/文档类
    '文档': '文档整理',
    '飞书': '飞书集成',
    'feishu': '飞书集成',
    'bitable': '飞书表格',
    'wiki': '知识库',
    
    # 测试/QA类
    '测试': 'QA测试',
    'qa': 'QA测试',
    'bug': 'Bug修复',
    '修复': 'Bug修复',
    'fix': 'Bug修复',
    'debug': '调试排查',
    '排查': '调试排查',
    
    # 数据勘误/校对
    '勘误': '数据勘误',
    'correction': '数据勘误',
    '数据库勘误': '数据勘误',
    '数据勘误': '数据勘误',
    '数据核对': '数据勘误',
    '数据对比': '数据勘误',
    '数据验证': '数据勘误',
    '数据校对': '数据勘误',
    '数据纠错': '数据勘误',
    '错误修正': '数据勘误',
    '数据质量': '数据勘误',
    
    # 定时任务/系统
    '定时任务': '任务调度',
    'cron': '任务调度',
    'heartbeat': '心跳监控',
    
    # 网络/搜索
    '搜索': '信息检索',
    '调研': '信息检索',
    '抓取': '网页抓取',
    '爬虫': '网页抓取',
    'api': 'API开发',
    
    # 前端/Web
    'html': '前端开发',
    'css': '前端开发',
    'javascript': '前端开发',
    'js': '前端开发',
    'react': '前端开发',
    'vue': '前端开发',
    '网站': '网站建设',
    '网页': '网页开发',
    
    # 后端/服务
    '后端': '后端开发',
    'server': '后端开发',
    'api': 'API开发',
    '数据库': '数据库',
    'db': '数据库',
    
    # AI/ML
    'ai': 'AI开发',
    '模型': '模型训练',
    '训练': '模型训练',
    '推理': '模型推理',
    'embedding': '向量嵌入',
    '向量': '向量检索',
    
    # 运维/DevOps
    'docker': '容器化',
    'k8s': 'K8s运维',
    'kubernetes': 'K8s运维',
    'nginx': '服务器配置',
    '服务器': '服务器运维',
    'ssl': '安全配置',
    '备份': '数据备份',
}

# GitHub 仓库监控列表
GITHUB_REPOS = [
    'hiyaScott/scott-portfolio',
    'hiyaScott/jetton-monitor',
]

def get_system_metrics():
    """获取系统指标"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        return {
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2)
        }
    except:
        return {'cpu_percent': 0, 'memory_percent': 0, 'memory_used_gb': 0, 'memory_total_gb': 0}

def get_github_workflow_status():
    """获取 GitHub Actions 运行状态"""
    workflows = []
    try:
        for repo in GITHUB_REPOS:
            # 使用 gh CLI 获取最近的工作流运行
            result = subprocess.run(
                ['gh', 'run', 'list', '--repo', repo, '--limit', '5', '--json', 'databaseId,workflowName,status,conclusion,startedAt,event,headBranch'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                for run in runs:
                    # 只返回正在运行或最近完成的
                    if run.get('status') in ['in_progress', 'queued', 'waiting', 'requested']:
                        workflows.append({
                            'repo': repo.split('/')[-1],
                            'name': run.get('workflowName', 'Unknown'),
                            'status': run.get('status'),
                            'conclusion': run.get('conclusion'),
                            'branch': run.get('headBranch', 'unknown'),
                            'run_id': run.get('databaseId'),
                            'type': 'github_workflow'
                        })
    except Exception as e:
        print(f"[GitHub Workflow Error] {e}")
    
    return workflows

def get_local_build_processes():
    """检测本地构建进程"""
    builds = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                # 检测构建相关进程
                build_keywords = [
                    ('godot', 'Godot导出'),
                    ('npm run build', 'NPM构建'),
                    ('webpack', 'Webpack打包'),
                    ('vite build', 'Vite构建'),
                    ('docker build', 'Docker构建'),
                    ('docker-compose', 'Docker编排'),
                    ('python setup.py', 'Python打包'),
                    ('pytest', '测试运行'),
                    ('jest', 'Jest测试'),
                    ('mvn', 'Maven构建'),
                    ('gradle', 'Gradle构建'),
                ]
                
                for keyword, label in build_keywords:
                    if keyword in cmdline.lower():
                        builds.append({
                            'pid': proc.info['pid'],
                            'name': label,
                            'type': 'local_build'
                        })
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"[Build Process Error] {e}")
    
    return builds

def get_session_files():
    """获取会话文件 - v5.32: 扩展时间窗口以检测子代理任务"""
    pattern = os.path.join(WORKSPACE, "*.jsonl")
    files = glob.glob(pattern)
    sessions = []
    now = time.time()
    for f in files:
        try:
            stat = os.stat(f)
            mtime = stat.st_mtime
            age = now - mtime
            
            # 策略调整：
            # 1. 10分钟内修改的文件 -> 活跃会话
            # 2. 10-60分钟内修改的文件 -> 可能是子代理任务，也包含进来
            if age < 600:  # 10分钟内
                sessions.append({'file': f, 'name': os.path.basename(f), 'mtime': mtime, 'is_subagent': False})
            elif age < 3600:  # 10-60分钟内，可能是子代理任务
                sessions.append({'file': f, 'name': os.path.basename(f), 'mtime': mtime, 'is_subagent': True})
        except:
            pass
    return sessions

def extract_task_label(content):
    """从内容中提取标签 - v5.23 增强版"""
    content_lower = content.lower()
    
    # 1. 先检查关键词映射（最长匹配优先）
    matched_tags = []
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in content_lower:
            matched_tags.append((len(keyword), tag))
    
    if matched_tags:
        # 按关键词长度排序，取最长的匹配
        matched_tags.sort(reverse=True)
        return matched_tags[0][1][:10]
    
    # 2. 检测后台任务
    if 'sessions_spawn' in content:
        match = re.search(r'"task"\s*:\s*"([^"]{5,80})', content)
        if match:
            task = match.group(1).strip()
            task_lower = task.lower()
            for keyword, tag in KEYWORD_TAGS.items():
                if keyword in task_lower:
                    return tag[:10]
            # 提取前10个字
            return task[:10]
    
    # 3. 检测工具调用类型
    tool_tags = [
        (['feishu_doc', 'feishu_wiki'], '飞书文档'),
        (['feishu_bitable'], '飞书表格'),
        (['feishu_drive'], '飞书云盘'),
        (['web_search', 'kimi_search'], '信息检索'),
        (['web_fetch', 'kimi_fetch'], '网页抓取'),
        (['browser'], '浏览器操作'),
        (['exec', 'process'], '命令执行'),
        (['read', 'write', 'edit'], '文件操作'),
        (['github', 'gh '], 'GitHub操作'),
        (['git '], '代码版本'),
        (['cron'], '任务调度'),
        (['sessions_spawn'], '后台任务'),
        (['canvas'], '画布操作'),
        (['nodes'], '节点控制'),
        (['gateway'], '网关管理'),
        (['message'], '消息发送'),
        (['tts'], '语音合成'),
    ]
    
    for tools, tag in tool_tags:
        for tool in tools:
            if tool in content_lower:
                return tag[:10]
    
    # 4. 检测内容主题（更智能的匹配）
    topic_patterns = [
        (r'计策|策略|谋略', '计策设计'),
        (r'角色.*技能|技能.*设计', '技能设计'),
        (r'关卡.*设计|地图.*设计', '关卡设计'),
        (r'数值.*设计|数值.*平衡', '数值设计'),
        (r'剧情|故事|叙事', '剧情设计'),
        (r'ui|界面|布局', 'UI设计'),
        (r'ux|交互|体验', 'UX设计'),
        (r'音效|音乐|声音', '音频设计'),
        (r'导出|打包|构建|build', '构建打包'),
        (r'测试|qa|验证', 'QA测试'),
        (r'bug|修复|fix', 'Bug修复'),
        (r'部署|发布|release', '部署发布'),
    ]
    
    for pattern, tag in topic_patterns:
        if re.search(pattern, content_lower):
            return tag[:10]
    
    return None

def analyze_session(file_path):
    """分析会话 - v7.2: 添加任务分类"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_tokens = 0
        tool_calls = 0
        messages = 0
        last_user_time = 0
        last_assistant_time = 0
        
        label = None
        has_recent_thinking = False
        is_group = False
        is_spawn = False
        
        # v7.2: 收集内容用于分类
        all_content = []
        
        for line in lines[-80:]:  # 检查最近80条，提高准确度
            try:
                msg = json.loads(line.strip())
                if msg.get('type') == 'message':
                    msg_data = msg.get('message', {})
                    content = str(msg_data.get('content', ''))
                    role = msg_data.get('role', '')
                    timestamp = msg.get('timestamp', '')
                    
                    total_tokens += len(content) // 4
                    messages += 1
                    
                    # v7.2: 收集内容
                    all_content.append(content)
                    
                    # 提取标签（从最近的消息中）
                    if label is None:
                        extracted = extract_task_label(content)
                        if extracted:
                            label = extracted
                    
                    # 检测后台任务
                    if 'sessions_spawn' in content:
                        is_spawn = True
                    
                    # 记录用户消息时间
                    if role == 'user':
                        last_user_time = timestamp
                        if 'group_subject' in content or '"is_group_chat": true' in content.lower():
                            is_group = True
                    
                    # 记录助手消息时间
                    elif role == 'assistant':
                        content_list = msg_data.get('content', [])
                        has_tool_result = False
                        has_text_output = False
                        
                        if isinstance(content_list, list):
                            for item in content_list:
                                if isinstance(item, dict):
                                    if item.get('type') == 'toolResult':
                                        has_tool_result = True
                                    elif item.get('type') == 'text' and len(item.get('text', '')) > 50:
                                        has_text_output = True
                                    elif item.get('type') == 'thinking':
                                        has_recent_thinking = True
                        
                        # 只有有实际输出时才更新最后助手时间
                        if has_tool_result or has_text_output:
                            last_assistant_time = timestamp
                    
                    # 检测工具调用
                    if '"toolCallId"' in content or '"tool_calls"' in content:
                        tool_calls += 1
                        
            except:
                pass
        
        # v7.2: 对收集的内容进行分类
        combined_content = ' '.join(all_content[-20:])  # 最近20条内容用于分类
        task_classification = classify_task(combined_content)
        
        # 确定会话类型和标签
        if label:
            if is_spawn:
                session_type = "🤖"
            elif is_group:
                session_type = "👥"
            else:
                session_type = "💬"
            session_name = label[:10]
        elif is_spawn:
            session_type = "🤖"
            session_name = "后台任务"
        elif is_group:
            session_type = "👥"
            session_name = "群聊"
        else:
            session_type = "💬"
            session_name = "私聊"
        
        # 状态判断
        file_mtime = os.path.getmtime(file_path)
        last_activity = time.time() - file_mtime
        
        # 解析时间戳
        try:
            user_ts = datetime.fromisoformat(last_user_time.replace('Z', '+00:00')).timestamp() if last_user_time else 0
            assistant_ts = datetime.fromisoformat(last_assistant_time.replace('Z', '+00:00')).timestamp() if last_assistant_time else 0
        except:
            user_ts = assistant_ts = 0
        
        # 三种状态判断 - v6.2: 改进活跃会话检测
        is_waiting = False
        is_processing = False
        is_active = False  # 是否是活跃会话（最近5分钟有活动）
        wait_time = 0
        
        # 检测是否有lock文件（表示正在被写入/处理中）
        lock_file = file_path + '.lock'
        has_lock = os.path.exists(lock_file)
        
        # 判断是否是活跃会话（最近5分钟内有活动）
        if last_activity < 300:  # 5分钟内
            is_active = True
        
        if user_ts > assistant_ts:
            is_waiting = True
            wait_time = int(time.time() - user_ts)
            # 如果waiting时间短且有lock文件，说明正在处理中
            if wait_time < 300 and has_lock:
                is_processing = True
                is_waiting = False  # 优先显示为处理中
        elif has_lock or (last_activity < 60 and has_recent_thinking):
            # 有lock文件，或60秒内有thinking消息 = 处理中
            is_processing = True
        
        return {
            'messages': messages,
            'estimated_tokens': total_tokens,
            'tool_calls': tool_calls,
            'is_waiting': is_waiting,
            'is_processing': is_processing,
            'is_active': is_active,  # 新增：是否是活跃会话
            'user_ts': user_ts,
            'wait_time': max(0, wait_time),
            'last_mtime': file_mtime,
            'session_type': session_type,
            'session_name': session_name,
            'full_type': f"{session_type} {session_name}",
            'has_lock': has_lock,
            # v7.2: 新增任务分类信息
            'task_category': task_classification['category'],
            'task_icon': task_classification['icon'],
            'task_description': task_classification['description']
        }
    except Exception as e:
        print(f"[analyze_session error] {e}")
        return {'messages': 0, 'estimated_tokens': 0, 'tool_calls': 0, 
                'is_waiting': False, 'is_processing': False, 'user_ts': 0, 'wait_time': 0, 'last_mtime': 0,
                'session_type': "💭", 'session_name': "未知", 'full_type': "💭 未知", 'has_lock': False,
                'task_category': '其他', 'task_icon': '📦', 'task_description': '临时任务、待分类事项、杂项'}

def get_cognitive_load():
    """获取认知负载 - v5.33: 修复任务去重问题"""
    sessions = get_session_files()
    github_workflows = get_github_workflow_status()
    local_builds = get_local_build_processes()
    
    # 合并所有任务
    all_tasks = []
    seen_sessions = set()  # 用于去重
    
    # 1. 会话任务
    if sessions:
        total_tokens = 0
        pending_count = 0
        processing_count = 0
        max_wait = 0
        recent_mtime = 0
        
        for sess in sessions:
            file_key = os.path.basename(sess['file'])  # 用于去重的key
            if file_key in seen_sessions:
                continue  # 跳过重复
            seen_sessions.add(file_key)
            
            a = analyze_session(sess['file'])
            total_tokens += a['estimated_tokens']
            recent_mtime = max(recent_mtime, a['last_mtime'])
            
            if a['is_waiting']:
                pending_count += 1
                max_wait = max(max_wait, a['wait_time'])
            elif a['is_processing']:
                processing_count += 1
            
            # 状态显示 - v5.35: 改为"最后活跃"而非"等待"，更准确
            if a['is_waiting']:
                if a['wait_time'] > 120:
                    status = f"💤 {a['wait_time']//60}分钟前活跃"
                elif a['wait_time'] > 60:
                    status = f"💤 {a['wait_time']//60}分钟前活跃"
                else:
                    status = f"💤 {a['wait_time']}秒前活跃"
            elif a['is_processing']:
                status = "🔄 处理中"
            elif a.get('is_active', False):
                # 新增：活跃但未在处理中的会话
                status = "💡 活跃中"
            else:
                status = "✅ 已回复"
            
            # 标记系统监控任务 - v5.34: 特殊处理
            is_system_monitor = '系统监控' in a['full_type']
            
            all_tasks.append({
                'name': a['full_type'],
                'status': status,
                'tokens': a['estimated_tokens'],
                'type': 'session',
                'file_key': file_key,
                'user_ts': a.get('user_ts', 0),  # 用户消息时间戳
                'is_system_monitor': is_system_monitor,  # 标记系统监控
                # v7.2: 新增任务分类
                'category': a.get('task_category', '其他'),
                'category_icon': a.get('task_icon', '📦'),
                'category_description': a.get('task_description', '临时任务、待分类事项、杂项')
            })
    else:
        total_tokens = 0
        pending_count = 0
        processing_count = 0
        max_wait = 0
        recent_mtime = 0
    
    # 2. GitHub Workflow 任务
    for wf in github_workflows:
        status_emoji = "🔄" if wf['status'] == 'in_progress' else "⏳"
        status_text = f"{status_emoji} {wf['status']}"
        all_tasks.append({
            'name': f"🚀 CI: {wf['repo']}/{wf['name'][:15]}",
            'status': status_text,
            'tokens': 0,
            'type': 'github_workflow',
            'details': wf,
            # v7.2: 新增任务分类
            'category': '开发',
            'category_icon': '⚙️',
            'category_description': '后端服务、API开发、自动化脚本、技术基建'
        })
        # GitHub 构建也算作处理中任务
        if wf['status'] in ['in_progress', 'queued']:
            processing_count += 1
    
    # 3. 本地构建进程
    for build in local_builds:
        all_tasks.append({
            'name': f"🔨 Build: {build['name']}",
            'status': "🔄 运行中",
            'tokens': 0,
            'type': 'local_build',
            'pid': build['pid'],
            # v7.2: 新增任务分类
            'category': '开发',
            'category_icon': '⚙️',
            'category_description': '后端服务、API开发、自动化脚本、技术基建'
        })
        processing_count += 1
    
    last_active = int(time.time() - recent_mtime) if recent_mtime > 0 else 999
    
    # v7.1: Mixed Score 混合评分算法 - 体感优化版
    # 基于等待时间、Token数量、队列长度、活跃会话、系统负载五因素
    # v7.1更新: 降低敏感度，让1个pending任务不显示为"轻负载"
    
    # 因素1: 等待评分 (0-20分) - 基于最长等待时间
    # 2分钟内0分(正常响应时间)，2-5分钟10分，5-10分钟15分，10分钟以上20分
    if max_wait <= 120:
        wait_score = 0
    elif max_wait <= 300:
        wait_score = 10
    elif max_wait <= 600:
        wait_score = 15
    else:
        wait_score = 20
    
    # 因素2: Token评分 (0-25分) - 基于处理中任务的Token数量
    # 每20万Tokens得5分，最高25分(需要100万tokens才满)
    processing_tokens = sum(
        t.get('tokens', 0) for t in all_tasks 
        if '🔄' in t.get('status', '') or '处理中' in t.get('status', '')
    )
    token_score = min(processing_tokens // 200000 * 5, 25)
    
    # 因素3: 队列评分 (0-25分) - 基于队列长度，非线性增长
    # 0个:0分, 1个:2分, 2个:6分, 3个:12分, 4个:20分, 5个+:25分
    total_queue = processing_count + pending_count
    queue_score_map = {0: 0, 1: 2, 2: 6, 3: 12, 4: 20}
    queue_score = queue_score_map.get(total_queue, 25)
    
    # 因素4: 活跃会话评分 (0-10分) - 降低权重
    # 只计算真正活跃的，每个2分
    recent_active_count = len([s for s in sessions if s.get('is_recent', False)])
    active_score = min(recent_active_count * 2, 10)
    
    # 因素5: 系统负载评分 (0-10分) - 保持不变
    sys_metrics = get_system_metrics()
    system_score = min((sys_metrics.get('cpu_percent', 0) + sys_metrics.get('memory_percent', 0)) // 20, 10)
    
    # 计算基础分数 (0-90)
    base_score = wait_score + token_score + queue_score + active_score + system_score
    
    # 处理加成: 处理中的任务额外加成，但上限10%
    # 每个处理中任务加3分，更温和
    processing_bonus = min(processing_count * 3, 10)
    
    # 最终分数 (0-100)
    score = min(base_score + processing_bonus, 100)
    
    # v7.0: 详细的分数分解
    score_breakdown = {
        'wait_score': wait_score,
        'token_score': token_score,
        'queue_score': queue_score,
        'active_score': active_score,
        'system_score': system_score,
        'processing_bonus': processing_bonus,
        'base_score': base_score,
        'final_score': score
    }
    
    # v7.0: 计算预估回复时间 (更精细)
    if score <= 10:
        estimated_wait = {'text': '立即', 'seconds': 0, 'detail': '可立即响应'}
    elif score <= 25:
        estimated_wait = {'text': '~15秒', 'seconds': 15, 'detail': '预计15秒内回复'}
    elif score <= 40:
        estimated_wait = {'text': '~30秒', 'seconds': 30, 'detail': '预计30秒内回复'}
    elif score <= 55:
        estimated_wait = {'text': '~1分钟', 'seconds': 60, 'detail': '预计1分钟内回复'}
    elif score <= 70:
        estimated_wait = {'text': '~2分钟', 'seconds': 120, 'detail': '预计2分钟内回复'}
    elif score <= 85:
        estimated_wait = {'text': '~3分钟', 'seconds': 180, 'detail': '预计3分钟内回复'}
    else:
        estimated_wait = {'text': '~5分钟+', 'seconds': 300, 'detail': '预计5分钟或更久'}
    
    # v6.2: 返回活跃任务到 task_queue（处理中、等待中、或最近5分钟活跃）
    active_tasks = [t for t in all_tasks if '🔄' in t.get('status', '') or '前活跃' in t.get('status', '') or '运行中' in t.get('status', '') or '活跃中' in t.get('status', '')]
    
    # 任务排序：最近活跃 > 处理中 > 已回复
    def task_priority(t):
        if '前活跃' in t.get('status', ''):
            return (0, 0, t.get('wait_time', 0))
        elif '🔄' in t.get('status', ''):
            return (1, 0, 0)
        else:
            return (2, 0, 0)
    
    active_tasks.sort(key=task_priority)
    
    return {
        'active_sessions': len(sessions),
        'pending_count': pending_count,
        'processing_count': processing_count,
        'github_workflows': len(github_workflows),
        'local_builds': len(local_builds),
        'max_wait_sec': max_wait,
        'total_tokens': total_tokens,
        'processing_tokens': processing_tokens,
        'estimated_wait': estimated_wait,
        'last_active_sec': last_active,
        'task_queue': active_tasks,
        'cognitive_score': score,
        'score_breakdown': score_breakdown,
        'system': sys_metrics,
        'workflow_details': github_workflows,
        'build_details': local_builds
    }

def determine_status(score):
    if score >= 80:
        return "high", "🔴 高负载", "建议等待，系统忙碌"
    elif score >= 55:
        return "medium", "🟡 中等负载", "可派简单任务"
    elif score >= 30:
        return "medium", "🟡 轻负载", "30秒内响应"
    else:
        return "low", "🟢 空闲", "可立即响应"

def update_redis(data):
    """v5.40: 更新 Redis，添加格式化字段"""
    try:
        # 添加格式化字段
        redis_data = dict(data)
        redis_data['total_tokens_formatted'] = f"{(redis_data.get('total_tokens', 0) / 1000):.1f}k" if redis_data.get('total_tokens', 0) > 1000 else str(redis_data.get('total_tokens', 0))
        
        # 添加状态文本
        score = redis_data.get('cognitive_score', 0)
        code, text, sug = determine_status(score)
        redis_data['status_code'] = code
        redis_data['status_text'] = text
        redis_data['suggestion'] = sug
        
        # 格式化任务队列
        formatted_tasks = []
        for task in redis_data.get('task_queue', []):
            formatted_tasks.append({
                'label': task.get('name', '💭 未知任务'),
                'status': task.get('status', '✅ 空闲'),
                'tokens': task.get('tokens', 0),
                'type': task.get('type', 'session')
            })
        redis_data['task_queue'] = formatted_tasks
        
        url = f"{UPSTASH_REDIS_REST_URL}/set/cognitive.json"
        req = request.Request(
            url,
            data=json.dumps({"value": json.dumps(redis_data)}).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Redis Error] {e}")
        return False

def update_data_file(data):
    """更新 cognitive-data.json 文件供前端读取"""
    try:
        # 转换 task_queue 格式以兼容前端
        formatted_tasks = []
        for task in data.get('task_queue', []):
            # 修复：只保留一个名称，避免重复显示
            task_name = task.get('name', '💭 未知任务')
            formatted_tasks.append({
                'label': task_name,
                'status': task.get('status', '✅ 空闲'),
                'tokens': task.get('tokens', 0),
                'type': task.get('type', 'session'),
                'last_role': 'user' if '前活跃' in task.get('status', '') else 'assistant',
                # v7.2: 新增任务分类
                'category': task.get('category', '其他'),
                'category_icon': task.get('category_icon', '📦'),
                'category_description': task.get('category_description', '临时任务、待分类事项、杂项')
            })
        
        # 构建前端兼容的数据格式
        # v7.1: 使用正确的 score_breakdown
        sb = data.get('score_breakdown', {})
        output = {
            "timestamp": data.get('timestamp'),
            "cognitive_score": data.get('cognitive_score'),
            "score_breakdown": {
                "wait_score": sb.get('wait_score', 0),
                "token_score": sb.get('token_score', 0),
                "queue_score": sb.get('queue_score', 0),
                "active_score": sb.get('active_score', 0),
                "system_score": sb.get('system_score', 0),
                "processing_bonus": sb.get('processing_bonus', 0),
                "base_score": sb.get('base_score', data.get('cognitive_score', 0)),
                "final_score": sb.get('final_score', data.get('cognitive_score', 0)),
                "active_sessions": data.get('active_sessions', 0),
                "recent_active": data.get('active_sessions', 0),
                "tool_calls": 0,
                "pending": data.get('pending_count', 0),
                "processing": data.get('processing_count', 0),
                "estimated_response": data.get('estimated_wait', {}).get('seconds', 30)
            },
            "status_code": data.get('status_code'),
            "status_text": data.get('status_text'),
            "suggestion": data.get('suggestion'),
            "active_sessions": data.get('active_sessions', 0),
            "recent_active_count": data.get('active_sessions', 0),
            "total_tool_calls": 0,
            "pending_count": data.get('pending_count', 0),
            "processing_count": data.get('processing_count', 0),
            "github_workflows": data.get('github_workflows', 0),
            "local_builds": data.get('local_builds', 0),
            "total_tokens": data.get('total_tokens', 0),
            "total_tokens_formatted": f"{(data.get('total_tokens', 0) / 1000):.1f}k",
            "estimated_response": 30,
            "estimated_response_formatted": f"{30}s",
            "task_queue": formatted_tasks,
            "cpu_percent": data.get('cpu_percent', 0),
            "memory_percent": data.get('memory_percent', 0),
            "workflow_details": data.get('workflow_details', []),
            "build_details": data.get('build_details', [])
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[DATA_FILE ERROR] {e}")
        return False

def update_history_file(data):
    """v5.34: 追加历史数据到 JSON Lines 文件"""
    try:
        # 精简数据，只存储必要的走势数据
        history_record = {
            "timestamp": data.get('timestamp'),
            "score": data.get('cognitive_score', 0),
            "sessions": data.get('active_sessions', 0),
            "pending": data.get('pending_count', 0),
            "processing": data.get('processing_count', 0),
            "tokens": data.get('total_tokens', 0),
            "cpu": data.get('cpu_percent', 0),
            "memory": data.get('memory_percent', 0)
        }
        
        # 追加写入 JSON Lines
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(history_record, ensure_ascii=False) + '\n')
        
        # v5.37: 同时生成轻量趋势文件
        update_trend_data(history_record)
        
        return True
    except Exception as e:
        print(f"[HISTORY_FILE ERROR] {e}")
        return False

def update_trend_data(record):
    """v5.37: 生成轻量趋势文件，用于前端首次加载"""
    try:
        TREND_FILE = "/root/.openclaw/workspace/portfolio-blog/status-monitor/trend-data.json"
        
        # 读取现有趋势数据
        trend_data = []
        if os.path.exists(TREND_FILE):
            try:
                with open(TREND_FILE, 'r', encoding='utf-8') as f:
                    trend_data = json.load(f).get('points', [])
            except:
                trend_data = []
        
        # 添加新记录（转换时间格式）
        ts = record['timestamp']
        if isinstance(ts, str):
            ts_dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        else:
            ts_dt = datetime.now(timezone.utc)
        
        trend_point = {
            "t": ts_dt.strftime("%H:%M"),  # 简化时间格式
            "s": record['score'],
            "ts": record['timestamp']  # 完整时间戳用于去重
        }
        
        # 避免重复（检查最近一条）
        if trend_data and trend_data[-1].get('ts') == trend_point['ts']:
            return True
        
        trend_data.append(trend_point)
        
        # 只保留最近60条（约1小时数据）
        trend_data = trend_data[-60:]
        
        # 写入文件
        output = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(trend_data),
            "points": trend_data
        }
        
        with open(TREND_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"[TREND_DATA ERROR] {e}")
        return False

def cleanup_history_file():
    """v5.34: 清理过期历史数据（7天前的数据归档）"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return
        
        cutoff_time = time.time() - (HISTORY_RETENTION_DAYS * 24 * 3600)
        current_month = datetime.now().strftime("%Y-%m")
        archive_file = os.path.join(ARCHIVE_DIR, f"cognitive-{current_month}.jsonl")
        
        # 确保归档目录存在
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # 读取所有记录
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = []
        old_lines = []
        
        for line in lines:
            try:
                record = json.loads(line.strip())
                record_ts = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).timestamp()
                
                if record_ts > cutoff_time:
                    recent_lines.append(line)
                else:
                    old_lines.append(line)
            except:
                continue
        
        # 将过期数据归档
        if old_lines:
            with open(archive_file, 'a', encoding='utf-8') as f:
                f.writelines(old_lines)
            print(f"[HISTORY] 归档 {len(old_lines)} 条记录到 {archive_file}")
        
        # 重写历史文件（只保留最近7天）
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.writelines(recent_lines)
        
        return True
    except Exception as e:
        print(f"[HISTORY_CLEANUP ERROR] {e}")
        return False

def compress_old_archives():
    """v5.34: 压缩上月及更早的归档文件"""
    try:
        if not os.path.exists(ARCHIVE_DIR):
            return
        
        current_month = datetime.now().strftime("%Y-%m")
        import gzip
        
        for filename in os.listdir(ARCHIVE_DIR):
            if filename.endswith('.jsonl') and not filename.startswith(current_month):
                filepath = os.path.join(ARCHIVE_DIR, filename)
                gz_path = filepath + '.gz'
                
                # 如果已压缩则跳过
                if os.path.exists(gz_path):
                    continue
                
                # 压缩文件
                with open(filepath, 'rb') as f_in:
                    with gzip.open(gz_path, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                # 删除原文件
                os.remove(filepath)
                print(f"[ARCHIVE] 压缩 {filename} -> {filename}.gz")
        
        return True
    except Exception as e:
        print(f"[ARCHIVE_COMPRESS ERROR] {e}")
        return False

def get_history_data(hours=1, max_points=200):
    """v5.34: 获取指定时间范围的历史数据供前端使用"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return []
        
        cutoff_time = time.time() - (hours * 3600)
        records = []
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    record_ts = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')).timestamp()
                    
                    if record_ts > cutoff_time:
                        records.append(record)
                except:
                    continue
        
        # 如果数据点太多，进行采样
        if len(records) > max_points:
            step = len(records) // max_points
            records = records[::step]
        
        return records
    except Exception as e:
        print(f"[GET_HISTORY ERROR] {e}")
        return []


def main():
    """v6.0: 单次执行模式 - crontab 每分钟调用一次"""
    print("🧠 Shrimp Jetton v7.2 - 六大任务分类版 - 单次执行模式")
    
    try:
        load = get_cognitive_load()
        code, text, sug = determine_status(load['cognitive_score'])
        
        data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cognitive_score": load['cognitive_score'],
            "status_code": code,
            "status_text": text,
            "suggestion": sug,
            "active_sessions": load['active_sessions'],
            "pending_count": load['pending_count'],
            "processing_count": load['processing_count'],
            "github_workflows": load['github_workflows'],
            "local_builds": load['local_builds'],
            "max_wait_sec": load['max_wait_sec'],
            "total_tokens": load['total_tokens'],
            "total_tokens_formatted": f"{load['total_tokens']/1000:.1f}k" if load['total_tokens'] >= 1000 else str(load['total_tokens']),
            "last_active_sec": load['last_active_sec'],
            "task_queue": load['task_queue'],
            "cpu_percent": load['system']['cpu_percent'],
            "memory_percent": load['system']['memory_percent'],
            "estimated_wait": load.get('estimated_wait', {"text": "立即", "detail": "可立即响应"}),
            "workflow_details": load['workflow_details'],
            "build_details": load['build_details']
        }
        
        # v6.0: 写入数据仓库
        update_data_file(data)
        update_history_file(data)
        
        ts = datetime.now().strftime("%H:%M:%S")
        tasks = ", ".join([d['name'].split()[1] if ' ' in d['name'] else d['name'] 
                           for d in load['task_queue'][:3]])
        wf_info = f" | {load['github_workflows']} CI" if load['github_workflows'] > 0 else ""
        build_info = f" | {load['local_builds']} Build" if load['local_builds'] > 0 else ""
        print(f"[{ts}] {text} | Score:{load['cognitive_score']} | Queue:{load['processing_count']+load['pending_count']} | {tasks}{wf_info}{build_info}")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
