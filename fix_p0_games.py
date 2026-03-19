#!/usr/bin/env python3
"""
P0修复脚本：为游戏页面添加返回按钮和SEO元数据
"""

import os
import re
from pathlib import Path

# 深空风格的返回按钮CSS
BACK_BUTTON_CSS = '''
        /* 返回按钮 - 深空风格 */
        .back-nav {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }
        .back-nav a {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: rgba(10, 10, 26, 0.9);
            border: 2px solid #00ffff;
            border-radius: 25px;
            color: #00ffff;
            text-decoration: none;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            font-weight: 600;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(0, 255, 255, 0.1);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        .back-nav a:hover {
            background: rgba(0, 255, 255, 0.2);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), inset 0 0 15px rgba(0, 255, 255, 0.2);
            transform: translateX(-3px);
        }
        .back-nav a::before {
            content: '←';
            font-size: 16px;
        }
'''

# 返回按钮HTML
BACK_BUTTON_HTML = '''
    <nav class="back-nav">
        <a href="../../index.html">返回主页</a>
    </nav>
'''

def get_game_description(game_name):
    """根据游戏名返回描述"""
    descriptions = {
        'card-alchemist': '元素卡牌合成战斗游戏，通过合成不同元素卡牌来对抗敌人',
        'gravity-slingshot': '重力弹射游戏，利用重力场将飞船弹射到目标位置',
        'color-symphony': '色彩交响乐 - 颜色匹配音乐节奏游戏',
        'chain-reaction': '连锁反应 - 策略解谜游戏，引发连锁爆炸清除目标',
        'pixel-painter': '像素画家 - 创意像素绘画工具',
        'sonic-maze': '声波迷宫 - 利用回声定位探索迷宫',
        'neon-defense': '霓虹防线 - 赛博朋克风格塔防游戏',
        'word-alchemy': '文字炼金术 - 文字解谜与组合游戏',
        'rhythm-parkour': '节奏跑酷 - 音乐节奏动作游戏',
        'shape-shifter': '形态转换 - 几何变形解谜游戏',
        'rhythm-commander': '节奏指挥官 - 音乐节拍策略游戏',
        'word-alchemy-2': '文字炼金术2 - 升级版文字解谜游戏',
        'gravity-flip': '重力翻转 - 重力操控平台跳跃游戏',
        'six-finger-midi': '六指MIDI - 多轨音乐创作工具',
        'mirror-maze': '镜像迷宫 - 镜面反射解谜游戏',
        'snake': '经典贪吃蛇 - 复古风格蛇形移动游戏',
        'circuit-connect': '电路连接 - 电子工程解谜游戏',
        'thermal-expansion': '热胀冷缩 - 物理模拟解谜游戏',
        'minesweeper': '经典扫雷 - 数字推理游戏',
        'wave-warrior': '波动战士 - 波形战斗游戏',
        'chroma-blaster': '色彩爆破 - 颜色匹配射击游戏',
        'who-is-spy': '谁是卧底 - 社交推理游戏',
        'time-rewind': '时间回溯 - 时间操控解谜游戏',
        'mama-counter': '妈妈计数器 - 趣味计数工具',
        'memory-maze': '记忆迷宫 - 记忆力挑战游戏',
        'shadow-puzzle': '影子谜题 - 光影解谜游戏',
        'quantum-split': '量子分裂 - 量子物理概念游戏',
        'aircraft-war': '飞机大战 - 经典射击游戏',
        'time-slice': '时间切片 - 时间操控策略游戏',
        'magnetic-snap': '磁力吸附 - 物理益智游戏',
        'bot-coder': '编程机器人 - 代码解谜游戏',
    }
    return descriptions.get(game_name, '一款精心设计的互动游戏作品')

def process_game_html(file_path):
    """处理游戏HTML文件，添加返回按钮和SEO"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有返回按钮
    if 'back-nav' in content or '返回主页' in content:
        print(f"  跳过(已有返回按钮): {file_path}")
        return False
    
    # 获取游戏名称
    game_dir = Path(file_path).parent.name
    game_desc = get_game_description(game_dir)
    
    # 从title提取游戏名称
    title_match = re.search(r'<title>(.*?)</title>', content)
    game_title = title_match.group(1) if title_match else game_dir
    
    # 构建SEO元数据
    seo_meta = f'''    <meta name="description" content="{game_title} - {game_desc} | Shrimp Jetton (Jetton) 的游戏作品集">
    <meta name="keywords" content="游戏设计, 交互设计, Shrimp Jetton, {game_title}">
    <meta property="og:title" content="{game_title} | 虾折腾">
    <meta property="og:description" content="{game_desc} - Shrimp Jetton的互动游戏作品">
    <link rel="canonical" href="https://hiyascott.github.io/scott-portfolio/games/{game_dir}/">
'''
    
    # 添加favicon（如果缺少）
    if 'favicon' not in content:
        favicon_link = '    <link rel="icon" type="image/svg+xml" href="../../favicon.svg">\n    <link rel="alternate icon" type="image/x-icon" href="../../favicon.ico">\n'
        # 在 </head> 前添加
        content = re.sub(r'(</head>)', favicon_link + r'\1', content, flags=re.IGNORECASE)
    
    # 添加SEO元数据（在 </head> 前）
    if 'property="og:title"' not in content:
        content = re.sub(r'(</head>)', seo_meta + r'\1', content, flags=re.IGNORECASE)
    
    # 添加CSS到<style>标签内
    if '<style>' in content and 'back-nav' not in content:
        content = content.replace('<style>', '<style>' + BACK_BUTTON_CSS)
    elif 'back-nav' not in content:
        # 没有style标签，在</head>前添加
        style_block = '<style>' + BACK_BUTTON_CSS + '    </style>\n'
        content = re.sub(r'(</head>)', style_block + r'\1', content, flags=re.IGNORECASE)
    
    # 添加返回按钮HTML（在<body>后）
    if 'back-nav' not in content:
        content = re.sub(r'(<body[^>]*>)', r'\1' + BACK_BUTTON_HTML, content, flags=re.IGNORECASE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  已更新: {file_path}")
    return True

def main():
    games_dir = Path('portfolio-blog/games')
    if not games_dir.exists():
        print(f"错误: 找不到目录 {games_dir}")
        return
    
    updated = 0
    skipped = 0
    
    # 遍历所有游戏目录
    for game_dir in games_dir.iterdir():
        if game_dir.is_dir() and game_dir.name != 'index.html':
            index_file = game_dir / 'index.html'
            if index_file.exists():
                if process_game_html(str(index_file)):
                    updated += 1
                else:
                    skipped += 1
    
    print(f"\n完成! 更新了 {updated} 个文件, 跳过了 {skipped} 个文件")

if __name__ == '__main__':
    main()
