import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'
MATH_TEMPLATE = '/root/.openclaw/workspace/portfolio-blog/research/junior-math/courseware-math/grade6-sem1-ch02/tutorial.html'

CHAPTERS = {
    'grade8-sem1-ch00': {'title': '声波分析中心 · 学习手册 — 声', 'subtitle': '沪科版八年级 · 序言 · 学习手册', 'units': 4},
    'grade8-sem1-ch01': {'title': '第一章 测量 · 物理基础实验室', 'subtitle': '沪科版八年级第一学期 · 第一章 · 学习手册', 'units': 4},
    'grade8-sem1-ch02': {'title': '第二章 机械运动 · 物理基础实验室', 'subtitle': '沪科版八年级第一学期 · 第二章 · 学习手册', 'units': 4},
    'grade8-sem1-ch03': {'title': '声波分析中心 · 学习手册 — 声', 'subtitle': '沪科版八年级第一学期 · 第三章 · 学习手册', 'units': 3},
    'grade8-sem1-ch04': {'title': '第四章 光现象 · 光学实验室', 'subtitle': '沪科版八年级第一学期 · 第四章 · 学习手册', 'units': 5},
    'grade8-sem1-ch05': {'title': '第五章 运动和力 · 力学实验室', 'subtitle': '沪科版八年级第一学期 · 第五章 · 学习手册', 'units': 6},
    'grade8-sem2-ch06': {'title': '第六章 密度与压强 · 流体力学实验室', 'subtitle': '沪科版八年级第二学期 · 第六章 · 学习手册', 'units': 7},
    'grade8-sem2-ch07': {'title': '第七章 浮力 · 流体动力学实验室', 'subtitle': '沪科版八年级第二学期 · 第七章 · 学习手册', 'units': 6},
    'grade8-sem2-ch08': {'title': '第八章 简单机械 · 机械实验室', 'subtitle': '沪科版八年级第二学期 · 第八章 · 学习手册', 'units': 7},
    'grade8-sem2-ch09': {'title': '第九章 物态变化 · 热学实验室', 'subtitle': '沪科版八年级第二学期 · 第九章 · 学习手册', 'units': 7},
    'grade9-sem1-ch10': {'title': '第十章 内能 — 热力学实验室', 'subtitle': '沪科版九年级第一学期 · 第十章 · 学习手册', 'units': 7},
    'grade9-sem1-ch11': {'title': '第十一章 静电与电流 · 电路实验室', 'subtitle': '沪科版九年级第一学期 · 第十一章 · 学习手册', 'units': 7},
    'grade9-sem1-ch12': {'title': '第十二章 欧姆定律 · 电学实验室', 'subtitle': '沪科版九年级第一学期 · 第十二章 · 学习手册', 'units': 7},
    'grade9-sem1-ch13': {'title': '第十三章 电功与电功率 · 电力实验室', 'subtitle': '沪科版九年级第一学期 · 第十三章 · 学习手册', 'units': 7},
    'grade9-sem2-ch14': {'title': '第十四章 电与磁 · 电磁实验室', 'subtitle': '沪科版九年级第二学期 · 第十四章 · 学习手册', 'units': 7},
    'grade9-sem2-ch15': {'title': '第十五章 电磁波 · 通信实验室', 'subtitle': '沪科版九年级第二学期 · 第十五章 · 学习手册', 'units': 7},
    'grade9-sem2-ch16': {'title': '第十六章 从原子到星系 · 宇宙实验室', 'subtitle': '沪科版九年级第二学期 · 第十六章 · 学习手册', 'units': 7},
    'grade9-sem2-ch17': {'title': '第十七章 能源 · 能源实验室', 'subtitle': '沪科版九年级第二学期 · 第十七章 · 学习手册', 'units': 7},
}

# ========== Extract template parts ==========
with open(MATH_TEMPLATE, 'r', encoding='utf-8') as f:
    math_html = f.read()

# Extract CSS shell (from <head> to </style>)
style_end = math_html.find('</style>')
css_shell = math_html[:style_end + len('</style>')]

# Extract body shell (from <body> to first card)
body_start = math_html.find('<body>')
first_card_marker = '<!-- ========== CHAPTER'
first_card_idx = math_html.find(first_card_marker)
before_cards = math_html[body_start:first_card_idx]

# Extract after-cards shell (from last </div> before script)
script_start = math_html.find('<script>')
after_cards = math_html[script_start:]

# Extract standard script
script_end = math_html.find('</script>')
script_content = math_html[script_start:script_end + len('</script>')]

# End shell (after script)
end_shell = math_html[script_end + len('</script>'):]

