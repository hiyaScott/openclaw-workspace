import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# Math template HUD elements
HUD_ELEMENTS = '''
<div id="hud-grid"></div>
<div class="corner-tl"></div><div class="corner-tr"></div>
<div class="corner-bl"></div><div class="corner-br"></div>
'''

# Standard math template CSS additions needed for HUD
HUD_CSS = '''
/* Scanlines */
body::before {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.15) 2px, rgba(0,0,0,0.15) 4px);
  pointer-events: none;
  z-index: 9999;
}

/* HUD Grid */
#hud-grid {
  position: fixed; inset: 0;
  background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 1;
}

/* Corners */
.corner-tl, .corner-tr, .corner-bl, .corner-br {
  position: fixed; width: 80px; height: 80px; z-index: 2; pointer-events: none;
}
.corner-tl { top: 10px; left: 10px; border-top: 2px solid var(--accent); border-left: 2px solid var(--accent); }
.corner-tr { top: 10px; right: 10px; border-top: 2px solid var(--accent); border-right: 2px solid var(--accent); }
.corner-bl { bottom: 10px; left: 10px; border-bottom: 2px solid var(--accent); border-left: 2px solid var(--accent); }
.corner-br { bottom: 10px; right: 10px; border-bottom: 2px solid var(--accent); border-right: 2px solid var(--accent); }
'''

NON_STANDARD = ['grade8-sem1-ch04', 'grade8-sem1-ch05', 'grade8-sem2-ch07', 'grade8-sem2-ch08', 'grade8-sem2-ch09']

for ch_id in NON_STANDARD:
    path = os.path.join(BASE, ch_id, 'tutorial.html')
    if not os.path.exists(path):
        print(f"⚠️ {ch_id}: not found")
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check if already has hud-grid
    if '#hud-grid' in html:
        print(f"✅ {ch_id}: already has HUD elements")
        continue
    
    # 1. Add HUD CSS before </style>
    # Find last </style>
    style_end = html.rfind('</style>')
    if style_end != -1:
        html = html[:style_end] + '\n\n/* === HUD Elements === */\n' + HUD_CSS + '\n' + html[style_end:]
    
    # 2. Add HUD elements after <body>
    body_tag = html.find('<body>')
    if body_tag != -1:
        body_end = body_tag + len('<body>')
        html = html[:body_end] + '\n' + HUD_ELEMENTS + '\n' + html[body_end:]
    
    # 3. Ensure #app has z-index
    # Check if #app already has z-index
    if 'z-index: 10' not in html[html.find('#app'):html.find('#app')+500]:
        # Add z-index to #app if missing
        app_css = html.find('#app {')
        if app_css != -1:
            app_end = html.find('}', app_css)
            if app_end != -1:
                app_block = html[app_css:app_end+1]
                if 'z-index' not in app_block:
                    html = html[:app_end] + '\n  z-index: 10; position: relative;' + html[app_end:]
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ {ch_id}: HUD elements added ({len(html)} chars)")

print("\n=== Done ===")
