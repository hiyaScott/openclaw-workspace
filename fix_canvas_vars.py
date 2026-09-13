#!/usr/bin/env python3
"""
Fix canvas CSS variable usage in tutorial.html files.
canvas 2D context may not properly parse CSS variable strings like 'var(--accent)'.
Replace them with actual color values from :root.
"""

import os
import re
import glob

BASE_DIR = "/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics"

def parse_root_vars(filepath):
    """Extract CSS variable definitions from :root block"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find :root block
    root_match = re.search(r':root\s*\{([^}]+)\}', content)
    if not root_match:
        return {}
    
    vars = {}
    for line in root_match.group(1).split('\n'):
        line = line.strip()
        if line.startswith('--') and ':' in line:
            parts = line.split(':', 1)
            name = parts[0].strip()
            val = parts[1].strip().rstrip(';')
            vars[name] = val
    
    return vars

def fix_canvas_vars(filepath, vars):
    """Replace var(--xxx) with actual color values in canvas drawing code"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Only replace inside <script> tags to avoid breaking CSS
    script_pattern = re.compile(r'(<script>.*?</script>)', re.DOTALL)
    
    def replace_in_script(match):
        script = match.group(1)
        # Replace var(--xxx) with actual values
        for name, val in vars.items():
            pattern = rf"var\({re.escape(name)}\)"
            script = re.sub(pattern, val, script)
        return script
    
    new_content = script_pattern.sub(replace_in_script, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return new_content != content

def main():
    courses = sorted(glob.glob(os.path.join(BASE_DIR, "grade*")))
    
    print("=" * 60)
    print("  Canvas CSS Variable Fix")
    print("=" * 60)
    
    fixed = 0
    errors = []
    
    for course_dir in courses:
        name = os.path.basename(course_dir)
        tutorial = os.path.join(course_dir, "tutorial.html")
        
        if not os.path.exists(tutorial):
            continue
        
        print(f"\n📁 {name}")
        
        try:
            vars = parse_root_vars(tutorial)
            if not vars:
                print(f"  ⚠️ No :root vars found")
                continue
            
            print(f"  📊 Found {len(vars)} CSS variables")
            
            # Check if file has canvas var usage
            with open(tutorial, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_canvas_vars = False
            for name in vars:
                if f"var({name})" in content:
                    has_canvas_vars = True
                    break
            
            if not has_canvas_vars:
                print(f"  ✅ No canvas var usage to fix")
                continue
            
            if fix_canvas_vars(tutorial, vars):
                # Count replacements
                count = 0
                for name in vars:
                    count += content.count(f"var({name})")
                
                print(f"  ✅ Fixed {count} canvas var(--xxx) usages")
                fixed += 1
            else:
                print(f"  ⚠️ No changes made")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors.append(f"{name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"  DONE: Fixed {fixed} files")
    if errors:
        print(f"  ERRORS: {len(errors)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