print("=== Template parts extracted ===")
print(f"CSS shell: {len(css_shell)} chars")
print(f"Before cards: {len(before_cards)} chars")
print(f"Script: {len(script_content)} chars")
print(f"End shell: {len(end_shell)} chars")

# ========== Helper: extract card content using stack ==========
def extract_cards(html):
    """Extract all <div class="card" id="chX"> blocks"""
    cards = []
    
    # Find all card start positions (exact match, not card-header)
    for match in re.finditer(r'<div\s+class="card(?:\s+hidden)?"[^>]*id="(ch\d+)"', html):
        card_id = match.group(1)
        start = match.start()
        
        # Find matching </div> using stack
        pos = html.find('>', start) + 1
        depth = 1
        while depth > 0 and pos < len(html):
            next_open = html.find('<div', pos)
            next_close = html.find('</div>', pos)
            
            if next_close == -1:
                break
            
            if next_open != -1 and next_open < next_close:
                depth += 1
                pos = next_open + 4
            else:
                depth -= 1
                if depth == 0:
                    end = next_close + len('</div>')
                    card_html = html[start:end]
                    cards.append((card_id, card_html))
                    break
                pos = next_close + 6
    
    return cards

# ========== Helper: extract extra CSS ==========
def extract_extra_css(html):
    """Extract CSS rules not in math template"""
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    extra_css = []
    for style in styles:
        # Skip if it's the main template CSS
        if any(s in style for s in ['#hud-grid', '.corner-tl', '.title-bar', '.progress-bar']):
            continue
        if not style.strip():
            continue
        extra_css.append(style.strip())
    return '\n'.join(extra_css)

# ========== Helper: extract extra JS ==========
def extract_extra_js(html):
    """Extract JS functions not in math template"""
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    extra_js = []
    for script in scripts:
        if 'function goTo(' in script and 'function updateProgress(' in script:
            continue
        if not script.strip():
            continue
        extra_js.append(script.strip())
    return '\n\n'.join(extra_js)

# ========== Process each chapter ==========
for ch_id, meta in CHAPTERS.items():
    path = os.path.join(BASE, ch_id, 'tutorial.html')
    if not os.path.exists(path):
        print(f"⚠️ {ch_id}: file not found")
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        phys_html = f.read()
    
    # Extract cards
    cards = extract_cards(phys_html)
    print(f"{ch_id}: {len(cards)} cards found")
    
    if len(cards) == 0:
        print(f"  ⚠️ No cards found, skipping")
        continue
    
    # Extract extra CSS
    extra_css = extract_extra_css(phys_html)
    
    # Extract extra JS
    extra_js = extract_extra_js(phys_html)
    
    # Build new HTML
    # 1. Title
    new_title = f'<title>{meta["title"]}</title>'
    
    # 2. CSS shell + extra CSS
    css_part = css_shell.replace(
        '<title>数学特工局 · 特工手册 — 简单的代数式</title>',
        new_title
    )
    
    if extra_css:
        css_part = css_part.replace('</style>', f'\n/* === Chapter-specific CSS === */\n{extra_css}\n</style>')
    
    # 3. Before cards (with updated title/subtitle/progress)
    before = before_cards.replace(
        '<h1>📐 数学特工局</h1>',
        '<h1>📐 物理特工局</h1>'
    )
    before = before.replace(
        '特工手册 — 简单的代数式 · 代号：ALGEBRA · 六年级',
        meta['subtitle']
    )
    
    # Update progress bar
    before = re.sub(r'<div class="progress-seg"[^>]*>\s*</div>\s*', '', before)
    segments = '\n  '.join(['<div class="progress-seg"></div>'] * (meta['units'] - 1))
    before = before.replace(
        '<div class="progress-bar" id="progress-bar">',
        f'<div class="progress-bar" id="progress-bar">\n  <div class="progress-seg active"></div>\n  {segments}'
    )
    
    # 4. Cards
    cards_html = '\n\n'.join([card for _, card in cards])
    
    # 5. Script + extra JS
    script_part = script_content
    if extra_js:
        script_part = script_part.replace(
            '</script>',
            f'\n\n/* === Chapter-specific JS === */\n{extra_js}\n</script>'
        )
    
    script_part = re.sub(
        r'const totalCh = \d+;',
        f'const totalCh = {meta["units"]};',
        script_part
    )
    
    # Assemble
    new_html = css_part + before + cards_html + '\n\n</div>\n\n' + script_part + end_shell
    
    # Write
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"  ✅ Converted")

print("\n=== Done ===")
