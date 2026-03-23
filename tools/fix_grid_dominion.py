#!/usr/bin/env python3
"""
为grid-dominion添加返回按钮HTML
"""

with open('portfolio-blog/games/grid-dominion/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加返回按钮HTML到body标签后
back_nav = '''<body>
		<nav class="back-nav">
			<a href="../../index.html">返回主页</a>
		</nav>'''

content = content.replace('<body>', back_nav)

with open('portfolio-blog/games/grid-dominion/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加返回按钮到grid-dominion")
