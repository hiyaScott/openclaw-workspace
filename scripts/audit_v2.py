import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

CHAPTERS = {
    'grade8-sem1-ch00': '序言',
    'grade8-sem1-ch01': 'ch01 测量',
    'grade8-sem1-ch02': 'ch02 机械运动',
    'grade8-sem1-ch03': 'ch03 声现象',
    'grade8-sem1-ch04': 'ch04 光现象',
    'grade8-sem1-ch05': 'ch05 运动和力',
    'grade8-sem2-ch06': 'ch06 密度与压强',
    'grade8-sem2-ch07': 'ch07 浮力',
    'grade8-sem2-ch08': 'ch08 简单机械',
    'grade8-sem2-ch09': 'ch09 物态变化',
    'grade9-sem1-ch10': 'ch10 内能',
    'grade9-sem1-ch11': 'ch11 静电与电流',
    'grade9-sem1-ch12': 'ch12 欧姆定律',
    'grade9-sem1-ch13': 'ch13 电功率',
    'grade9-sem2-ch14': 'ch14 电与磁',
    'grade9-sem2-ch15': 'ch15 电磁波',
    'grade9-sem2-ch16': 'ch16 从原子到星系',
    'grade9-sem2-ch17': 'ch17 能源',
}

def audit(ch_dir):
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    issues = []
    
    # === 1. Progress bar segments (use balanced matching) ===
    # Find <div class="progress-bar" ...> with balanced divs
    pb_start = text.find('<div class="progress-bar"')
    if pb_start >= 0:
        # Find matching </div> by counting
        depth = 0
        i = pb_start
        while i < len(text):
            if text[i:i+4] == '<div':
                depth += 1
            elif text[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    pb_html = text[pb_start:i+6]
                    break
            i += 1
        else:
            pb_html = ''
        seg_count = pb_html.count('progress-seg')
    else:
        seg_count = 0
    
    # === 2. Unit count ===
    # Method A: id="chN" top-level cards
    top_cards = re.findall(r'<div\s+class="card(?:\s+hidden)?"\s+id="ch\d+"', text)
    # Method B: section-based with id="sec-"
    sections = re.findall(r'<section\s+id="sec-[^"]+"', text)
    # Method C: data-sec attribute cards
    data_sec_cards = re.findall(r'<div\s+class="card\s+section"\s+data-sec="\d+"', text)
    # Method D: section.module
    mod_sections = re.findall(r'<section\s+class="module"', text)
    # Exclude appendix/error sections from count
    mod_ids = re.findall(r'<section\s+class="module"\s+id="([^"]+)"', text)
    mod_count = sum(1 for mid in mod_ids if mid not in ['error', 'appendix'])
    if not mod_count and mod_sections:
        mod_count = len(mod_sections)  # fallback if no id attr
    
    if top_cards:
        unit_count = len(top_cards)
        nav_mode = 'card'
    elif sections:
        unit_count = len(sections)
        nav_mode = 'section'
    elif data_sec_cards:
        unit_count = len(data_sec_cards)
        nav_mode = 'data-sec'
    elif mod_sections:
        unit_count = mod_count if mod_count else len(mod_sections)
        nav_mode = 'module-section'
    else:
        # Try to find other patterns
        other = re.findall(r'<div\s+class="(?:card|module)[^"]*"\s+id="[^"]*"', text)
        unit_count = len(other)
        nav_mode = 'other'
    
    # === 3. Check goTo vs showModule ===
    has_goto = 'function goTo' in text
    has_showmodule = 'function showModule' in text or 'showModule(' in text
    
    # === 4. Check updateProgress ===
    has_update = 'function updateProgress' in text
    
    # === 5. Check .card.hidden CSS ===
    has_hidden_css = re.search(r'\.card\.hidden\s*\{[^}]*display[^}]*\}', text) is not None or '.card.hidden { display: none; }' in text
    
    # === 6. Check title-bar center ===
    has_center = ('text-align: center' in text or 'text-align:center' in text) and ('title-bar' in text or 'header' in text or '.header' in text)
    
    # === 7. Check h1 style ===
    h1_patterns = [
        r'\.title-bar\s+h1',
        r'header\s+h1',
        r'\.hero\s+h1',
        r'\.chapter-title',
        r'\.header-title',
        r'^\s*h1\s*\{',
    ]
    h1_match = None
    for pat in h1_patterns:
        h1_match = re.search(pat + r'\s*\{([^}]*)\}', text, re.DOTALL | re.MULTILINE)
        if h1_match:
            break
    if h1_match:
        h1_css = h1_match.group(1)
        h1_ok = 'font-size' in h1_css and ('32' in h1_css or '2rem' in h1_css)
        h1_ok = h1_ok and ('letter-spacing' in h1_css)
    else:
        # Fallback: just check if 32px and letter-spacing: 4px exist somewhere in first 5000 chars
        h1_ok = ('32px' in text[:5000] or '2rem' in text[:5000]) and ('letter-spacing: 4px' in text[:5000] or 'letter-spacing:4px' in text[:5000])
    
    # === 8. Challenge button inside header/titlebar ===
    header_end = max(text.find('</header>'), text.find('</div><!-- title-bar -->')) if ('</header>' in text or '<!-- title-bar -->' in text) else text.find('<div class="progress-bar"')
    if header_end > 0:
        header_area = text[:header_end]
        has_challenge = 'index.html' in header_area and '挑战' in header_area or 'index.html' in header_area and ('btn' in header_area or 'button' in header_area)
    else:
        has_challenge = False
    
    # === Validate ===
    if seg_count != unit_count:
        issues.append(f"进度条 {seg_count} 段 ≠ 单元数 {unit_count}")
    
    if nav_mode == 'card':
        if not has_goto:
            issues.append("缺少 goTo 函数")
        if not has_hidden_css:
            issues.append("缺少 .card.hidden CSS")
    elif nav_mode == 'section' or nav_mode == 'module-section':
        if not has_showmodule:
            issues.append("section-based 缺少 showModule")
    elif nav_mode == 'data-sec':
        if not has_goto:
            issues.append("data-sec 缺少 goTo")
        if not has_hidden_css:
            issues.append("缺少 .card.hidden CSS")
    
    if has_goto and not has_update:
        issues.append("goTo 存在但缺少 updateProgress")
    
    if unit_count < 2:
        issues.append(f"单元数仅 {unit_count}，少于2个")
    if unit_count > 9:
        issues.append(f"单元数 {unit_count}，超过9个")
    
    if not has_center:
        issues.append("title-bar 未居中")
    if not has_challenge:
        issues.append("挑战按钮位置不正确")
    if not h1_ok:
        issues.append("h1 样式不正确")
    
    return {
        'nav_mode': nav_mode,
        'units': unit_count,
        'segs': seg_count,
        'goto': has_goto,
        'showmod': has_showmodule,
        'update': has_update,
        'hidden_css': has_hidden_css,
        'center': has_center,
        'challenge': has_challenge,
        'h1': h1_ok,
        'issues': issues,
    }

print("=" * 75)
print("物理课件统一规范检查报告 v2")
print("=" * 75)
print()

all_ok = True
for ch_dir, name in CHAPTERS.items():
    r = audit(ch_dir)
    status = "✅" if len(r['issues']) == 0 else "❌"
    mode = r['nav_mode']
    print(f"{status} {name} ({ch_dir}) [{mode}]")
    print(f"   单元: {r['units']} | 进度条: {r['segs']}段 | goTo: {'✓' if r['goto'] else '✗'} | showModule: {'✓' if r['showmod'] else '✗'} | updateProgress: {'✓' if r['update'] else '✗'}")
    print(f"   居中: {'✓' if r['center'] else '✗'} | 挑战按钮: {'✓' if r['challenge'] else '✗'} | h1样式: {'✓' if r['h1'] else '✗'} | card.hidden: {'✓' if r['hidden_css'] else '✗'}")
    for issue in r['issues']:
        print(f"   → {issue}")
    if r['issues']:
        all_ok = False
    print()

ok_count = sum(1 for ch_dir in CHAPTERS if len(audit(ch_dir)['issues']) == 0)
print("=" * 75)
print(f"通过: {ok_count}/{len(CHAPTERS)}")
if not all_ok:
    print("\n需修复章节:")
    for ch_dir, name in CHAPTERS.items():
        r = audit(ch_dir)
        if r['issues']:
            print(f"  {name}: {len(r['issues'])} 项")
