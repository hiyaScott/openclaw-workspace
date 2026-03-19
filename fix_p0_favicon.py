#!/usr/bin/env python3
"""
P0-5修复脚本：为缺少favicon的HTML页面添加favicon
"""

import os
import re
from pathlib import Path

def get_relative_path_to_root(file_path):
    """计算从文件到网站根目录的相对路径"""
    # 移除 portfolio-blog 前缀
    if 'portfolio-blog' in file_path:
        rel_path = file_path.split('portfolio-blog/')[-1]
    else:
        rel_path = file_path
    
    # 计算目录层级
    depth = rel_path.count('/')
    if depth == 0:
        return './'
    else:
        return '../' * depth

def add_favicon(file_path):
    """为HTML文件添加favicon"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 检查是否已有favicon
    if 'favicon' in content.lower():
        return False
    
    # 检查是否是有效的HTML文件
    if '<html' not in content.lower():
        return False
    
    # 计算相对路径
    prefix = get_relative_path_to_root(file_path)
    
    # 构建favicon链接
    favicon_link = f'    <link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">\n    <link rel="alternate icon" type="image/x-icon" href="{prefix}favicon.ico">\n'
    
    # 尝试在 </head> 前插入
    if '</head>' in content.lower():
        content = re.sub(r'(</head>)', favicon_link + r'\1', content, flags=re.IGNORECASE)
    elif '<head>' in content.lower():
        # 如果有<head>但没有</head>，在<head>后插入
        content = re.sub(r'(<head[^>]*>)', r'\1\n' + favicon_link, content, flags=re.IGNORECASE)
    else:
        # 没有head标签，跳过
        print(f"  跳过(无head标签): {file_path}")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    base_dir = Path('portfolio-blog')
    if not base_dir.exists():
        print(f"错误: 找不到目录 {base_dir}")
        return
    
    updated = 0
    skipped = 0
    errors = 0
    
    # 遍历所有HTML文件
    for html_file in base_dir.rglob('*.html'):
        file_str = str(html_file)
        
        # 跳过node_modules
        if 'node_modules' in file_str:
            continue
        
        try:
            if add_favicon(file_str):
                print(f"  已添加favicon: {file_str}")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  错误处理 {file_str}: {e}")
            errors += 1
    
    print(f"\n完成! 更新了 {updated} 个文件, 跳过了 {skipped} 个文件, 错误 {errors} 个")

if __name__ == '__main__':
    main()
