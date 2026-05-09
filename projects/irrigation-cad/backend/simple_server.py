#!/usr/bin/env python3
"""
花园灌溉CAD设计系统 - 纯Python HTTP API服务器
不依赖uvicorn/fastapi，使用http.server + threading
"""

import os
import sys
import json
import cgi
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.dxf_parser import parse_dxf_from_upload
from core.sprinkler_layout import (
    Point, Polygon, PlantType, SprinklerType,
    design_irrigation_zone, calculate_valve_groups,
    estimate_materials, SPRINKLER_CONFIGS
)

OUTPUT_DIR = "/tmp/irrigation-cad-outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class CORSHandler(BaseHTTPRequestHandler):
    """支持CORS的请求处理器"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """简化日志"""
        print(f"[{threading.current_thread().name}] {args[0]} {args[1]} - {args[2]}")


# 静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

class APIHandler(CORSHandler):
    """API请求处理器 + 静态文件服务"""
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # API 路由
        if path == '/' or path == '/api/health':
            self.send_json({
                "status": "ok",
                "service": "花园灌溉CAD设计系统",
                "version": "0.1.0"
            })
        elif path == '/api/config':
            self.send_config()
        elif path.startswith('/api/'):
            self.send_error(404, "API Not Found")
        else:
            # 静态文件服务
            self.serve_static(path)
    
    def serve_static(self, path):
        """服务静态文件"""
        if path == '/':
            path = '/test-interface.html'
        
        # 安全检查：防止目录遍历
        safe_path = os.path.normpath(path).lstrip('/')
        if '..' in safe_path:
            self.send_error(403, "Forbidden")
            return
        
        file_path = os.path.join(FRONTEND_DIR, safe_path)
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_error(404, "Not Found")
            return
        
        # MIME 类型
        mime_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
        }
        ext = os.path.splitext(file_path)[1].lower()
        content_type = mime_types.get(ext, 'application/octet-stream')
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")
    
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == '/api/parse-dxf':
            self.handle_parse_dxf()
        elif path == '/api/design':
            self.handle_design()
        else:
            self.send_error(404, "Not Found")
    
    def send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def handle_parse_dxf(self):
        """处理DXF文件上传和解析"""
        try:
            # 读取multipart/form-data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_json({"error": "需要 multipart/form-data"}, 400)
                return
            
            # 解析multipart数据
            boundary = content_type.split('boundary=')[1].strip()
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                self.send_json({"error": "空文件"}, 400)
                return
            
            # 读取原始数据
            raw_data = self.rfile.read(content_length)
            
            # 解析multipart
            parts = raw_data.split(b'--' + boundary.encode())
            
            file_content = None
            filename = "upload.dxf"
            
            for part in parts:
                if b'Content-Disposition' in part:
                    # 提取文件名
                    header_end = part.find(b'\r\n\r\n')
                    if header_end > 0:
                        header = part[:header_end].decode('utf-8', errors='ignore')
                        if 'filename=' in header:
                            # 提取文件名
                            fname_start = header.find('filename="') + 10
                            fname_end = header.find('"', fname_start)
                            filename = header[fname_start:fname_end]
                        
                        # 提取文件内容
                        file_content = part[header_end + 4:]
                        # 去掉末尾的\r\n
                        if file_content.endswith(b'\r\n'):
                            file_content = file_content[:-2]
                        break
            
            if not file_content:
                self.send_json({"error": "未找到文件"}, 400)
                return
            
            # 解析DXF
            result = parse_dxf_from_upload(file_content, filename)
            
            self.send_json(result.to_dict())
            
        except Exception as e:
            print(f"解析错误: {e}")
            import traceback
            traceback.print_exc()
            self.send_json({"error": f"解析错误: {str(e)}"}, 500)
    
    def handle_design(self):
        """处理灌溉设计请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json({"error": "空请求"}, 400)
                return
            
            body = self.rfile.read(content_length)
            request = json.loads(body.decode('utf-8'))
            
            # TODO: 实现设计逻辑
            self.send_json({
                "status": "not_implemented",
                "message": "设计API待实现"
            })
            
        except Exception as e:
            self.send_json({"error": f"设计错误: {str(e)}"}, 500)
    
    def send_config(self):
        """发送配置信息"""
        configs = {}
        for st, cfg in SPRINKLER_CONFIGS.items():
            configs[st.value] = {
                "name": cfg.name,
                "price": cfg.price,
                "install_fee": cfg.install_fee,
                "flow": cfg.flow,
                "unit": cfg.unit,
                "spray_radius": cfg.spray_radius,
                "spacing": cfg.spacing,
                "coverage_pattern": cfg.coverage_pattern
            }
        self.send_json({
            "sprinkler_types": configs,
            "plant_types": ["shrub", "lawn", "flower"],
            "pipe_sizes": [25, 32],
            "water_source_flows": [2.5, 3.0, 3.5]
        })


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """多线程HTTP服务器"""
    daemon_threads = True
    allow_reuse_address = True


def run_server(host='0.0.0.0', port=8000):
    """启动服务器"""
    server = ThreadedHTTPServer((host, port), APIHandler)
    print(f"🚀 灌溉CAD设计系统启动: http://{host}:{port}")
    print(f"📁 前端页面: http://{host}:{port}/test-interface.html")
    print(f"📁 解析器就绪: ezdxf + numpy")
    print(f"🔧 端点:")
    print(f"   GET  /                  - 前端测试页面")
    print(f"   GET  /api/health     - 健康检查")
    print(f"   GET  /api/config     - 喷头配置")
    print(f"   POST /api/parse-dxf  - 解析DXF文件")
    print(f"   POST /api/design     - 生成设计方案")
    print(f"\n按 Ctrl+C 停止\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ 服务器停止")
        server.shutdown()


if __name__ == '__main__':
    run_server()
