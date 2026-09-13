#!/usr/bin/env python3
"""
Fix mobile responsiveness and unify button styles for all physics courseware.

Targets:
1. tutorial.html - Add consistent mobile @media queries (3 breakpoints)
2. index.html - Unify .btn core dimensions (padding, font-size) while preserving design themes
"""

import os
import re
import glob

BASE_DIR = "/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics"

# Standard mobile breakpoints for tutorial.html
TUTORIAL_MEDIA_QUERIES = """
/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 768px) {
  .title-bar h1 { font-size: 24px; letter-spacing: 2px; }
  #app { padding: 24px 16px; }
  .card { padding: 20px; }
  .card-header h2 { font-size: 18px; }
  .concept-box { padding: 14px 16px; }
  .concept-box .formula { font-size: 16px; }
  .anim-area { padding: 18px; min-height: 100px; }
  .example-item { padding: 12px 14px; }
  .example-item .q { font-size: 14px; }
  .quiz-btn { padding: 10px 14px; font-size: 14px; }
  .btn-row { flex-direction: column; gap: 10px; }
  .btn { width: 100%; text-align: center; padding: 12px 24px; font-size: 14px; }
  .progress-seg { width: 40px; }
  .compare-table { font-size: 12px; }
  .compare-table th, .compare-table td { padding: 6px 8px; }
}
@media (max-width: 480px) {
  .title-bar h1 { font-size: 20px; letter-spacing: 1px; }
  .title-bar .subtitle { font-size: 12px; }
  #app { padding: 16px 12px; }
  .card { padding: 16px; }
  .card-header h2 { font-size: 16px; }
  .concept-box { padding: 12px 14px; }
  .concept-box p { font-size: 14px; line-height: 1.6; }
  .anim-area { padding: 14px; min-height: 80px; }
  .anim-area canvas { max-width: 100%; height: auto; }
  .example-item { padding: 10px 12px; }
  .quiz-box { padding: 14px; }
  .quiz-question { font-size: 14px; }
  .btn { padding: 10px 20px; font-size: 13px; }
  .quiz-btn { padding: 8px 12px; font-size: 13px; }
  .progress-seg { width: 32px; height: 3px; }
}
@media (max-width: 360px) {
  .title-bar h1 { font-size: 18px; }
  #app { padding: 12px 10px; }
  .card { padding: 12px; }
  .card-header h2 { font-size: 15px; }
  .concept-box { padding: 10px 12px; }
  .concept-box .formula { font-size: 14px; }
  .btn { padding: 8px 16px; font-size: 12px; }
  .quiz-options { gap: 6px; }
  .quiz-btn { padding: 6px 10px; font-size: 12px; }
  .example-item .q { font-size: 13px; }
  .example-item .a { font-size: 12px; }
}
"""

# Standard button base + variant CSS for index.html
# Replaces ALL button-related CSS with unified standard
STANDARD_INDEX_BTN_CSS = """  /* ===== UNIFIED BUTTON SYSTEM ===== */
  .btn {
    display: inline-block;
    padding: 12px 28px;
    border-radius: 6px;
    font-family: 'Orbitron', 'Share Tech Mono', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    text-align: center;
    border: none;
    min-height: 44px;
    line-height: 1.2;
  }
  .btn:hover { transform: translateY(-2px); }
  .btn:active { transform: translateY(0); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
  
  /* Primary variant - accent filled */
  .btn-primary,
  .btn-filled {
    background: var(--accent);
    color: var(--bg);
  }
  .btn-primary:hover,
  .btn-filled:hover { box-shadow: 0 4px 20px rgba(0,240,200,0.4); }
  
  /* Ghost variant */
  .btn-ghost {
    background: transparent;
    border: 1px solid var(--accent);
    color: var(--accent);
  }
  .btn-ghost:hover { background: rgba(0,240,200,0.1); }
  
  /* Warning/CTA variant */
  .btn-warn,
  .btn-cta {
    background: rgba(255,209,102,0.15);
    border: 1px solid var(--warn, #ffd166);
    color: var(--warn, #ffd166);
  }
  .btn-warn:hover,
  .btn-cta:hover { background: rgba(255,209,102,0.25); box-shadow: 0 0 20px rgba(255,209,102,0.3); }
  
  /* Danger variant */
  .btn-danger {
    background: rgba(239,71,111,0.15);
    border: 1px solid var(--danger);
    color: var(--danger);
  }
  .btn-danger:hover { background: rgba(239,71,111,0.25); }
  
  /* Small variant */
  .btn-sm {
    padding: 8px 20px;
    font-size: 12px;
    min-height: 36px;
  }
  
  /* Legacy class aliases for backward compatibility */
  .start-btn, .opt-btn, .stage-btn {
    display: inline-block;
    padding: 12px 28px;
    border-radius: 6px;
    font-family: 'Orbitron', 'Share Tech Mono', sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    text-align: center;
    border: none;
    min-height: 44px;
    line-height: 1.2;
  }
  .start-btn:hover, .opt-btn:hover, .stage-btn:hover { transform: translateY(-2px); }
  .start-btn:active, .opt-btn:active, .stage-btn:active { transform: translateY(0); }
  .start-btn:disabled, .opt-btn:disabled, .stage-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
"""

