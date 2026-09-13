import re, os, glob

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# ch00-ch06: 清理特工主题 + 调主题色
CH_THEME = {
    'grade8-sem1-ch00': '#00bbf9',  # 天蓝
    'grade8-sem1-ch01': '#00f0c8',  # 青绿
    'grade8-sem1-ch02': '#ff6b35',  # 橙色
    'grade8-sem1-ch03': '#00bbf9',  # 声波蓝
    'grade8-sem1-ch04': '#ffd166',  # 金黄
    'grade8-sem1-ch05': '#ef476f',  # 红色
    'grade8-sem2-ch06': '#00bbf9',  # 蓝色
}

def clean_agent_theme(path, theme_color):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    orig_len = len(html)
    
    # 1. 移除扫描线 body::before CSS
    html = re.sub(
        r'/\* Scanlines \*/\s*body::before\s*\{[^}]+\}',
        '/* Scanlines removed */',
        html, flags=re.DOTALL
    )
    
    # 2. 移除 HUD Grid CSS
    html = re.sub(
        r'/\* HUD Grid \*/\s*#hud-grid\s*\{[^}]+\}',
        '/* HUD Grid removed */',
        html, flags=re.DOTALL
    )
    
    # 3. 移除 Corners CSS
    html = re.sub(
        r'/\* Corners \*/\s*\.corner-tl[^}]+\}\s*\.corner-tr[^}]+\}\s*\.corner-bl[^}]+\}\s*\.corner-br[^}]+\}',
        '/* Corners removed */',
        html, flags=re.DOTALL
    )
    
    # 4. 移除 HTML中的 hud-grid div 和 corner divs
    html = re.sub(r'<div id="hud-grid"></div>\s*', '', html)
    html = re.sub(r'<div class="corner-tl"></div><div class="corner-tr"></div>\s*<div class="corner-bl"></div><div class="corner-br"></div>\s*', '', html)
    
    # 5. 替换主题色
    html = html.replace('--accent: #00f5d4;', f'--accent: {theme_color};')
    
    # 6. 替换标题中的特工文字
    html = html.replace('物理特工装备室', '物理实验室')
    html = html.replace('特工手册', '学习手册')
    html = html.replace('物理特工总部', '物理探索中心')
    html = html.replace('时空追踪局', '运动学实验室')
    html = html.replace('声波动能实验室', '声学实验室')
    html = html.replace('光子特遣队', '光学实验室')
    html = html.replace('动力学指挥部', '力学实验室')
    html = html.replace('材料实验室', '材料与压强实验室')
    
    new_len = len(html)
    removed = orig_len - new_len
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return removed

print("=== Cleaning ch00-ch06 agent themes ===")
for ch, color in CH_THEME.items():
    path = os.path.join(BASE, ch, 'tutorial.html')
    if os.path.exists(path):
        removed = clean_agent_theme(path, color)
        print(f"  {ch}: removed {removed} chars, theme -> {color}")
    else:
        print(f"  {ch}: file not found")

print("\nDone.")
