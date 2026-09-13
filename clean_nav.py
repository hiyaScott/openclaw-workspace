#!/usr/bin/env python3
"""清理七年级 tutorial.html 中的汉堡菜单残留代码"""

import os, re

BASE = "/root/.openclaw/workspace/portfolio-blog/research/junior-math/courseware-math"

FILES = [
    "grade7-sem1-ch10/tutorial.html",
    "grade7-sem1-ch11/tutorial.html",
    "grade7-sem1-ch14/tutorial.html",
    "grade7-sem2-ch16/tutorial.html",
]

def clean_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 删除 .nav-panel 所有 CSS 规则（从章节跳转面板注释开始到主内容区之前）
    content = re.sub(
        r'/\* ===== 章节跳转面板 ===== \*/\s*'
        r'(?:\.nav-panel[^{]*\{[^}]*\}\s*)*'
        r'(?:\.nav-panel[^}]*\}\s*)*'
        r'\s*/\* 移动端汉堡菜单 \*/\s*'
        r'\.menu-toggle[^{]*\{[^}]*\}\s*',
        '',
        content
    )
    
    # 2. 删除响应式中的 nav-panel 相关
    content = re.sub(
        r'\s*\.nav-panel\s*\{[^}]*\}\s*'
        r'(?:\.nav-panel[^}]*\}\s*)*',
        '\n',
        content
    )
    
    # 3. 删除 HTML 中的 ☰ 按钮和 nav-panel
    content = re.sub(
        r'\s*<button[^>]*>☰</button>\s*'
        r'<nav[^>]*nav-panel[^>]*>.*?</nav>\s*',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # 4. 删除 navOverlay
    content = re.sub(
        r'\s*<div[^>]*navOverlay[^>]*>.*?</div>\s*',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # 5. 删除 JS 中的 toggleNav 函数
    content = re.sub(
        r'\s*function\s+toggleNav\s*\(\)\s*\{[^}]*\}\s*',
        '\n',
        content
    )
    
    # 6. 删除 resize 监听
    content = re.sub(
        r"\s*window\.addEventListener\s*\(\s*['\"]resize['\"]\s*,\s*\(\)\s*=>\s*\{[^}]*toggleNav[^}]*\}\s*\)\s*;?\s*",
        '\n',
        content
    )
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

for rel_path in FILES:
    path = os.path.join(BASE, rel_path)
    if os.path.exists(path):
        try:
            clean_file(path)
            # 验证
            has_nav = bool(re.search(r'nav-panel|menu-toggle|☰', open(path).read()))
            has_bottom = bool(re.search(r'bottom-nav', open(path).read()))
            status = "✅" if not has_nav and has_bottom else "⚠️"
            print(f"{status} {rel_path} | nav-panel: {'❌' if has_nav else '已清除'} | bottom-nav: {'✅' if has_bottom else '❌'}")
        except Exception as e:
            print(f"❌ Error: {rel_path} - {e}")
    else:
        print(f"⚠️ Not found: {rel_path}")
