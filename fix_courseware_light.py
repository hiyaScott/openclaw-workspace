#!/usr/bin/env python3
"""
Lightweight fix for mobile responsiveness and button size consistency.

Strategy:
1. tutorial.html - Append standard @media queries (preserve all existing CSS)
2. index.html - Only inject a .btn size override + mobile @media, preserve all existing design
"""

import os
import re
import glob

BASE_DIR = "/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics"

# ===== 1. tutorial.html mobile queries =====
TUTORIAL_MOBILE_CSS = """
/* ===== MOBILE RESPONSIVE (auto-injected) ===== */
@media (max-width: 768px) {
  .title-bar h1 { font-size: 24px !important; letter-spacing: 2px !important; }
  #app { padding: 24px 16px !important; }
  .card { padding: 20px !important; }
  .card-header h2 { font-size: 18px !important; }
  .concept-box { padding: 14px 16px !important; }
  .concept-box .formula { font-size: 16px !important; }
  .anim-area { padding: 18px !important; min-height: 100px !important; }
  .anim-area canvas { max-width: 100% !important; height: auto !important; }
  .example-item { padding: 12px 14px !important; }
  .example-item .q { font-size: 14px !important; }
  .quiz-btn { padding: 10px 14px !important; font-size: 14px !important; }
  .btn-row { flex-direction: column !important; gap: 10px !important; }
  .btn-row .btn { width: 100% !important; text-align: center !important; padding: 12px 24px !important; font-size: 14px !important; }
  .progress-seg { width: 40px !important; }
  .compare-table { font-size: 12px !important; }
  .compare-table th, .compare-table td { padding: 6px 8px !important; }
}
@media (max-width: 480px) {
  .title-bar h1 { font-size: 20px !important; letter-spacing: 1px !important; }
  .title-bar .subtitle { font-size: 12px !important; }
  #app { padding: 16px 12px !important; }
  .card { padding: 16px !important; }
  .card-header h2 { font-size: 16px !important; }
  .concept-box { padding: 12px 14px !important; }
  .concept-box p { font-size: 14px !important; line-height: 1.6 !important; }
  .anim-area { padding: 14px !important; min-height: 80px !important; }
  .example-item { padding: 10px 12px !important; }
  .quiz-box { padding: 14px !important; }
  .quiz-question { font-size: 14px !important; }
  .btn { padding: 10px 20px !important; font-size: 13px !important; }
  .quiz-btn { padding: 8px 12px !important; font-size: 13px !important; }
  .progress-seg { width: 32px !important; height: 3px !important; }
}
@media (max-width: 360px) {
  .title-bar h1 { font-size: 18px !important; }
  #app { padding: 12px 10px !important; }
  .card { padding: 12px !important; }
  .card-header h2 { font-size: 15px !important; }
  .concept-box { padding: 10px 12px !important; }
  .concept-box .formula { font-size: 14px !important; }
  .btn { padding: 8px 16px !important; font-size: 12px !important; }
  .quiz-options { gap: 6px !important; }
  .quiz-btn { padding: 6px 10px !important; font-size: 12px !important; }
  .example-item .q { font-size: 13px !important; }
  .example-item .a { font-size: 12px !important; }
}
"""

