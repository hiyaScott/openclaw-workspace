import re, os, json

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'
REPORT = {}

# Chapter mapping
CHAPTERS = {
    'grade8-sem1-ch00': '序言 踏上物理学奇妙旅途',
    'grade8-sem1-ch01': '第一章 测量',
    'grade8-sem1-ch02': '第二章 机械运动',
    'grade8-sem1-ch03': '第三章 声现象',
    'grade8-sem1-ch04': '第四章 光现象',
    'grade8-sem1-ch05': '第五章 运动和力',
    'grade8-sem2-ch06': '第六章 密度与压强',
    'grade8-sem2-ch07': '第七章 浮力',
    'grade8-sem2-ch08': '第八章 简单机械功和能',
    'grade8-sem2-ch09': '第九章 物态变化',
    'grade9-sem1-ch10': '第十章 内能',
    'grade9-sem1-ch11': '第十一章 静电与电流',
    'grade9-sem1-ch12': '第十二章 欧姆定律',
    'grade9-sem1-ch13': '第十三章 电功率',
    'grade9-sem2-ch14': '第十四章 电与磁',
    'grade9-sem2-ch15': '第十五章 电磁波',
    'grade9-sem2-ch16': '第十六章 从原子到星系',
    'grade9-sem2-ch17': '第十七章 能源',
}

SPECS = {
    'grade8-sem1-ch00': '00bbf9',
    'grade8-sem1-ch01': '00f0c8',
    'grade8-sem1-ch02': 'ff6b35',
    'grade8-sem1-ch03': '00bbf9',
    'grade8-sem1-ch04': 'ffd166',
    'grade8-sem1-ch05': 'ef476f',
    'grade8-sem2-ch06': '00bbf9',
    'grade8-sem2-ch07': '00f5d4',
    'grade8-sem2-ch08': '06d6a0',
    'grade8-sem2-ch09': 'ff6b35',
    'grade9-sem1-ch10': '9d00ff',
    'grade9-sem1-ch11': '9d00ff',
    'grade9-sem1-ch12': '9d00ff',
    'grade9-sem1-ch13': '9d00ff',
    'grade9-sem2-ch14': '9d00ff',
    'grade9-sem2-ch15': '9d00ff',
    'grade9-sem2-ch16': '00f0c8',
    'grade9-sem2-ch17': 'ff6b35',
}

