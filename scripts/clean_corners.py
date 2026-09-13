import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

CHS = [
    'grade8-sem1-ch00', 'grade8-sem1-ch01', 'grade8-sem1-ch02',
    'grade8-sem1-ch03', 'grade8-sem1-ch04', 'grade8-sem1-ch05',
    'grade8-sem2-ch06'
]

def remove_corners(text):
    """Remove corner-tl/tr/bl/br CSS rules."""
    # Match from .corner-tl group selector through all individual corner rules
    # Pattern: .corner-tl,... { ... } followed by .corner-tl { ... } etc.
    pattern = (
        r'\.corner-tl,\s*\.corner-tr,\s*\.corner-bl,\s*\.corner-br\s*\{[^}]+\}\s*'
        r'(\.corner-tl\s*\{[^}]+\}\s*)?'
        r'(\.corner-tr\s*\{[^}]+\}\s*)?'
        r'(\.corner-bl\s*\{[^}]+\}\s*)?'
        r'(\.corner-br\s*\{[^}]+\}\s*)?'
    )
    text = re.sub(pattern, '', text)
    return text

for ch in CHS:
    path = os.path.join(BASE, ch, 'tutorial.html')
    if not os.path.exists(path):
        print(f"  {ch}: not found")
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    orig = text
    text = remove_corners(text)
    
    # Also remove any remaining hud-grid divs in HTML
    text = re.sub(r'\s*<div id="hud-grid"></div>\s*', '\n', text)
    text = re.sub(r'\s*<div class="corner-tl"></div><div class="corner-tr"></div>\s*<div class="corner-bl"></div><div class="corner-br"></div>\s*', '\n', text)
    
    if text != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  {ch}: cleaned")
    else:
        print(f"  {ch}: no changes")
    
    # Verify
    with open(path, 'r') as f:
        content = f.read()
    remaining = sum(1 for kw in ['corner-tl','hud-grid','Scanlines','特工装备室','特工总部'] if kw in content)
    print(f"    -> {remaining} agent keywords remaining")

print("Done.")
