import re
import base64
import os

# Read the HTML file
file_path = '/root/.openclaw/workspace/portfolio-blog/irrigation-quotation/index.html'
with open(file_path, 'r') as f:
    content = f.read()

# Find all base64 images
pattern = r'data:image/([a-zA-Z]+);base64,([^"\'\s]+)'
matches = re.findall(pattern, content)

print(f'Found {len(matches)} base64 images:')

# Track replacements
replacements = []

for i, (img_type, data) in enumerate(matches):
    ext = img_type.lower()
    if ext == 'jpeg':
        ext = 'jpg'
    filename = f'image_{i+1}.{ext}'
    filepath = os.path.join('/root/.openclaw/workspace/portfolio-blog/irrigation-quotation/', filename)
    
    # Save to file
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(data))
    
    size = os.path.getsize(filepath)
    print(f'{i+1}. Type: {img_type}, Size: {size} bytes, Saved as: {filename}')
    
    # Store replacement info
    old_str = f'data:image/{img_type};base64,{data}'
    new_str = filename
    replacements.append((old_str, new_str))

# Update HTML content
updated_content = content
for old_str, new_str in replacements:
    updated_content = updated_content.replace(old_str, new_str, 1)

# Add loading="lazy" to img tags that reference external images
# Pattern to match img tags with src="image_X.ext"
img_pattern = r'(<img[^>]+src="image_\d+\.(?:jpg|png|svg)"[^>]*)(>)'
def add_lazy_loading(match):
    before, closing = match.groups()
    if 'loading=' not in before:
        return before + ' loading="lazy"' + closing
    return match.group(0)

updated_content = re.sub(img_pattern, add_lazy_loading, updated_content)

# Write updated HTML
with open(file_path, 'w') as f:
    f.write(updated_content)

print(f"\nHTML updated successfully!")

# Calculate file sizes
original_size = len(content)
new_size = len(updated_content)
print(f"Original HTML size: {original_size} bytes ({original_size/1024:.1f} KB)")
print(f"New HTML size: {new_size} bytes ({new_size/1024:.1f} KB)")
print(f"Reduction: {original_size - new_size} bytes ({(original_size - new_size)/1024:.1f} KB)")
