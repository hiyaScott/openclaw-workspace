import re, os

BASE = '/root/.openclaw/workspace/portfolio-blog/research/junior-physics/courseware-physics'

# CSS to add for inner cards
INNER_CARD_CSS = '''/* inner cards (nested within unit cards) */
.inner-card {
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 1rem 0;
  margin-bottom: 0.5rem;
}
.inner-card .card-title {
  font-size: 1.1rem;
  margin-bottom: 0.6rem;
}
'''

def fix_nested_cards(ch_dir):
    """Fix nested card class names to prevent layout bloat."""
    path = os.path.join(BASE, ch_dir, 'tutorial.html')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    changes = []
    
    # Count nested cards: <div class="card"> without id or hidden
    # These are inside unit cards and should be inner-card
    nested_pattern = r'<div\s+class="card"\s*>'
    nested = re.findall(nested_pattern, text)
    
    if not nested:
        print(f"  {ch_dir}: no nested cards to fix")
        return False
    
    # Replace nested cards with inner-card
    # We use a negative lookbehind to avoid matching top-level cards
    # But simpler: just replace all <div class="card"> that DON'T have id or hidden
    # Top-level cards have id="chX" or class="card hidden"
    # The nested ones are just <div class="card">
    
    text = re.sub(r'<div\s+class="card"\s*>', '<div class="inner-card">', text)
    changes.append(f"nested cards: {len(nested)} → inner-card")
    
    # Add .inner-card CSS after .card CSS block
    card_css = re.search(r'(\.card\s*\{[^}]*\})', text, re.DOTALL)
    if card_css and '.inner-card' not in text:
        insert_pos = card_css.end()
        text = text[:insert_pos] + '\n\n' + INNER_CARD_CSS + text[insert_pos:]
        changes.append("added .inner-card CSS")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"  {ch_dir}: {', '.join(changes)}")
    return True

print("=== Fixing nested cards ===")
fix_nested_cards('grade9-sem2-ch14')
fix_nested_cards('grade9-sem2-ch15')
print("Done.")