def check_chapter(ch_dir):
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    if not os.path.exists(path):
        return {'error': 'File not found'}
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    issues = []
    checks = {}
    
    # === 1. Layout Structure ===
    
    # 1.1 title-bar with text-align: center
    titlebar = re.search(r'text-align:\s*center', text)
    checks['title_bar_center'] = bool(titlebar)
    if not titlebar:
        issues.append("❌ title-bar 未居中 (缺少 text-align: center)")
    
    # 1.2 h1 font-size and letter-spacing
    h1_css = re.search(r'\.title-bar\s+h1\s*\{[^}]*\}', text, re.DOTALL) or re.search(r'h1\s*\{[^}]*\}', text, re.DOTALL)
    if h1_css:
        h1_text = h1_css.group(0)
        has_32px = '32px' in h1_text or '2rem' in h1_text
        has_ls4 = 'letter-spacing' in h1_text
        checks['h1_style'] = has_32px and has_ls4
        if not has_32px:
            issues.append("❌ h1 缺少 font-size: 32px")
        if not has_ls4:
            issues.append("❌ h1 缺少 letter-spacing")
    else:
        checks['h1_style'] = False
        issues.append("❌ 未找到 h1 CSS 定义")
    
    # 1.3 Challenge button inside title-bar
    # Find title-bar or header section, check if challenge button is inside
    header_end = text.find('</header>') if '<header>' in text else text.find('</div><!-- title-bar -->') if '<!-- title-bar -->' in text else text.find('class="progress-bar"')
    if header_end > 0:
        header_section = text[:header_end]
        challenge_in_header = '挑战' in header_section or '去挑战' in header_section or 'index.html' in header_section
        checks['challenge_in_titlebar'] = challenge_in_header
        if not challenge_in_header:
            issues.append("❌ 挑战按钮不在 title-bar/header 内部")
    
    # 1.4 .card.hidden CSS
    hidden_css = '.card.hidden { display: none; }' in text or '.card.hidden' in text
    checks['card_hidden_css'] = hidden_css
    if not hidden_css:
        issues.append("❌ 缺少 .card.hidden CSS 定义")
    
    # === 2. Navigation ===
    
    # 2.1 goTo function
    goto = re.search(r'function goTo\(n\)', text)
    checks['has_goto'] = bool(goto)
    if not goto:
        issues.append("❌ 缺少 goTo(n) 函数")
    else:
        goto_fn = re.search(r'function goTo\(n\).*?\}', text, re.DOTALL)
        if goto_fn:
            goto_text = goto_fn.group(0)
            has_hidden_toggle = 'hidden' in goto_text
            has_scroll = 'scrollTo' in goto_text or 'scroll' in goto_text
            checks['goto_complete'] = has_hidden_toggle and has_scroll
            if not has_hidden_toggle:
                issues.append("❌ goTo 函数未操作 .hidden 类")
            if not has_scroll:
                issues.append("❌ goTo 函数未调用 scrollTo")
    
    # 2.2 updateProgress function
    updateprog = 'function updateProgress' in text
    checks['has_updateprogress'] = updateprog
    if not updateprog:
        issues.append("❌ 缺少 updateProgress() 函数")
    else:
        # Check if goTo calls updateProgress
        if goto:
            goto_fn = re.search(r'function goTo\(n\).*?\}', text, re.DOTALL)
            if goto_fn and 'updateProgress' not in goto_fn.group(0):
                issues.append("❌ goTo 函数未调用 updateProgress()")
    
    # === 3. Progress Bar ===
    
    # Count top-level units
    top_cards = re.findall(r'<div\s+class="card(?:\s+hidden)?"\s+id="ch\d+"', text)
    unit_count = len(top_cards)
    checks['unit_count'] = unit_count
    
    if unit_count < 4:
        issues.append(f"❌ 单元数仅 {unit_count}，少于4个")
    elif unit_count > 7:
        issues.append(f"❌ 单元数 {unit_count}，超过7个")
    
    # Count progress segments
    progress_match = re.search(r'<div class="progress-bar"[^>]*>(.*?)</div>', text, re.DOTALL)
    if progress_match:
        seg_count = len(re.findall(r'progress-seg', progress_match.group(1)))
        checks['progress_segments'] = seg_count
        if seg_count != unit_count:
            issues.append(f"❌ 进度条 {seg_count} 段 ≠ 单元数 {unit_count}")
    else:
        checks['progress_segments'] = 0
        issues.append("❌ 未找到进度条")
    
    # === 4. Content Quality ===
    
    # 4.1 Count SVG experiments (SMIL animate tags inside svg)
    svg_blocks = re.findall(r'<svg.*?</svg>', text, re.DOTALL)
    svg_count = len(svg_blocks)
    checks['svg_count'] = svg_count
    
    # Check for SMIL animation in SVGs
    smil_count = text.count('<animate')
    checks['smil_count'] = smil_count
    
    # 4.2 Count examples (example-item or similar)
    examples = re.findall(r'class="example-item"', text)
    example_count = len(examples)
    checks['example_count'] = example_count
    
    # 4.3 Count quiz/test items
    quiz_items = re.findall(r'class="quiz-(item|question|num|number)"', text)
    quiz_count = len(quiz_items)
    checks['quiz_count'] = quiz_count
    
    # 4.4 Check for trap questions (look for keywords like 陷阱, 易错, 小心)
    trap_keywords = ['陷阱', '易错', '小心', '常见错误', '误区']
    trap_count = sum(text.count(kw) for kw in trap_keywords)
    checks['trap_count'] = trap_count
    
    # 4.5 Feedback ID uniqueness
    fb_ids = re.findall(r'id="(fb\d+-\d+)"', text)
    unique_fbs = set(fb_ids)
    checks['fb_unique'] = len(fb_ids) == len(unique_fbs)
    if len(fb_ids) != len(unique_fbs):
        issues.append(f"❌ Feedback ID 重复: {len(fb_ids)} 总, {len(unique_fbs)} 唯一")
    checks['fb_count'] = len(fb_ids)
    
    # === 5. Special checks for section-based chapters ===
    
    sections = re.findall(r'<section\s+id="sec-[^"]+"', text)
    if sections:
        checks['is_section_based'] = True
        checks['section_count'] = len(sections)
        # Check showModule or equivalent
        has_showmodule = 'showModule' in text
        checks['has_showmodule'] = has_showmodule
        if not has_showmodule:
            issues.append("❌ section-based 章节缺少 showModule 导航")
    else:
        checks['is_section_based'] = False
    
    # === 6. Color theme ===
    
    expected_color = SPECS.get(ch_dir, '9d00ff')
    color_in_css = expected_color in text
    checks['theme_color'] = color_in_css
    if not color_in_css:
        issues.append(f"⚠️ 未检测到主题色 #{expected_color}")
    
    return {
        'checks': checks,
        'issues': issues,
        'ok': len(issues) == 0
    }

# Run checks
print("=" * 70)
print("物理课件统一规范检查报告")
print("=" * 70)
print()

all_ok = True
for ch_dir, name in CHAPTERS.items():
    result = check_chapter(ch_dir)
    REPORT[ch_dir] = result
    
    checks = result['checks']
    issues = result['issues']
    
    status = "✅" if result['ok'] else "❌"
    print(f"{status} {name} ({ch_dir})")
    print(f"   单元数: {checks.get('unit_count', 'N/A')} | SVG实验: {checks.get('svg_count', 0)} | 例题: {checks.get('example_count', 0)} | 测试题: {checks.get('quiz_count', 0)}")
    print(f"   进度条: {checks.get('progress_segments', 'N/A')}段 | goTo: {'✓' if checks.get('has_goto') else '✗'} | updateProgress: {'✓' if checks.get('has_updateprogress') else '✗'}")
    print(f"   title-bar居中: {'✓' if checks.get('title_bar_center') else '✗'} | 挑战按钮位置: {'✓' if checks.get('challenge_in_titlebar') else '✗'} | card.hidden: {'✓' if checks.get('card_hidden_css') else '✗'}")
    print(f"   Feedback唯一: {'✓' if checks.get('fb_unique') else '✗'}({checks.get('fb_count',0)}个) | 陷阱题关键词: {checks.get('trap_count',0)}次 | Section模式: {'✓' if checks.get('is_section_based') else '✗'}")
    
    if issues:
        for issue in issues:
            print(f"   → {issue}")
        all_ok = False
    print()

# Summary
print("=" * 70)
print("汇总")
print("=" * 70)
total = len(CHAPTERS)
ok_count = sum(1 for r in REPORT.values() if r['ok'])
print(f"通过: {ok_count}/{total}")
print(f"有问题: {total - ok_count}/{total}")
if not all_ok:
    print("\n需要修复的章节:")
    for ch_dir, name in CHAPTERS.items():
        if not REPORT[ch_dir]['ok']:
            print(f"  - {name}: {len(REPORT[ch_dir]['issues'])} 个问题")
