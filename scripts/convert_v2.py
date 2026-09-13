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

with open(MATH_TEMPLATE, 'r', encoding='utf-8') as f:
    math_html = f.read()

# ========== Extract template parts ==========
style_end = math_html.find('</style>')
math_css = math_html[:style_end + len('</style>')]

body_start = math_html.find('<body>')
first_card_marker = '<!-- ========== CHAPTER'
first_card_idx = math_html.find(first_card_marker)
before_cards = math_html[body_start:first_card_idx]

script_start = math_html.find('<script>')
script_end = math_html.find('</script>')
script_content = math_html[script_start:script_end + len('</script>')]
end_shell = math_html[script_end + len('</script>'):]

# ========== Helper: extract cards ==========
def extract_cards(html):
    cards = []
    for match in re.finditer(r'<div\s+class="card(?:\s+hidden)?"[^>]*id="(ch\d+)"', html):
        card_id = match.group(1)
        start = match.start()
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
                    cards.append((card_id, html[start:end]))
                    break
                pos = next_close + 6
    return cards

# ========== Helper: extract ALL CSS (no filtering) ==========
def extract_all_css(html):
    """Extract ALL <style> content, concatenated"""
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    return '\n\n'.join(s.strip() for s in styles if s.strip())

# ========== Helper: extract extra JS ==========
def extract_extra_js(html):
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
    backup_path = path + '.backup.' + ch_id
    
    if not os.path.exists(backup_path):
        print(f"⚠️ {ch_id}: backup not found, using current file")
        src_path = path
    else:
        src_path = backup_path
    
    with open(src_path, 'r', encoding='utf-8') as f:
        phys_html = f.read()
    
    # Extract cards
    cards = extract_cards(phys_html)
    print(f"{ch_id}: {len(cards)} cards found")
    
    if len(cards) == 0:
        print(f"  ⚠️ No cards found, skipping")
        continue
    
    # Extract ALL CSS from physical (no filtering!)
    phys_css = extract_all_css(phys_html)
    
    # Extract extra JS
    extra_js = extract_extra_js(phys_html)
    
    # Build CSS part: math template CSS + all physical CSS
    css_part = math_css.replace(
        '<title>数学特工局 · 特工手册 — 简单的代数式</title>',
        f'<title>{meta["title"]}</title>'
    )
    
    # Insert physical CSS BEFORE </style> (so it can override math CSS if needed)
    if phys_css:
        # Remove any duplicate CSS from physical that exactly matches math CSS
        # Simple dedup: if phys_css contains math_css body (without title), skip
        math_css_body = math_css[math_css.find('<style>') + len('<style>'):math_css.find('</style>')]
        phys_clean = phys_css
        if math_css_body in phys_css:
            phys_clean = phys_css.replace(math_css_body, '').strip()
        
        if phys_clean:
            css_part = css_part.replace('</style>', f'\n\n/* === Physics Chapter CSS === */\n{phys_clean}\n</style>')
    
    # Build before-cards (update title/subtitle/progress)
    before = before_cards.replace('<h1>📐 数学特工局</h1>', '<h1>📐 物理特工局</h1>')
    before = before.replace('特工手册 — 简单的代数式 · 代号：ALGEBRA · 六年级', meta['subtitle'])
    
    # Update progress bar
    before = re.sub(r'<div class="progress-seg"[^>]*>\s*</div>\s*', '', before)
    segments = '\n  '.join(['<div class="progress-seg"></div>'] * (meta['units'] - 1))
    before = before.replace(
        '<div class="progress-bar" id="progress-bar">',
        f'<div class="progress-bar" id="progress-bar">\n  <div class="progress-seg active"></div>\n  {segments}'
    )
    
    # Cards HTML
    cards_html = '\n\n'.join([card for _, card in cards])
    
    # Script
    script_part = script_content
    if extra_js:
        script_part = script_part.replace('</script>', f'\n\n/* === Chapter JS === */\n{extra_js}\n</script>')
    script_part = re.sub(r'const totalCh = \d+;', f'const totalCh = {meta["units"]};', script_part)
    
    # Assemble
    new_html = css_part + before + cards_html + '\n\n</div>\n\n' + script_part + end_shell
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"  ✅ Converted ({len(new_html)} chars)")

print("\n=== Done ===")
