#!/usr/bin/env python3
"""
AI短片Pipeline QA验证脚本
验证渲染逻辑、JSON数据完整性、文件存在性
"""

import json
import os
import sys

def verify_pipeline(project_path, project_name):
    """
    验证Pipeline项目的完整性
    
    Args:
        project_path: 项目根目录路径
        project_name: 项目名称（用于资产目录）
    """
    print(f"=== Pipeline QA验证: {project_name} ===\n")
    
    issues = []
    
    # 1. 检查JSON文件
    json_path = os.path.join(project_path, 'pipeline/data', f'{project_name}.json')
    if not os.path.exists(json_path):
        issues.append(f"JSON文件不存在: {json_path}")
        return False
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # 2. 验证每个Step的当前版本
    for step in data.get('steps', []):
        step_num = step.get('number')
        for version in step.get('content', {}).get('versions', []):
            if version.get('status') != '当前版本':
                continue
            
            v_data = version.get('data', {})
            
            # 验证参考图
            for img in v_data.get('referenceImages', []):
                thumb = img.get('thumbnail', '')
                if not thumb or thumb == 'N/A':
                    issues.append(f"Step {step_num} 参考图 '{img.get('title')}' 缺少缩略图")
                else:
                    thumb_path = os.path.join(project_path, f'assets/{project_name}/thumbnails/{thumb}')
                    if not os.path.exists(thumb_path):
                        issues.append(f"Step {step_num} 参考图缩略图不存在: {thumb}")
            
            # 验证三视图
            three_views = v_data.get('threeViews', {})
            for view_key in ['front', 'side', 'back']:
                view_data = three_views.get(view_key, {})
                thumb = view_data.get('thumbnail', '')
                if thumb:
                    thumb_path = os.path.join(project_path, f'assets/{project_name}/thumbnails/{thumb}')
                    if not os.path.exists(thumb_path):
                        issues.append(f"Step {step_num} 三视图 {view_key} 缩略图不存在: {thumb}")
            
            # 验证场景
            for scene in v_data.get('scenes', []):
                thumb = scene.get('thumbnail', '')
                if not thumb:
                    issues.append(f"Step {step_num} 场景 '{scene.get('title')}' 缺少缩略图")
                else:
                    thumb_path = os.path.join(project_path, f'assets/{project_name}/thumbnails/{thumb}')
                    if not os.path.exists(thumb_path):
                        issues.append(f"Step {step_num} 场景缩略图不存在: {thumb}")
            
            # 验证首帧
            for shot in v_data.get('shots', []):
                ff = shot.get('firstFrame', {})
                thumb = ff.get('thumbnail', '')
                if not thumb:
                    issues.append(f"Step {step_num} 首帧 '{shot.get('title')}' 缺少缩略图")
                else:
                    thumb_path = os.path.join(project_path, f'assets/{project_name}/thumbnails/{thumb}')
                    if not os.path.exists(thumb_path):
                        issues.append(f"Step {step_num} 首帧缩略图不存在: {thumb}")
    
    # 3. 验证HTML渲染逻辑
    html_path = os.path.join(project_path, 'pipeline.html')
    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        # 检查thumbBasePath定义次数
        thumb_base_count = html_content.count("const thumbBasePath")
        if thumb_base_count < 4:
            issues.append(f"thumbBasePath 只定义了 {thumb_base_count} 次，应该有4次")
        
        # 检查是否包含thumbnails/子目录
        if "thumbnails/'" not in html_content and 'thumbnails/"' not in html_content:
            issues.append("HTML中可能缺少thumbnails/子目录路径")
    
    # 4. 输出结果
    print(f"检查完成，发现 {len(issues)} 个问题:\n")
    for issue in issues:
        print(f"  ❌ {issue}")
    
    if not issues:
        print("✅ 所有验证通过！")
        return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 qa_verify.py <project_path> <project_name>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2]
    
    success = verify_pipeline(project_path, project_name)
    sys.exit(0 if success else 1)
