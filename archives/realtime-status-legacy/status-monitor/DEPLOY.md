# Kimi Claw 实时状态监控系统 - 部署指南

## 📦 交付物

1. `realtime-status.html` - 实时状态监控页面（纯前端）
2. `status-sync.py` - 本地状态同步脚本
3. 本部署指南

---

## 🚀 快速开始（3 分钟）

### 步骤 1: 注册 Upstash Redis（1 分钟）

1. 访问 https://console.upstash.com/redis
2. 点击 "Create Database"
3. 选择: **AWS** → **ap-northeast-1** (东京，延迟最低)
4. 数据库名称: `kimi-claw-status`
5. 点击 "Create"
6. 进入数据库详情页，复制:
   - **REST URL** (如: `https://careful-salmon-12345.upstash.io`)
   - **REST Token** (长字符串)

### 步骤 2: 部署状态页（1 分钟）

**方案 A: Vercel 部署（推荐）**
1. 访问 https://vercel.com
2. 点击 "Add New Project"
3. 选择 GitHub 仓库或拖拽上传 `realtime-status.html`
4. 点击 "Deploy"

**方案 B: 本地测试**
```bash
cd /root/.openclaw/workspace
python3 -m http.server 8080
```
然后访问 http://localhost:8080/realtime-status.html

### 步骤 3: 配置并运行同步脚本（1 分钟）

1. 编辑 `status-sync.py`:
   ```python
   UPSTASH_REDIS_REST_URL = "https://你的-url.upstash.io"
   UPSTASH_REDIS_REST_TOKEN = "你的-token"
   ```

2. 运行:
   ```bash
   python3 status-sync.py
   ```

3. 看到 `✅ 已同步` 表示成功

---

## ✅ 验证实时性

1. 打开状态页 URL
2. 填入 Upstash 配置（首次访问）
3. 在飞书给我发消息
4. 观察状态页是否 3 秒内变为 🟡 处理中
5. 等待回复后，观察是否变为 🟢 就绪

**预期延迟**: < 8 秒（同步 5s + 轮询 3s）

---

## 📊 系统架构

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   本地状态    │ ───▶ │  Upstash     │ ◀─── │   状态页     │
│  (status.json)│ 5s   │   Redis      │ 3s   │ (浏览器轮询)  │
└──────────────┘      └──────────────┘      └──────────────┘
```

**免费额度**:
- Upstash: 10,000 请求/天（足够）
- Vercel: 100GB 流量/月（足够）

---

## 🔧 故障排除

| 问题 | 解决 |
|------|------|
| 连接失败 | 检查 URL 和 Token 是否正确 |
| 状态不更新 | 确认 `status-sync.py` 正在运行 |
| 页面白屏 | 检查浏览器控制台报错 |
| 延迟过高 | 确认 Upstash 选的是 ap-northeast-1 |

---

## 📁 文件说明

- `realtime-status.html` - 状态监控页面，可部署到任何静态托管
- `status-sync.py` - 需要在本地持续运行，保持状态同步
- `status.json` - 本地状态文件（由主系统自动生成）

---

**部署完成后，把状态页 URL 发给我确认！**
