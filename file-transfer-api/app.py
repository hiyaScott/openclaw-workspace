from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://hiyascott.github.io", "http://localhost:*"],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# GitHub配置
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN') or open('/root/.config/github-token').read().strip()
GITHUB_REPO = "hiyaScott/scott-portfolio"
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_REPO}"

def get_file_sha(path):
    """获取文件SHA（如果文件存在）"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(f"{GITHUB_API_BASE}/contents/{path}", headers=headers)
    if response.status_code == 200:
        return response.json().get('sha')
    return None

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件到GitHub"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files['file']
        sender = request.form.get('sender', 'unknown')  # 'scott' or 'jetton'
        
        if file.filename == '':
            return jsonify({"error": "文件名为空"}), 400
        
        # 读取文件内容
        file_content = file.read()
        
        # 构建文件路径
        today = datetime.now().strftime("%Y-%m-%d")
        folder = f"transfers/from-{sender}/{today}"
        filename = file.filename
        
        # 处理重名文件
        base_name, ext = os.path.splitext(filename)
        counter = 1
        path = f"{folder}/{filename}"
        
        while get_file_sha(path):
            path = f"{folder}/{base_name}_{counter}{ext}"
            counter += 1
        
        # Base64编码文件内容
        content_b64 = base64.b64encode(file_content).decode('utf-8')
        
        # 提交到GitHub
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "message": f"Upload {filename} from {sender}",
            "content": content_b64,
            "branch": "main"
        }
        
        response = requests.put(
            f"{GITHUB_API_BASE}/contents/{path}",
            headers=headers,
            json=data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return jsonify({
                "success": True,
                "url": result['content']['html_url'],
                "download_url": result['content']['download_url'],
                "path": path,
                "size": len(file_content)
            })
        else:
            return jsonify({
                "error": f"GitHub API错误: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/list', methods=['GET'])
def list_files():
    """列出传输文件夹中的文件"""
    try:
        sender = request.args.get('sender', 'jetton')  # 查看谁发来的文件
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 获取 transfers/from-{sender} 目录下的所有文件
        folder = f"transfers/from-{sender}"
        response = requests.get(
            f"{GITHUB_API_BASE}/contents/{folder}",
            headers=headers
        )
        
        if response.status_code == 404:
            return jsonify({"files": []})
        
        if response.status_code != 200:
            return jsonify({"error": f"GitHub API错误: {response.status_code}"}), 500
        
        # 递归获取所有文件
        files = []
        
        def get_files_recursive(url, prefix=""):
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                return
            
            items = resp.json()
            for item in items:
                if item['type'] == 'file':
                    files.append({
                        "name": item['name'],
                        "path": item['path'],
                        "size": item['size'],
                        "url": item['html_url'],
                        "download_url": item['download_url'],
                        "date": item.get('last_modified', 'unknown')
                    })
                elif item['type'] == 'dir':
                    get_files_recursive(item['url'], prefix + item['name'] + "/")
        
        get_files_recursive(response.url)
        
        # 按日期排序（最新的在前）
        files.sort(key=lambda x: x['path'], reverse=True)
        
        return jsonify({"files": files})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    """获取文件下载URL"""
    try:
        path = request.args.get('path')
        if not path:
            return jsonify({"error": "缺少path参数"}), 400
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(
            f"{GITHUB_API_BASE}/contents/{path}",
            headers=headers
        )
        
        if response.status_code != 200:
            return jsonify({"error": "文件不存在"}), 404
        
        data = response.json()
        return jsonify({
            "download_url": data['download_url'],
            "content": data.get('content'),  # Base64编码的内容
            "encoding": data.get('encoding')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_file():
    """删除文件"""
    try:
        data = request.json
        path = data.get('path')
        
        if not path:
            return jsonify({"error": "缺少path参数"}), 400
        
        # 获取文件SHA
        sha = get_file_sha(path)
        if not sha:
            return jsonify({"error": "文件不存在"}), 404
        
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "message": f"Delete {path}",
            "sha": sha,
            "branch": "main"
        }
        
        response = requests.delete(
            f"{GITHUB_API_BASE}/contents/{path}",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 204]:
            return jsonify({"success": True})
        else:
            return jsonify({"error": f"删除失败: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
