#!/usr/bin/env python3
"""
Deploy Sentinel - 发布哨兵全套检查
"""

import os
import subprocess
from pathlib import Path

class DeploySentinel:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.results = {
            'build': {'status': True, 'details': []},
            'links': {'status': True, 'details': [], 'total': 0, 'broken': 0},
            'files': {'status': True, 'details': [], 'largest': 0},
            'git': {'status': True, 'details': [], 'branch': '', 'commits_ahead': 0},
        }
    
    def check_build(self):
        """构建检查"""
        html_files = list(self.base_path.rglob('*.html'))
        self.results['build']['details'] = f"HTML 文件 {len(html_files)} 个"
        self.results['build']['count'] = len(html_files)
        
        # 检查是否有语法错误（简单的HTML检查）
        error_count = 0
        for html_file in html_files[:50]:  # 抽样检查
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 检查基本HTML结构
                    if '<html' not in content.lower() and '<!doctype' not in content.lower():
                        error_count += 1
            except:
                error_count += 1
        
        if error_count > 10:
            self.results['build']['status'] = False
            self.results['build']['details'] += f" (发现 {error_count} 个异常文件)"
        
        return self.results['build']['status']
    
    def check_links(self):
        """链接检查"""
        import re
        
        total_links = 0
        broken_links = []
        
        html_files = list(self.base_path.rglob('*.html'))
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            pattern = r'href=["\']([^"\']+)["\']'
            links = re.findall(pattern, content)
            
            for link in links:
                total_links += 1
                
                # 跳过外部链接、hash、mailto、javascript
                if (link.startswith('http') or link.startswith('#') or 
                    link.startswith('mailto:') or link.startswith('javascript:') or
                    link.startswith('data:')):
                    continue
                
                # 检查相对路径
                html_dir = html_file.parent
                if link.startswith('/'):
                    target_path = self.base_path / link.lstrip('/')
                else:
                    target_path = html_dir / link
                
                # 移除锚点
                if '#' in str(target_path):
                    target_path = Path(str(target_path).split('#')[0])
                
                if not target_path.exists():
                    broken_links.append({
                        'file': str(html_file.relative_to(self.base_path)),
                        'link': link
                    })
        
        self.results['links']['total'] = total_links
        self.results['links']['broken'] = len(broken_links)
        self.results['links']['details'] = f"扫描 {total_links} 个链接，{len(broken_links)} 个死链"
        
        if len(broken_links) > 50:  # 超过50个死链视为失败
            self.results['links']['status'] = False
        
        return self.results['links']['status']
    
    def check_files(self):
        """文件检查"""
        # 检查关键文件
        key_files = [
            'index.html',
            'kimi-claw/index.html',
            'games/index.html',
        ]
        
        missing = []
        for key_file in key_files:
            if not (self.base_path / key_file).exists():
                missing.append(key_file)
        
        # 检查文件大小
        largest = 0
        largest_file = ''
        for html_file in self.base_path.rglob('*.html'):
            size = html_file.stat().st_size
            if size > largest:
                largest = size
                largest_file = str(html_file.relative_to(self.base_path))
        
        self.results['files']['largest'] = largest
        self.results['files']['largest_file'] = largest_file
        
        # 超过500KB视为异常 (但排除重要数据文件)
        whitelist = ['character-skills-enumeration.html']  # 重要数据文件白名单
        is_whitelisted = any(w in largest_file for w in whitelist)
        
        if largest > 500 * 1024 and not is_whitelisted:
            self.results['files']['status'] = False
            self.results['files']['details'] = f"最大文件 {largest/1024:.1f}KB ({largest_file})，超过500KB阈值"
        else:
            self.results['files']['details'] = f"最大文件 {largest/1024:.1f}KB ({largest_file})"
            if is_whitelisted:
                self.results['files']['details'] += " (白名单)"        
        
        if missing:
            self.results['files']['status'] = False
            self.results['files']['details'] += f"，缺失关键文件: {', '.join(missing)}"
        
        return self.results['files']['status']
    
    def check_git(self):
        """Git状态检查"""
        try:
            # 检查分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            branch = result.stdout.strip()
            self.results['git']['branch'] = branch
            
            # 检查是否有未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            changes = result.stdout.strip()
            
            # 检查是否有未推送的提交
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'origin/{branch}..{branch}'],
                cwd=self.base_path,
                capture_output=True,
                text=True
            )
            commits_ahead = int(result.stdout.strip() or 0)
            self.results['git']['commits_ahead'] = commits_ahead
            
            if changes:
                self.results['git']['status'] = False
                self.results['git']['details'] = f"分支 {branch}，有未提交的更改"
            elif commits_ahead > 0:
                self.results['git']['details'] = f"分支 {branch}，有 {commits_ahead} 个提交待推送"
            else:
                self.results['git']['details'] = f"分支 {branch}，工作区干净"
            
        except Exception as e:
            self.results['git']['status'] = False
            self.results['git']['details'] = f"Git检查失败: {e}"
        
        return self.results['git']['status']
    
    def run_all(self):
        """运行所有检查"""
        print("🚀 发布哨兵检查报告")
        print("="*50)
        
        self.check_build()
        status_icon = "✅" if self.results['build']['status'] else "❌"
        print(f"{status_icon} 构建检查: {'通过' if self.results['build']['status'] else '失败'} ({self.results['build']['details']})")
        
        self.check_links()
        status_icon = "✅" if self.results['links']['status'] else "⚠️"
        print(f"{status_icon} 链接检查: {'通过' if self.results['links']['status'] else '警告'} ({self.results['links']['details']})")
        
        self.check_files()
        status_icon = "✅" if self.results['files']['status'] else "❌"
        print(f"{status_icon} 文件检查: {'通过' if self.results['files']['status'] else '失败'} ({self.results['files']['details']})")
        
        self.check_git()
        status_icon = "✅" if self.results['git']['status'] else "⚠️"
        print(f"{status_icon} Git状态: {'通过' if self.results['git']['status'] else '警告'} ({self.results['git']['details']})")
        
        print("="*50)
        
        # 总结
        all_pass = all(r['status'] for r in self.results.values())
        if all_pass:
            print("🎉 所有检查通过，可以安全发布")
        else:
            print("⚠️ 部分检查未通过，建议修复后发布")
        
        return all_pass, self.results

if __name__ == '__main__':
    sentinel = DeploySentinel('/root/.openclaw/workspace/portfolio-blog')
    sentinel.run_all()
