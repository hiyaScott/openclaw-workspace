import re, os, sys

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# Chapter mapping
CHAPTERS = {
    'grade8-sem1-ch00': {'name':'序言','color':'#00bbf9','units':4},
    'grade8-sem1-ch01': {'name':'第一章 测量','color':'#00f0c8','units':4},
    'grade8-sem1-ch02': {'name':'第二章 机械运动','color':'#ff6b35','units':4},
    'grade8-sem1-ch03': {'name':'第三章 声现象','color':'#00bbf9','units':3}, # 需要处理
    'grade8-sem1-ch04': {'name':'第四章 光现象','color':'#ffd166','units':None}, # data-sec结构
    'grade8-sem1-ch05': {'name':'第五章 运动和力','color':'#ef476f','units':None}, # data-sec结构
    'grade8-sem2-ch06': {'name':'第六章 密度与压强','color':'#00bbf9','units':7},
    'grade8-sem2-ch07': {'name':'第七章 浮力','color':'#00f5d4','units':6},
    'grade8-sem2-ch08': {'name':'第八章 简单机械功和能','color':'#06d6a0','units':7},
    'grade8-sem2-ch09': {'name':'第九章 物态变化','color':'#ff6b35','units':None}, # section-based
    'grade9-sem1-ch10': {'name':'第十章 内能','color':'#9d00ff','units':7},
    'grade9-sem1-ch11': {'name':'第十一章 静电与电流','color':'#9d00ff','units':7},
    'grade9-sem1-ch12': {'name':'第十二章 欧姆定律','color':'#9d00ff','units':7},
    'grade9-sem1-ch13': {'name':'第十三章 电功率','color':'#9d00ff','units':7},
    'grade9-sem2-ch14': {'name':'第十四章 电与磁','color':'#9d00ff','units':7},
    'grade9-sem2-ch15': {'name':'第十五章 电磁波','color':'#9d00ff','units':7},
    'grade9-sem2-ch16': {'name':'第十六章 从原子到星系','color':'#00f0c8','units':7},
    'grade9-sem2-ch17': {'name':'第十七章 能源','color':'#ff6b35','units':7},
}

