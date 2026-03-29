#!/usr/bin/env python3
"""
Shrimp Jetton 认知负载 API 服务器 v7.0
提供实时认知负载数据，支持 CORS

端口: 8080
端点: /api/status
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# 数据文件路径
DATA_FILE = "/root/.openclaw/workspace/portfolio-blog/status-monitor/cognitive-data.json"
HISTORY_FILE = "/root/.openclaw/workspace/portfolio-blog/status-monitor/cognitive-history.jsonl"

def get_status():
    """读取当前认知负载数据"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {
            "error": str(e),
            "cognitive_score": 0,
            "status_text": "🟡 数据读取失败",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def get_trend_data():
    """读取趋势数据 - 返回最近100个点"""
    points = []
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                lines = f.readlines()
            
            # 解析最近100行
            for line in lines[-100:]:
                try:
                    r = json.loads(line.strip())
                    ts = r.get('timestamp', '')
                    if ts:
                        # 转换为毫秒时间戳
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        points.append({
                            "timestamp_ms": int(dt.timestamp() * 1000),
                            "score": r.get('score', 0)
                        })
                except:
                    pass
    except Exception as e:
        return {"error": str(e), "points": []}
    
    return {"points": points}

class CORSRequestHandler(BaseHTTPRequestHandler):
    """支持 CORS 的请求处理器"""
    
    def log_message(self, format, *args):
        """静默日志，减少输出"""
        pass
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/status':
            # 返回认知负载状态
            data = get_status()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode('utf-8'))
        
        elif path == '/api/trend':
            # 返回趋势数据
            data = get_trend_data()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode('utf-8'))
        
        elif path == '/health':
            # 健康检查
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        
        else:
            # 404
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run_server(port=8080):
    """启动服务器"""
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"🚀 API 服务器启动成功")
    print(f"   端口: {port}")
    print(f"   状态: http://localhost:{port}/api/status")
    print(f"   趋势: http://localhost:{port}/api/trend")
    print(f"   健康: http://localhost:{port}/health")
    print(f"   按 Ctrl+C 停止")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)

if __name__ == '__main__':
    from datetime import datetime, timezone
    
    # 支持命令行指定端口
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
