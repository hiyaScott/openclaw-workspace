import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

def fix_chapter(ch_dir, num_sections):
    """Fix section-based chapter navigation and progress bar."""
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    changes = []
    
    # 1. Fix showModule selector
    old_selector = "const modules = document.querySelectorAll('section.module, .module');"
    new_selector = "const modules = document.querySelectorAll('section[id^=\"sec\"], section.module, .module');"
    if old_selector in text:
        text = text.replace(old_selector, new_selector)
        changes.append("selector fixed")
    
    # 2. Fix progress bar segments
    # Find progress bar and replace with correct number of segments
    progress_match = re.search(r'<div class="progress-bar"[^\u003e]*>(.*?</div\u003e)', text, re.DOTALL)
    if progress_match:
        progress_html = progress_match.group(1)
        current_segs = len(re.findall(r'progress-seg', progress_html))
        if current_segs != num_sections:
            # Build new progress bar HTML
            new_segs = '\n  '.join([
                f'<div class="progress-seg{' active' if i == 0 else ''}" data-ch="{i+1}"></div>'
                for i in range(num_sections)
            ])
            new_progress = f'<div class="progress-bar" id="progress-bar"\u003e\n  {new_segs}\n</div>'
            
            # Replace old progress bar
            old_progress = progress_match.group(0)
            text = text.replace(old_progress, new_progress)
            changes.append(f"progress bar: {current_segs} → {num_sections} segments")
    
    # 3. Ensure showModule updates progress bar
    showmod_match = re.search(r'function showModule\(n\) \{[^}]+\}', text, re.DOTALL)
    if showmod_match:
        showmod_fn = showmod_match.group(0)
        if 'progress-seg' not in showmod_fn:
            # Add progress bar update inside showModule
            old_body = showmod_fn.rstrip('}')
            new_body = old_body + '\n    // update progress bar\n    const segs = document.querySelectorAll(\'.progress-seg\');\n    segs.forEach((s, i) => {\n      s.classList.remove(\'active\', \'done\');\n      if (i === n) s.classList.add(\'active\');\n      else if (i < n) s.classList.add(\'done\');\n    });\n  }'
            text = text.replace(showmod_fn, new_body)
            changes.append("showModule progress update added")
    
    if changes:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  {ch_dir}: {', '.join(changes)}")
        return True
    else:
        print(f"  {ch_dir}: no changes needed")
        return False

print("=== Fixing section-based chapters ===")
fix_chapter('grade8-sem2-ch07', 6)  # 6 sections
fix_chapter('grade8-sem2-ch08', 7)  # 7 sections
# ch09 already fixed
print("Done.")
