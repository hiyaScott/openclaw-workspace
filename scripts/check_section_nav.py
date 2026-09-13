import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

def fix_section_based_chapter(ch_dir):
    """Fix section-based chapters (ch07, ch08, ch09) that use showModule navigation."""
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    if not os.path.exists(path):
        print(f"  {ch_dir}: NOT FOUND")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Count actual top-level sections
    sections = re.findall(r'<section\s+id="sec-[^"]+"', text)
    print(f"  {ch_dir}: {len(sections)} sections found")
    
    # Check progress bar segments
    progress_match = re.search(r'<div class="progress-bar".*?</div>', text, re.DOTALL)
    progress_seg_count = 0
    if progress_match:
        progress_seg_count = len(re.findall(r'progress-seg', progress_match.group(0)))
    print(f"    Progress segments: {progress_seg_count}")
    
    # Check showModule selector
    showmod_match = re.search(r'const modules = document\.querySelectorAll\(([^)]+)\)', text)
    if showmod_match:
        selector = showmod_match.group(1)
        print(f"    showModule selector: {selector}")
        
        # Check if selector matches sections
        if 'sec-' not in selector and 'section[id' not in selector:
            # Need to fix selector to match section[id^="sec-"]
            print(f"    ⚠️ Selector doesn't match section[id^='sec-'] structure")
    
    # Check if navigation overlay script exists
    nav_overlay = 'Card navigation overlay' in text or 'showModule' in text
    print(f"    Navigation overlay: {nav_overlay}")
    
    return True

print("=== Checking section-based chapters ===")
for ch in ['grade8-sem2-ch07', 'grade8-sem2-ch08', 'grade8-sem2-ch09']:
    fix_section_based_chapter(ch)
    print()
