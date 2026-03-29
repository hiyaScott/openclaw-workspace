#!/usr/bin/env python3
"""
查询可灵视频生成结果 - 修正版
"""

import requests
import json
import re

API_KEY = "sk-0SIXEK6miUYpDpZYGI3UEsSJMB2ZsY82J2TsGvfU44GSneTo"
TASK_ID = "867147274790014976"  # 刚才提交的任务ID

url = "https://www.dmxapi.cn/v1/responses"

headers = {
    "Content-Type": "application/json",
    "Authorization": API_KEY,
}

# 查询参数 - 使用流式输出
payload = {
    "model": "kling-text2video-get",
    "input": TASK_ID,
    "stream": True
}

print(f"正在查询任务: {TASK_ID}")
print("-" * 60)

response = requests.post(url, headers=headers, json=payload, stream=True)

final_result = None

for line in response.iter_lines():
    if line:
        line_text = line.decode('utf-8')
        if line_text.startswith('data: '):
            data = line_text[6:]
            if data != '[DONE]':
                try:
                    json_data = json.loads(data)
                    final_result = json_data
                    print(f"收到数据: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}...")
                except json.JSONDecodeError:
                    pass

print("-" * 60)
print("查询完成!")

if final_result:
    print(f"\n完整结果:\n{json.dumps(final_result, indent=2, ensure_ascii=False)}")
    
    # 尝试提取视频URL
    try:
        resp_data = final_result.get("response", {})
        status = resp_data.get("status", "")
        output = resp_data.get("output", [])
        
        print(f"\n状态: {status}")
        
        if status == "completed" and output:
            text_content = output[0].get("content", [{}])[0].get("text", "")
            print(f"\n内容预览:\n{text_content[:1000]}")
            
            # 提取视频URL
            url_match = re.search(r'(https?://[^\s]+\.mp4[^\s]*)', text_content)
            if url_match:
                video_url = url_match.group(1)
                video_url = re.sub(r'[\n\r].*$', '', video_url)
                print(f"\n✅ 视频URL:\n{video_url}")
        else:
            print(f"\n任务状态: {status} (未completed)")
    except Exception as e:
        print(f"解析错误: {e}")
