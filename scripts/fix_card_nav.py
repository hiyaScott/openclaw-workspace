import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'
CHS = ['grade8-sem1-ch04', 'grade8-sem1-ch05']

NAV_CSS = '''
/* Card navigation override */
.card.section[data-sec]:not([data-sec="0"]) { display: none; }
'''

NAV_JS = '''
<script>
(function(){
  const sections = document.querySelectorAll('.card.section[data-sec]');
  if (sections.length === 0) return;
  let current = 0;

  function goTo(n) {
    if (n < 0 || n >= sections.length) return;
    sections.forEach((s, i) => {
      s.style.display = (i === n) ? 'block' : 'none';
    });
    current = n;
    // update progress bar
    document.querySelectorAll('.progress-seg').forEach((seg, i) => {
      seg.classList.toggle('active', i === n);
      seg.classList.toggle('done', i < n);
    });
    window.scrollTo(0, 0);
  }

  // Add nav buttons to each section
  sections.forEach((sec, i) => {
    const existingNav = sec.querySelector('.nav-row, .btn-row');
    if (existingNav) return; // skip if already has nav

    const nav = document.createElement('div');
    nav.style.cssText = 'display:flex;gap:16px;justify-content:center;margin-top:32px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.1);';

    if (i > 0) {
      const prev = document.createElement('button');
      prev.className = 'btn btn-ghost';
      prev.textContent = '← 上一单元';
      prev.onclick = () => goTo(i - 1);
      nav.appendChild(prev);
    }
    if (i < sections.length - 1) {
      const next = document.createElement('button');
      next.className = 'btn';
      next.textContent = '下一单元 →';
      next.onclick = () => goTo(i + 1);
      nav.appendChild(next);
    }
    sec.appendChild(nav);
  });

  // Progress bar click
  document.querySelectorAll('.progress-seg').forEach((seg, i) => {
    seg.style.cursor = 'pointer';
    seg.onclick = () => goTo(i);
  });
})();
</script>
'''

def fix(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if 'goTo(' in text and 'card.section[data-sec]:not' in text:
        print(f"  {os.path.basename(os.path.dirname(path))}: already fixed")
        return
    
    # Insert CSS before </style>
    text = text.replace('</style>', NAV_CSS + '\n</style>')
    
    # Insert JS before </body>
    text = text.replace('</body>', NAV_JS + '\n</body>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"  {os.path.basename(os.path.dirname(path))}: fixed")

for ch in CHS:
    path = os.path.join(BASE, ch, 'tutorial.html')
    if os.path.exists(path):
        fix(path)
    else:
        print(f"  {ch}: not found")

print("Done.")
