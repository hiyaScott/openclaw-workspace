# 文件传输服务部署说明

## 架构
- **前端**: GitHub Pages 静态页面
- **后端**: Python Flask API（需要独立部署）

## 部署步骤

### 1. 安装依赖

```bash
cd file-transfer-api
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
export GITHUB_TOKEN="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"
```

或创建 `.env` 文件：
```
GITHUB_TOKEN=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
```

### 3. 运行服务

**开发模式**:
```bash
python app.py
```

**生产模式** (使用gunicorn):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. 更新前端API地址

编辑 `portfolio-blog/file-transfer/index.html`，修改：
```javascript
const API_BASE = 'http://localhost:5000/api';  // 改为你的API地址
```

如果使用公网服务器，改为：
```javascript
const API_BASE = 'https://your-server.com/api';
```

## 部署选项

### 选项A: 本地运行（最简单）

在你的电脑上运行 Flask 服务：
```bash
python file-transfer-api/app.py
```

然后访问 `http://localhost:5000` 测试。

### 选项B: 使用内网穿透（推荐）

使用 ngrok 或类似工具暴露本地服务：

```bash
# 安装 ngrok
# 运行 Flask
python app.py &

# 暴露到公网
ngrok http 5000
```

获取 ngrok 提供的公网 URL，更新到前端。

### 选项C: 部署到云服务器

1. 购买 VPS (阿里云、腾讯云等)
2. 上传代码
3. 使用 systemd 或 docker 运行服务
4. 配置 Nginx 反向代理 + SSL

### 选项D: Serverless (Cloudflare Workers)

创建一个 worker 处理上传请求，无需维护服务器。

## 文件存储结构

上传的文件会存储在 GitHub 仓库：
```
scott-portfolio/
├── transfers/
│   ├── from-scott/
│   │   └── 2026-03-15/
│   │       └── filename.zip
│   └── from-jetton/
│       └── 2026-03-15/
│           └── another-file.pdf
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/upload` | POST | 上传文件 |
| `/api/list` | GET | 列出文件 |
| `/api/download` | GET | 获取下载链接 |
| `/api/delete` | POST | 删除文件 |

## 安全注意

1. Token 不要提交到 GitHub
2. 生产环境使用 HTTPS
3. 考虑添加访问控制（密码或 IP 白名单）
4. 大文件限制在 100MB 以内

## 测试

```bash
# 检查API状态
curl http://localhost:5000/api/health

# 上传测试
curl -X POST -F "file=@test.txt" -F "sender=scott" http://localhost:5000/api/upload

# 列出文件
curl "http://localhost:5000/api/list?sender=jetton"
```
