#!/usr/bin/env python3
"""为 tutorial.html 添加 bottom-nav CSS（如果缺失）"""

import os

BASE = "/root/.openclaw/workspace/portfolio-blog/research/junior-math/courseware-math"

FILES = [
    "grade7-sem1-ch10/tutorial.html",
    "grade7-sem1-ch11/tutorial.html", 
    "grade7-sem1-ch14/tutorial.html",
    "grade7-sem2-ch16/tutorial.html",
]

CSS_BLOCK = """
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

for rel_path in FILES:
    path = os.path.join(BASE, rel_path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有 bottom-nav CSS
    if '.bottom-nav' not in content:
        # 在 </style> 前插入
        content = content.replace('</style>', CSS_BLOCK + '\n  </style>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Added bottom-nav CSS to {rel_path}")
    else:
        print(f"⚠️ bottom-nav CSS already exists in {rel_path}")