# ===== 2. index.html unified button size + mobile =====
INDEX_BTN_OVERRIDE_CSS = """
/* ===== BUTTON SIZE UNIFICATION (auto-injected) ===== */
.btn, .btn-ghost, .btn-warn, .btn-danger, .btn-cta, .btn-sm,
.start-btn, .opt-btn, .stage-btn, .action-btn, .check-btn, .next-btn {
  padding: 12px 28px !important;
  font-size: 14px !important;
  min-height: 44px !important;
  line-height: 1.2 !important;
}
.btn-sm, .btn-small { padding: 8px 20px !important; font-size: 12px !important; min-height: 36px !important; }

/* Mobile override for all buttons */
@media (max-width: 768px) {
  .btn, .btn-ghost, .btn-warn, .btn-danger, .btn-cta,
  .start-btn, .opt-btn, .stage-btn, .action-btn, .check-btn, .next-btn {
    padding: 12px 24px !important;
    font-size: 14px !important;
    min-height: 44px !important;
  }
  .btn-sm, .btn-small { padding: 8px 16px !important; font-size: 12px !important; }
  .action-btns, .btn-row { flex-direction: column !important; gap: 10px !important; }
  .action-btns .btn, .btn-row .btn { width: 100% !important; text-align: center !important; }
  .work-area { flex-direction: column !important; }
  .side-panel { flex: 1 1 auto !important; width: 100% !important; }
  .main-panel { padding: 16px !important; min-height: 280px !important; }
  .hud-header { padding: 10px 14px !important; }
  .hud-title { font-size: 1rem !important; }
}
@media (max-width: 480px) {
  .btn, .btn-ghost, .btn-warn, .btn-danger, .btn-cta,
  .start-btn, .opt-btn, .stage-btn, .action-btn, .check-btn, .next-btn {
    padding: 10px 20px !important;
    font-size: 13px !important;
    width: 100% !important;
    text-align: center !important;
  }
  .btn-sm, .btn-small { padding: 6px 14px !important; font-size: 11px !important; }
  body { padding: 8px !important; }
  .intro-box { padding: 24px 16px !important; }
  .intro-title { font-size: 1.2rem !important; }
  .side-panel { display: none !important; }
  .main-panel { padding: 12px !important; }
}
"""

def fix_tutorial(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    style_end = content.rfind('</style>')
    if style_end == -1:
        return False
    
    # Remove any previously injected mobile blocks (detect by comment)
    marker = '/* ===== MOBILE RESPONSIVE (auto-injected) ===== */'
    if marker in content:
        idx = content.find(marker)
        next_style = content.find('</style>', idx)
        content = content[:idx] + content[next_style:]
    
    style_end = content.rfind('</style>')
    content = content[:style_end] + TUTORIAL_MOBILE_CSS + '\n' + content[style_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def fix_index(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    style_end = content.rfind('</style>')
    if style_end == -1:
        return False
    
    # Remove any previously injected blocks
    marker = '/* ===== BUTTON SIZE UNIFICATION (auto-injected) ===== */'
    if marker in content:
        idx = content.find(marker)
        next_style = content.find('</style>', idx)
        content = content[:idx] + content[next_style:]
    
    style_end = content.rfind('</style>')
    content = content[:style_end] + INDEX_BTN_OVERRIDE_CSS + '\n' + content[style_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    courses = sorted(glob.glob(os.path.join(BASE_DIR, "grade*")))
    
    print("=" * 60)
    print("  Courseware Mobile + Button Size Fix (Lightweight)")
    print("=" * 60)
    
    fixed_t = fixed_i = 0
    errors = []
    
    for course_dir in courses:
        name = os.path.basename(course_dir)
        print(f"\n📁 {name}")
        
        t = os.path.join(course_dir, "tutorial.html")
        if os.path.exists(t):
            try:
                if fix_tutorial(t):
                    print(f"  ✅ tutorial.html  → mobile CSS injected")
                    fixed_t += 1
            except Exception as e:
                print(f"  ❌ tutorial.html  → {e}")
                errors.append(f"{name}/tutorial: {e}")
        
        i = os.path.join(course_dir, "index.html")
        if os.path.exists(i):
            try:
                if fix_index(i):
                    print(f"  ✅ index.html     → button size unified")
                    fixed_i += 1
            except Exception as e:
                print(f"  ❌ index.html     → {e}")
                errors.append(f"{name}/index: {e}")
    
    print("\n" + "=" * 60)
    print(f"  DONE: {fixed_t} tutorial + {fixed_i} index files")
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
    print("=" * 60)

if __name__ == '__main__':
    main()
