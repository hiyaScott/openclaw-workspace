#!/usr/bin/env python3
"""
Pipeline 页面 QA 验证工具
验证视频海报是否正确显示
"""

import json
import urllib.request
import urllib.error
import ssl
import sys

# 禁用 SSL 验证警告
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://hiyascott.github.io/hiyamax-blog"

def check_url(url, description):
    """检查 URL 是否可访问"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (QA-Check)')
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            return status == 200, status
    except Exception as e:
        return False, str(e)

def fetch_json():
    """获取并解析 JSON 数据"""
    url = f"{BASE_URL}/pipeline/data/the_147th_day.json?t=9999999999"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (QA-Check)')
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ JSON 获取失败: {e}")
        return None

def check_video_posters():
    """检查所有视频海报"""
    print("=" * 60)
    print("Pipeline 页面 QA 验证")
    print("=" * 60)
    
    # 1. 检查页面
    print("\n【Step 1】检查页面可访问性...")
    page_ok, page_status = check_url(f"{BASE_URL}/pipeline.html", "Pipeline页面")
    print(f"  页面状态: {'✅' if page_ok else '❌'} HTTP {page_status}")
    
    # 2. 检查 JSON 数据
    print("\n【Step 2】检查数据完整性...")
    data = fetch_json()
    if not data:
        return False
    print("  ✅ JSON 格式有效")
    
    # 3. 找到 V5 版本的 clips
    print("\n【Step 3】检查视频海报配置...")
    try:
        step5 = data['steps'][4]  # 视频生成步骤
        versions = step5['content']['versions']
        v5 = [v for v in versions if v['version'] == 'v5'][0]
        clips = v5['data']['clips']
        
        poster_issues = []
        poster_checks = []
        
        for clip in clips:
            clip_id = clip.get('id', 'unknown')
            has_poster = 'poster' in clip
            poster_url = clip.get('poster', '')
            
            if not has_poster:
                poster_issues.append(f"{clip_id}: 缺少 poster 字段")
                poster_checks.append((clip_id, False, "无poster字段"))
                continue
            
            # 检查海报图片可访问性
            # 处理相对路径
            if poster_url.startswith('./'):
                poster_url = f"{BASE_URL}{poster_url[1:]}"
            
            img_ok, img_status = check_url(poster_url, f"{clip_id}海报")
            
            if img_ok:
                poster_checks.append((clip_id, True, f"HTTP {img_status}"))
            else:
                poster_issues.append(f"{clip_id}: 海报不可访问 ({img_status})")
                poster_checks.append((clip_id, False, str(img_status)))
        
        # 输出结果
        for clip_id, ok, status in poster_checks:
            icon = "✅" if ok else "❌"
            print(f"  {icon} {clip_id}: {status}")
        
        # 4. 特别关注 shot02 版本
        print("\n【Step 4】检查 shot02 V5 版本...")
        shot02_clips = [c for c in clips if c.get('id', '').startswith('hailuo_v5_shot02')]
        for clip in shot02_clips:
            clip_id = clip.get('id')
            has_poster = 'poster' in clip
            poster_url = clip.get('poster', '')
            is_absolute = poster_url.startswith('http') if has_poster else False
            
            print(f"  {'✅' if has_poster and is_absolute else '❌'} {clip_id}")
            print(f"      poster字段: {'✅' if has_poster else '❌'}")
            print(f"      绝对路径: {'✅' if is_absolute else '❌'}")
        
        # 5. 总结
        print("\n" + "=" * 60)
        if poster_issues:
            print("❌ QA 验证失败")
            print("\n问题列表:")
            for issue in poster_issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ QA 验证通过")
            print(f"\n总共检查 {len(clips)} 个视频")
            print(f"海报可访问: {len([c for c in poster_checks if c[1]])}/{len(poster_checks)}")
            return True
            
    except Exception as e:
        print(f"❌ 数据解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_video_posters()
    sys.exit(0 if success else 1)
