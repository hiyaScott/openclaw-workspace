#!/usr/bin/env python3
"""
Website Link Checker
检测网站所有链接状态
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

class LinkChecker:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.empty_links = []
        self.broken_links = []
        self.external_links = []
        self.hash_links = []
        self.mailto_links = []
        self.total_links = 0
        
    def extract_links(self, html_file):
        """从HTML文件中提取所有href链接"""
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 无法读取文件: {html_file} - {e}")
            return []
        
        # 匹配 href="..." 或 href='...'
        pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(pattern, content)
        return links
    
    def check_link(self, link, html_file):
        """检查单个链接状态"""
        self.total_links += 1
        
        # 跳过空链接
        if not link or link.strip() == '':
            self.empty_links.append({
                'file': str(html_file),
                'link': link,
                'type': '空链接'
            })
            return
        
        # 检测hash链接 (#)
        if link == '#' or link.startswith('#'):
            self.hash_links.append({
                'file': str(html_file),
                'link': link,
                'type': 'Hash链接'
            })
            return
        
        # 检测mailto链接
        if link.startswith('mailto:'):
            self.mailto_links.append({
                'file': str(html_file),
                'link': link,
                'type': 'Mailto链接'
            })
            return
        
        # 检测外部链接
        if link.startswith('http://') or link.startswith('https://'):
            self.external_links.append({
                'file': str(html_file),
                'link': link,
                'type': '外部链接'
            })
            return
        
        # 检测javascript链接
        if link.startswith('javascript:'):
            self.external_links.append({
                'file': str(html_file),
                'link': link[:50] + '...' if len(link) > 50 else link,
                'type': 'JavaScript链接'
            })
            return
        
        # 处理相对路径
        html_dir = html_file.parent
        
        # 处理以/开头的绝对路径（相对于网站根目录）
        if link.startswith('/'):
            target_path = self.base_path / link.lstrip('/')
        else:
            target_path = html_dir / link
        
        # 解析路径，处理 ../ 和 ./
        try:
            target_path = target_path.resolve()
        except Exception:
            pass
        
        # 如果链接包含#锚点，移除锚点检查文件
        if '#' in str(target_path):
            target_path = Path(str(target_path).split('#')[0])
        
        # 检查文件是否存在
        if not target_path.exists():
            self.broken_links.append({
                'file': str(html_file.relative_to(self.base_path)),
                'link': link,
                'target': str(target_path.relative_to(self.base_path)) if self.base_path in target_path.parents else str(target_path),
                'type': '文件不存在'
            })
    
    def run(self):
        """运行检查"""
        print("="*60)
        print("🔍 网站链接检测开始")
        print("="*60)
        
        html_files = list(self.base_path.rglob('*.html'))
        print(f"\n📁 发现 {len(html_files)} 个HTML文件")
        
        for html_file in html_files:
            links = self.extract_links(html_file)
            for link in links:
                self.check_link(link, html_file)
        
        self.print_report()
    
    def print_report(self):
        """打印检测报告"""
        print("\n" + "="*60)
        print("📊 检测报告")
        print("="*60)
        
        print(f"\n✅ 总链接数: {self.total_links}")
        print(f"❌ 空链接: {len(self.empty_links)}")
        print(f"⚠️ Hash链接 (#): {len(self.hash_links)}")
        print(f"📧 Mailto链接: {len(self.mailto_links)}")
        print(f"🌐 外部链接: {len(self.external_links)}")
        print(f"💔 损坏链接: {len(self.broken_links)}")
        
        # 详细报告
        if self.empty_links:
            print("\n" + "-"*60)
            print("❌ 空链接 (需要修复)")
            print("-"*60)
            for item in self.empty_links[:20]:  # 只显示前20个
                print(f"  文件: {item['file']}")
            if len(self.empty_links) > 20:
                print(f"  ... 还有 {len(self.empty_links) - 20} 个")
        
        if self.broken_links:
            print("\n" + "-"*60)
            print("💔 损坏链接 (文件不存在)")
            print("-"*60)
            for item in self.broken_links[:30]:  # 只显示前30个
                print(f"  来源: {item['file']}")
                print(f"  链接: {item['link']}")
                print(f"  目标: {item['target']}")
                print()
            if len(self.broken_links) > 30:
                print(f"... 还有 {len(self.broken_links) - 30} 个")
        
        if self.external_links:
            print("\n" + "-"*60)
            print("🌐 外部链接 (需要手动验证)")
            print("-"*60)
            unique_external = {}
            for item in self.external_links:
                if item['link'] not in unique_external:
                    unique_external[item['link']] = item
            
            for item in list(unique_external.values())[:20]:
                print(f"  {item['link']}")
            if len(unique_external) > 20:
                print(f"  ... 还有 {len(unique_external) - 20} 个唯一外部链接")
        
        print("\n" + "="*60)
        print("检测完成")
        print("="*60)

if __name__ == '__main__':
    checker = LinkChecker('/root/.openclaw/workspace/portfolio-blog')
    checker.run()