def remove_media_queries(content):
    """Remove all @media blocks from CSS content"""
    # Handle nested braces carefully
    result = []
    i = 0
    while i < len(content):
        if content[i:i+7] == '@media ':
            # Find the opening brace
            brace_start = content.find('{', i)
            if brace_start == -1:
                result.append(content[i:])
                break
            # Skip past this @media block by counting braces
            depth = 1
            j = brace_start + 1
            while j < len(content) and depth > 0:
                if content[j] == '{':
                    depth += 1
                elif content[j] == '}':
                    depth -= 1
                j += 1
            # Skip whitespace after the block
            while j < len(content) and content[j] in ' \n\t':
                j += 1
            i = j
        else:
            result.append(content[i])
            i += 1
    return ''.join(result)

def fix_tutorial_html(filepath):
    """Ensure tutorial.html has comprehensive mobile @media queries"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find </style> tag position (last one)
    style_end = content.rfind('</style>')
    if style_end == -1:
        print(f"    ⚠️ No </style> found")
        return False
    
    # Remove existing @media blocks
    style_start = content.find('<style>')
    before_style = content[:style_start+7]
    style_content = content[style_start+7:style_end]
    after_style = content[style_end:]
    
    cleaned_style = remove_media_queries(style_content)
    
    # Append standard media queries
    new_content = before_style + cleaned_style + TUTORIAL_MEDIA_QUERIES + '\n' + after_style
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def fix_index_html(filepath):
    """Unify button styles in index.html while preserving other design"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find <style> section
    style_start = content.find('<style>')
    style_end = content.find('</style>')
    if style_start == -1 or style_end == -1:
        print(f"    ⚠️ No <style> section found")
        return False
    
    style_section = content[style_start:style_end+8]
    
    # Remove ALL button-related CSS rules (including variants and pseudo-classes)
    # Pattern matches: .btn, .btn-ghost, .btn-warn, .btn-danger, .btn-sm, .start-btn, .opt-btn, .stage-btn, etc.
    # and their :hover, :active, :disabled variants
    
    # First pass: remove button class declarations and their contents
    # This regex handles single-line and multi-line rule bodies
    def remove_btn_rules(css):
        # Match .something-btn or .btn-something { ... }
        # Need to handle nested braces carefully
        patterns = [
            r'\s*\.[\w-]*btn[\w-]*\s*\{[^}]*\}\s*',
            r'\s*\.[\w-]*btn[\w-]*:[\w-]+\s*\{[^}]*\}\s*',
            r'\s*\.action-btns\s*\{[^}]*\}\s*',
            r'\s*\.btn-row\s*\{[^}]*\}\s*',
        ]
        for pattern in patterns:
            css = re.sub(pattern, '\n', css)
        return css
    
    cleaned_style = remove_btn_rules(style_section)
    
    # Also remove .start-btn, .opt-btn, .stage-btn (non-btn-suffix patterns)
    def remove_special_btn_rules(css):
        patterns = [
            r'\s*\.start-btn[\w-]*\s*\{[^}]*\}\s*',
            r'\s*\.start-btn[\w-]*:[\w-]+\s*\{[^}]*\}\s*',
            r'\s*\.opt-btn[\w-]*\s*\{[^}]*\}\s*',
            r'\s*\.opt-btn[\w-]*:[\w-]+\s*\{[^}]*\}\s*',
            r'\s*\.stage-btn[\w-]*\s*\{[^}]*\}\s*',
            r'\s*\.stage-btn[\w-]*:[\w-]+\s*\{[^}]*\}\s*',
        ]
        for pattern in patterns:
            css = re.sub(pattern, '\n', css)
        return css
    
    cleaned_style = remove_special_btn_rules(cleaned_style)
    
    # Insert unified button CSS before </style>
    insert_pos = cleaned_style.rfind('</style>')
    new_style = cleaned_style[:insert_pos] + '\n' + STANDARD_INDEX_BTN_CSS + '\n' + cleaned_style[insert_pos:]
    
    # Replace old style section with new one
    new_content = content[:style_start] + new_style + content[style_end+8:]
    
    # Update inline button styles in HTML to use unified classes
    # Replace style="padding:..." on buttons with class variants
    # But be careful not to break functional inline styles
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    courses = sorted(glob.glob(os.path.join(BASE_DIR, "grade*")))
    
    print("=" * 70)
    print("  Physics Courseware - Mobile & Button Unification Fix")
    print("=" * 70)
    
    fixed_tutorial = 0
    fixed_index = 0
    skipped = []
    errors = []
    
    for course_dir in courses:
        course_name = os.path.basename(course_dir)
        print(f"\n📁 {course_name}")
        
        # Fix tutorial.html
        tutorial_path = os.path.join(course_dir, "tutorial.html")
        if os.path.exists(tutorial_path):
            try:
                if fix_tutorial_html(tutorial_path):
                    print(f"  ✅ tutorial.html  → mobile @media added/updated")
                    fixed_tutorial += 1
                else:
                    skipped.append(f"{course_name}/tutorial.html")
            except Exception as e:
                print(f"  ❌ tutorial.html  → error: {e}")
                errors.append(f"{course_name}/tutorial.html: {e}")
        else:
            skipped.append(f"{course_name}/tutorial.html (missing)")
        
        # Fix index.html
        index_path = os.path.join(course_dir, "index.html")
        if os.path.exists(index_path):
            try:
                if fix_index_html(index_path):
                    print(f"  ✅ index.html     → button styles unified")
                    fixed_index += 1
                else:
                    skipped.append(f"{course_name}/index.html")
            except Exception as e:
                print(f"  ❌ index.html     → error: {e}")
                errors.append(f"{course_name}/index.html: {e}")
        else:
            skipped.append(f"{course_name}/index.html (missing)")
    
    print("\n" + "=" * 70)
    print(f"  RESULTS:")
    print(f"    ✅ Fixed: {fixed_tutorial} tutorial.html + {fixed_index} index.html")
    if skipped:
        print(f"    ⚠️  Skipped: {len(skipped)} files")
    if errors:
        print(f"    ❌ Errors: {len(errors)}")
        for err in errors[:5]:
            print(f"       - {err}")
        if len(errors) > 5:
            print(f"       ... and {len(errors)-5} more")
    print("=" * 70)
    
    # Write summary to file
    summary_path = os.path.join(BASE_DIR, "FIX_SUMMARY.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# Courseware Fix Summary\n\n")
        f.write(f"Date: 2026-05-23\n\n")
        f.write("## Changes Made\n\n")
        f.write(f"- **tutorial.html**: Added unified mobile responsive @media queries ({fixed_tutorial} files)\n")
        f.write(f"  - 768px, 480px, 360px breakpoints\n")
        f.write(f"  - Card padding, font sizes, button widths adjusted\n")
        f.write(f"  - Canvas/images constrained to viewport\n")
        f.write(f"- **index.html**: Unified button styles ({fixed_index} files)\n")
        f.write(f"  - Standard padding: 12px 28px\n")
        f.write(f"  - Standard font-size: 14px\n")
        f.write(f"  - Standard min-height: 44px (touch-friendly)\n")
        f.write(f"  - Variants: .btn-primary, .btn-ghost, .btn-warn, .btn-danger, .btn-sm\n")
        f.write(f"\n## Skipped\n")
        for s in skipped:
            f.write(f"- {s}\n")
        if errors:
            f.write(f"\n## Errors\n")
            for e in errors:
                f.write(f"- {e}\n")
    print(f"\n📝 Summary written to: {summary_path}")

if __name__ == '__main__':
    main()
