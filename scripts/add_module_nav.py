import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

CHS = ['grade8-sem2-ch07', 'grade8-sem2-ch08', 'grade8-sem2-ch09']

NAV_JS = '''
<script>
// Card navigation overlay for module sections
(function(){
  const modules = document.querySelectorAll('section.module, .module');
  if (modules.length === 0) return;
  
  let current = 0;
  
  function showModule(n) {
    if (n < 0 || n >= modules.length) return;
    modules.forEach((m, i) => {
      m.style.display = (i === n) ? 'block' : 'none';
    });
    current = n;
    // update progress bar if exists
    const segs = document.querySelectorAll('.progress-seg');
    segs.forEach((s, i) => {
      s.classList.toggle('active', i === n);
      s.classList.toggle('done', i < n);
    });
    window.scrollTo(0, 0);
  }
  
  // init: hide all except first
  modules.forEach((m, i) => {
    if (i !== 0) m.style.display = 'none';
  });
  
  // add nav buttons to each module
  modules.forEach((m, i) => {
    const navDiv = document.createElement('div');
    navDiv.style.cssText = 'display:flex;gap:16px;justify-content:center;margin-top:32px;padding-top:20px;border-top:1px solid var(--border);';
    
    if (i > 0) {
      const prev = document.createElement('button');
      prev.textContent = '← 上一单元';
      prev.className = 'btn btn-ghost';
      prev.onclick = () => showModule(i - 1);
      navDiv.appendChild(prev);
    }
    
    if (i < modules.length - 1) {
      const next = document.createElement('button');
      next.textContent = '下一单元 →';
      next.className = 'btn';
      next.onclick = () => showModule(i + 1);
      navDiv.appendChild(next);
    }
    
    m.appendChild(navDiv);
  });
  
  // also hook TOC nav links to card mode
  document.querySelectorAll('.toc-nav a, nav a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (!href || !href.startsWith('#')) return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const idx = Array.from(modules).indexOf(target);
        if (idx >= 0) showModule(idx);
      }
    });
  });
})();
</script>
'''

def add_nav(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Check if already has goTo or card nav
    if 'showModule' in text or 'goTo(' in text:
        print(f"  {os.path.basename(os.path.dirname(path))}: already has nav")
        return
    
    # Insert before </body>
    text = text.replace('</body>', NAV_JS + '\n</body>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"  {os.path.basename(os.path.dirname(path))}: nav added")

for ch in CHS:
    path = os.path.join(BASE, ch, 'tutorial.html')
    if os.path.exists(path):
        add_nav(path)
    else:
        print(f"  {ch}: not found")

print("Done.")