def fix_chapter(ch_dir):
    """Apply fixes to a chapter. Returns list of changes made."""
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    if not os.path.exists(path):
        return ['File not found']
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    changes = []
    cfg = CHAPTERS[ch_dir]
    
    # === FIX 1: Add .card.hidden CSS if missing and if card structure exists ===
    has_card_hidden = '.card.hidden' in text
    has_cards = bool(re.search(r'class="card(?:\s+hidden)?"', text))
    
    if not has_card_hidden and has_cards and ch_dir not in ['grade8-sem1-ch04','grade8-sem1-ch05','grade8-sem2-ch09']:
        # Find where to insert: after .card CSS block
        card_css = re.search(r'(\.card\s*\{[^}]*\})', text, re.DOTALL)
        if card_css:
            insert_pos = card_css.end()
            text = text[:insert_pos] + '\n\n.card.hidden { display: none; }' + text[insert_pos:]
            changes.append('Added .card.hidden CSS')
        else:
            # Insert before </style>
            style_end = text.find('</style>')
            if style_end > 0:
                text = text[:style_end] + '\n\n.card.hidden { display: none; }\n' + text[style_end:]
                changes.append('Added .card.hidden CSS (before </style>)')
    
    # === FIX 2: Challenge button position ===
    # Check if challenge button is inside title-bar or header
    header_end = text.find('</header>') if '</header>' in text else text.find('<!-- title-bar -->')
    if header_end < 0:
        # Try to find end of title-bar div
        tb_match = re.search(r'<div class="title-bar"[^>]*>.*?</div>', text, re.DOTALL)
        if tb_match:
            header_end = tb_match.end()
    
    if header_end > 0:
        header_area = text[:header_end]
        # Check if challenge button/link is in header
        has_challenge_in_header = 'index.html' in header_area and ('挑战' in header_area or 'btn' in header_area)
        
        if not has_challenge_in_header:
            # Find challenge button outside header
            challenge_match = re.search(r'(<a [^>]*href="index\.html"[^>]*>[^<]*(?:挑战|🎮)[^<]*</a>)', text)
            if challenge_match:
                challenge_html = challenge_match.group(1)
                # Remove from current position
                text = text.replace(challenge_html, '', 1)
                # Insert inside title-bar before </div>
                if '</header>' in text:
                    insert_at = text.find('</header>')
                    text = text[:insert_at] + f'<div style="text-align:center;margin-top:16px;">{challenge_html}</div>' + text[insert_at:]
                else:
                    # Find title-bar closing
                    tb_match = re.search(r'(<div class="title-bar"[^>]*>.*?</div>)', text, re.DOTALL)
                    if tb_match:
                        tb_html = tb_match.group(1)
                        new_tb = tb_html.replace('</div>', f'<div style="text-align:center;margin-top:16px;">{challenge_html}</div></div>', 1)
                        text = text.replace(tb_html, new_tb, 1)
                    else:
                        # Fallback: insert after </header>
                        text = text.replace(challenge_html, '', 1)
                        if '</header>' in text:
                            insert_at = text.find('</header>')
                            text = text[:insert_at] + f'<div style="text-align:center;margin-top:16px;">{challenge_html}</div>' + text[insert_at:]
                changes.append('Moved challenge button into title-bar')
    
    # === FIX 3: Fix progress bar segments ===
    # Find progress-bar div
    pb_match = re.search(r'(<div class="progress-bar"[^>]*>)(.*?)(</div>)', text, re.DOTALL)
    if pb_match and cfg['units'] is not None:
        pb_content = pb_match.group(2)
        seg_count = pb_content.count('progress-seg')
        expected = cfg['units']
        
        if seg_count != expected:
            # Rebuild progress bar with correct segments
            new_pb = '<div class="progress-seg active"></div>\n' + '\n'.join('<div class="progress-seg"></div>' for _ in range(expected - 1))
            text = text[:pb_match.start(2)] + new_pb + text[pb_match.end(2):]
            changes.append(f'Fixed progress bar: {seg_count}→{expected} segments')
    
    # === FIX 4: H1 style ===
    # Check if h1 has proper styling
    h1_css = re.search(r'(\.title-bar\s+h1|header\s+h1|\.hero\s+h1)\s*\{([^}]*)\}', text, re.DOTALL)
    if h1_css:
        h1_rules = h1_css.group(2)
        if '32px' not in h1_rules and '2rem' not in h1_rules:
            # Fix font-size
            if 'font-size' in h1_rules:
                text = re.sub(r'(font-size:\s*)[^;]+', r'\g<1>32px', text, count=1)
            else:
                text = text.replace(h1_css.group(0), h1_css.group(0).rstrip() + '  font-size: 32px;\n}')
            changes.append('Fixed h1 font-size to 32px')
        if 'letter-spacing' not in h1_rules:
            text = text.replace(h1_css.group(0), h1_css.group(0).rstrip() + '  letter-spacing: 4px;\n}')
            changes.append('Added h1 letter-spacing: 4px')
    
    # === FIX 5: title-bar center ===
    if 'text-align: center' not in text and 'text-align:center' not in text:
        # Find title-bar CSS and add text-align: center
        tb_css = re.search(r'\.title-bar\s*\{([^}]*)\}', text, re.DOTALL)
        if tb_css:
            text = text.replace(tb_css.group(0), tb_css.group(0).rstrip() + '  text-align: center;\n}')
            changes.append('Added title-bar text-align: center')
    
    # Write changes
    if changes:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    return changes

# Run fixes
print("=" * 70)
print("逐章修复物理课件")
print("=" * 70)
print()

for ch_dir, cfg in CHAPTERS.items():
    changes = fix_chapter(ch_dir)
    status = "✅" if len(changes) == 0 else "🔧"
    print(f"{status} {cfg['name']} ({ch_dir})")
    if changes:
        for c in changes:
            print(f"   → {c}")
    else:
        print("   无需修复")
    print()

print("=" * 70)
print("修复完成，准备提交...")
print("=" * 70)
