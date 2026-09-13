import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# Standard updateProgress function snippet
UPDATE_PROGRESS_FN = '''
function updateProgress() {
  const segs = document.querySelectorAll('.progress-seg');
  segs.forEach((seg, i) => {
    seg.classList.remove('active', 'done');
    if (i + 1 < currentCh) seg.classList.add('done');
    else if (i + 1 === currentCh) seg.classList.add('active');
  });
}
'''

# Standard goTo function that calls updateProgress
GOTO_WITH_PROGRESS = '''function goTo(n) {
  document.getElementById('ch' + currentCh).classList.add('hidden');
  document.getElementById('ch' + n).classList.remove('hidden');
  currentCh = n;
  updateProgress();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}'''

def fix_ch17():
    """Fix ch17: remove footer nav, ensure goTo calls updateProgress"""
    path = os.path.join(BASE, 'grade9-sem2-ch17/tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 1. Remove the extra footer nav buttons
    footer_pattern = r'<div style="text-align:center; padding:40px 20px; border-top:1px solid var\(--border\);">\s*<div class="btn-row">\s*<button class="btn btn-ghost" onclick="location\.href=\'\.\.\/grade9-sem2-ch16\/tutorial\.html\'">← 上一单元</button>\s*<button class="btn btn-ghost" disabled>已到最后一章 →</button>\s*</div>'
    text = re.sub(footer_pattern, '', text, flags=re.DOTALL)
    
    # 2. Fix goTo to call updateProgress
    old_goto = '''let currentCh = 1;
function goTo(n) {
  document.getElementById('ch' + currentCh).classList.add('hidden');
  document.getElementById('ch' + n).classList.remove('hidden');
  currentCh = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}'''
    
    new_goto = '''let currentCh = 1;
function goTo(n) {
  document.getElementById('ch' + currentCh).classList.add('hidden');
  document.getElementById('ch' + n).classList.remove('hidden');
  currentCh = n;
  updateProgress();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}'''
    
    if old_goto in text:
        text = text.replace(old_goto, new_goto)
        print("  ch17: goTo fixed to call updateProgress")
    
    # 3. Add unit-nav to ch7 if missing
    ch7_start = text.find('id="ch7"')
    ch7_end = text.find('</div><!-- /.container -->', ch7_start)
    ch7_html = text[ch7_start:ch7_end]
    
    if 'class="unit-nav"' not in ch7_html:
        # Find last closing </div> before container end
        # Insert unit-nav before </div><!-- /.container -->
        nav_html = '''\n    <div class="unit-nav">
      <button class="btn btn-ghost" onclick="goTo(6)">← 上一单元</button>
    </div>'''
        
        # Find the position to insert (before the closing </div> of ch7)
        # ch7 is the last card, so its closing </div> should be before <!-- /.container -->
        insert_pos = text.rfind('</div>', 0, text.find('<!-- /.container -->'))
        if insert_pos > ch7_start:
            text = text[:insert_pos] + nav_html + text[insert_pos:]
            print("  ch17: unit-nav added to ch7")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return True

def fix_ch14():
    """ch14: add updateProgress call and function"""
    path = os.path.join(BASE, 'grade9-sem2-ch14/tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Find goTo and add updateProgress call
    old_goto = re.search(r'function goTo\(n\) \{[^}]+\}', text, re.DOTALL)
    if old_goto and 'updateProgress' not in old_goto.group(0):
        new_goto = old_goto.group(0).rstrip('}') + '\n  updateProgress();\n}'
        text = text.replace(old_goto.group(0), new_goto)
        print("  ch14: goTo fixed")
    
    # Add updateProgress function before goTo if not exists
    if 'function updateProgress' not in text:
        # Insert before goTo
        goto_pos = text.find('function goTo')
        if goto_pos > 0:
            text = text[:goto_pos] + UPDATE_PROGRESS_FN + '\n' + text[goto_pos:]
            print("  ch14: updateProgress function added")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True

def fix_ch15():
    """ch15: add updateProgress call and function"""
    path = os.path.join(BASE, 'grade9-sem2-ch15/tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    old_goto = re.search(r'function goTo\(n\) \{[^}]+\}', text, re.DOTALL)
    if old_goto and 'updateProgress' not in old_goto.group(0):
        new_goto = old_goto.group(0).rstrip('}') + '\n  updateProgress();\n}'
        text = text.replace(old_goto.group(0), new_goto)
        print("  ch15: goTo fixed")
    
    if 'function updateProgress' not in text:
        goto_pos = text.find('function goTo')
        if goto_pos > 0:
            text = text[:goto_pos] + UPDATE_PROGRESS_FN + '\n' + text[goto_pos:]
            print("  ch15: updateProgress function added")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True

def fix_ch16():
    """ch16: ch16 might not even have goTo - add full navigation"""
    path = os.path.join(BASE, 'grade9-sem2-ch16/tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Check if goTo exists
    if 'function goTo' not in text:
        # Find closing </body> and insert navigation before it
        body_end = text.find('</body>')
        if body_end > 0:
            nav_script = '''\n<script>
let currentCh = 1;
function goTo(n) {
  const cards = document.querySelectorAll('.card');
  cards.forEach((c, i) => {
    c.classList.toggle('hidden', i + 1 !== n);
  });
  currentCh = n;
  updateProgress();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
\n''' + UPDATE_PROGRESS_FN + '''\n</script>\n'''
            text = text[:body_end] + nav_script + text[body_end:]
            print("  ch16: full navigation added (no goTo existed)")
    else:
        # goTo exists but no updateProgress
        old_goto = re.search(r'function goTo\(n\) \{[^}]+\}', text, re.DOTALL)
        if old_goto and 'updateProgress' not in old_goto.group(0):
            new_goto = old_goto.group(0).rstrip('}') + '\n  updateProgress();\n}'
            text = text.replace(old_goto.group(0), new_goto)
            print("  ch16: goTo fixed")
        
        if 'function updateProgress' not in text:
            goto_pos = text.find('function goTo')
            if goto_pos > 0:
                text = text[:goto_pos] + UPDATE_PROGRESS_FN + '\n' + text[goto_pos:]
                print("  ch16: updateProgress function added")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return True

print("=== Fixing ch14, ch15, ch16, ch17 navigation ===")
fix_ch14()
fix_ch15()
fix_ch16()
fix_ch17()
print("Done.")
