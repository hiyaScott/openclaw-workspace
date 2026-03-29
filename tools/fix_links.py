#!/usr/bin/env python3
"""
自动修复网站链接问题
"""

import os
import re
from pathlib import Path

class LinkFixer:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.fixes = []
        
    def fix_favicon_links(self):
        """修复favicon.svg链接 - 改为根目录路径"""
        kimi_claw_dir = self.base_path / 'kimi-claw'
        
        # 检查根目录是否有favicon
        root_favicon = self.base_path / 'favicon.svg'
        has_root_favicon = root_favicon.exists()
        
        for html_file in kimi_claw_dir.rglob('*/index.html'):
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 检查是否有 ../favicon.svg 引用
                if '../favicon.svg' in content:
                    # 计算到根目录的相对路径
                    depth = len(html_file.relative_to(kimi_claw_dir).parts) - 1
                    if depth == 0:
                        # 直接子目录，如 kimi-claw/audio-design/
                        new_path = '../favicon.svg'  # 已经是正确的
                    else:
                        # 更深层的目录
                        new_path = '../../favicon.svg'
                    
                    # 实际上 ../favicon.svg 对于 kimi-claw/*/ 是正确的
                    # 问题可能是根目录没有favicon文件
                    pass
                    
            except Exception as e:
                print(f"❌ 处理失败: {html_file} - {e}")
        
        # 解决方案：在根目录创建favicon.svg
        if not has_root_favicon:
            self.create_root_favicon()
    
    def create_root_favicon(self):
        """在根目录创建favicon.svg"""
        favicon_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="20" fill="#0a0a0a"/>
  <text x="50" y="65" font-size="50" text-anchor="middle" fill="#00ffff">🦐</text>
</svg>'''
        
        favicon_path = self.base_path / 'favicon.svg'
        with open(favicon_path, 'w', encoding='utf-8') as f:
            f.write(favicon_content)
        
        self.fixes.append(f"创建根目录favicon.svg")
        print(f"✅ 创建: {favicon_path}")
    
    def fix_games_index(self):
        """修复 games/index.html 的链接"""
        games_index = self.base_path / 'games' / 'index.html'
        if not games_index.exists():
            return
        
        with open(games_index, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        # 修复 ../../index.html#works -> ./index.html#works
        content = content.replace('href="../../index.html#works"', 'href="../index.html#works"')
        
        if content != original:
            with open(games_index, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixes.append(f"修复 games/index.html 链接")
            print(f"✅ 修复: {games_index}")
    
    def fix_markdown_links(self):
        """修复指向.md文件的链接"""
        # 修复 bambu-3dprint/index.html
        bambu_html = self.base_path / 'kimi-claw' / 'bambu-3dprint' / 'index.html'
        if bambu_html.exists():
            with open(bambu_html, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            # 将 .md 链接改为指向技能目录或移除
            content = re.sub(r'href="SKILL\.md"', 'href="#" title="SKILL.md (内部文档)"', content)
            content = re.sub(r'href="references/([^"]+)\.md"', r'href="#" title="\1 (内部文档)"', content)
            
            if content != original:
                with open(bambu_html, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 bambu-3dprint Markdown链接")
                print(f"✅ 修复: {bambu_html}")
    
    def fix_template_variables(self):
        """修复模板变量残留"""
        file_transfer = self.base_path / 'pages' / 'tools' / 'file-transfer' / 'index.html'
        if file_transfer.exists():
            with open(file_transfer, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            # 移除或替换模板变量
            content = content.replace('${f.download_url}', '#')
            content = content.replace('${f.filename}', '文件名')
            
            if content != original:
                with open(file_transfer, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 file-transfer 模板变量")
                print(f"✅ 修复: {file_transfer}")
    
    def fix_research_links(self):
        """修复research目录的链接"""
        # 修复 research/institute/index.html
        institute_html = self.base_path / 'research' / 'institute' / 'index.html'
        if institute_html.exists():
            with open(institute_html, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            content = content.replace('href="../kimi-claw/index.html"', 'href="../../kimi-claw/index.html"')
            
            if content != original:
                with open(institute_html, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 research/institute 链接")
                print(f"✅ 修复: {institute_html}")
        
        # 修复 research/instrument-simulator/bianzhong/design-doc.html
        bianzhong_html = self.base_path / 'research' / 'instrument-simulator' / 'bianzhong' / 'design-doc.html'
        if bianzhong_html.exists():
            with open(bianzhong_html, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            content = content.replace('href="../../kimi-claw/index.html"', 'href="../../../kimi-claw/index.html"')
            
            if content != original:
                with open(bianzhong_html, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 bianzhong/design-doc 链接")
                print(f"✅ 修复: {bianzhong_html}")
    
    def fix_data_uri_links(self):
        """修复data:image链接被错误识别的问题"""
        # 这些实际上是有效的data URI，不需要修复
        pass
    
    def fix_ai_shortfilm_experiments(self):
        """修复 ai-shortfilm/experiments 链接"""
        experiments_index = self.base_path / 'kimi-claw' / 'ai-shortfilm' / 'experiments' / 'index.html'
        if experiments_index.exists():
            with open(experiments_index, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            content = content.replace('href="../ai-shortfilm/"', 'href="../"')
            
            if content != original:
                with open(experiments_index, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 ai-shortfilm/experiments 链接")
                print(f"✅ 修复: {experiments_index}")
    
    def fix_status_monitor_whitepaper(self):
        """修复status-monitor白皮书链接"""
        whitepaper_html = self.base_path / 'status-monitor' / 'whitepaper.html'
        if whitepaper_html.exists():
            with open(whitepaper_html, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            # 将.md链接改为.html或移除
            content = content.replace(
                'href="./认知负载监控系统技术白皮书_v1.0.md"',
                'href="#" title="白皮书文档"'
            )
            
            if content != original:
                with open(whitepaper_html, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 status-monitor 白皮书链接")
                print(f"✅ 修复: {whitepaper_html}")
    
    def fix_pages_tools_index(self):
        """修复pages/tools/index.html的链接"""
        tools_index = self.base_path / 'pages' / 'tools' / 'index.html'
        if tools_index.exists():
            with open(tools_index, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            # 移除不存在的页面链接
            content = re.sub(
                r'<a[^>]*href="./file-transfer\.html"[^>]*>.*?</a>',
                '<span style="opacity:0.5">文件传输 (开发中)</span>',
                content,
                flags=re.DOTALL
            )
            content = re.sub(
                r'<a[^>]*href="./temp-pages\.html"[^>]*>.*?</a>',
                '<span style="opacity:0.5">临时页面 (开发中)</span>',
                content,
                flags=re.DOTALL
            )
            
            if content != original:
                with open(tools_index, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes.append(f"修复 pages/tools/index.html 链接")
                print(f"✅ 修复: {tools_index}")
    
    def run(self):
        """运行所有修复"""
        print("="*60)
        print("🔧 自动修复链接问题")
        print("="*60)
        
        self.fix_favicon_links()
        self.fix_games_index()
        self.fix_markdown_links()
        self.fix_template_variables()
        self.fix_research_links()
        self.fix_ai_shortfilm_experiments()
        self.fix_status_monitor_whitepaper()
        self.fix_pages_tools_index()
        
        print("\n" + "="*60)
        print(f"✅ 完成 {len(self.fixes)} 项修复")
        print("="*60)
        for fix in self.fixes:
            print(f"  • {fix}")

if __name__ == '__main__':
    fixer = LinkFixer('/root/.openclaw/workspace/portfolio-blog')
    fixer.run()
