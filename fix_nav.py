#!/usr/bin/env python3
"""将七年级 tutorial.html 的汉堡菜单改为底部「下一章」导航"""

import os, re, glob

BASE = "/root/.openclaw/workspace/portfolio-blog/research/junior-math/courseware-math"

# 章节顺序与下一章映射
NEXT_CHAPTER = {
    "grade7-sem1-ch10": ("grade7-sem1-ch11", "整式的乘除"),
    "grade7-sem1-ch11": ("grade7-sem1-ch12", "因式分解"),
    "grade7-sem1-ch14": ("grade7-sem2-ch16", "相交线与平行线"),
    "grade7-sem2-ch16": ("grade7-sem1-ch10", "整式的加减"),
}

BOTTOM_NAV_CSS = """
    /* ===== 底部章节导航 ===== */
    .bottom-nav {
      display: flex; justify-content: space-between; align-items: center;
      margin-top: 40px; padding: 20px;
      background: var(--panel); border: 1px solid rgba(0, 245, 212, 0.2); border-radius: 8px;
    }
    .bottom-nav a { color: var(--accent); text-decoration: none; font-size: 14px; transition: all 0.3s; }
    .bottom-nav a:hover { text-shadow: 0 0 10px var(--accent); }
    .bottom-nav .next-chapter {
      padding: 10px 24px;
      background: linear-gradient(135deg, var(--accent), rgba(0,187,249,0.8));
      color: var(--bg); border-radius: 6px;
      font-family: 'Orbitron', sans-serif; font-weight: 700;
    }
    @media (max-width: 768px) {
      .bottom-nav { flex-direction: column; gap: 12px; text-align: center; }
    }
"""

def fix_file(path, next_dir, next_name):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 删除 .nav-panel 相关 CSS (从 .nav-panel 开始到 .menu-toggle 之前)
    content = re.sub(
        r'/\* ===== 章节跳转面板 ===== \*/\s*\.nav-panel\s*\{[^}]*\}\s*(?:\.nav-panel[^}]*\}\s*)*\.menu-toggle\s*\{[^}]*\}\s*',
        BOTTOM_NAV_CSS + "\n",
        content,
        flags=re.DOTALL
    )
    
    # 2. 删除响应式中的 nav-panel 和 menu-toggle 规则
    content = re.sub(
        r'\s*\.nav-panel\s*\{[^}]*\}\s*\.nav-panel\.open\s*\{[^}]*\}\s*\.menu-toggle\s*\{[^}]*\}\s*',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # 3. 删除 HTML 中的 ☰ 按钮、nav-panel、navOverlay
    content = re.sub(
        r'\s*<button class="menu-toggle"[^>]*>☰</button>\s*'
        r'<nav class="nav-panel"[^>]*>.*?</nav>\s*'
        r'<div id="navOverlay"[^>]*></div>\s*',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # 4. 在 </main> 前添加 bottom-nav
    nav_html = f'''
  <!-- 底部导航 -->
  <div class="bottom-nav">
    <span style="color:var(--text-dim);font-size:14px;">← 上一节</span>
    <a href="../{next_dir}/tutorial.html" class="next-chapter">下一章：{next_name} →</a>
  </div>
'''
    content = content.replace('</main>', nav_html + '</main>')
    
    # 5. 删除 toggleNav 函数
    content = re.sub(
        r'\s*function toggleNav\(\)[^{]*\{[^}]*\}\s*',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # 6. 删除 resize 监听中的 toggleNav
    content = re.sub(
        r"\s*if\s*\(\s*window\.innerWidth\s*<=\s*768\s*\)\s*toggleNav\(\);\s*",
        '\n',
        content
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

for dir_name, (next_dir, next_name) in NEXT_CHAPTER.items():
    path = os.path.join(BASE, dir_name, "tutorial.html")
    if os.path.exists(path):
        try:
            fix_file(path, next_dir, next_name)
            print(f"✅ Fixed: {dir_name}/tutorial.html")
        except Exception as e:
            print(f"❌ Error fixing {dir_name}: {e}")
    else:
        print(f"⚠️ Not found: {dir_name}/tutorial.html")
