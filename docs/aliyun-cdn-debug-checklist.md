# 阿里云 CDN 配置检查清单

## 检查步骤

### 1. CDN 域名基础配置
**路径：** 阿里云控制台 → CDN → 域名管理 → 点击 resource.cornpup.com

| 检查项 | 正确配置 | 你的配置 |
|--------|---------|---------|
| 加速域名 | resource.cornpup.com | ? |
| 业务类型 | 图片小文件 | ? |
| 加速区域 | 仅中国内地 | ? |

### 2. 源站配置（最关键）
**路径：** CDN 域名详情 → 基本配置 → 源站信息

| 检查项 | 正确配置 | 你的配置 |
|--------|---------|---------|
| 源站类型 | 源站域名 / IP | ? |
| 源站地址 | 47.242.202.209 | ? |
| 端口 | 80 或 443 | ? |
| 回源 Host | resource.cornpup.com | ? |

⚠️ **常见错误：**
- 源站类型选成了"OSS域名"（应该是IP或源站域名）
- 回源 Host 没设置或设置错了
- 端口选错了（CDN用443回源但服务器没配SSL）

### 3. DNS 解析配置
**路径：** 阿里云控制台 → 云解析DNS → 找到 cornpup.com 域名

查找记录：
| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| resource | CNAME | xxx.cloudfront.com 或 xxx.alicdn.com |

### 4. HTTPS 配置
**路径：** CDN 域名详情 → HTTPS配置

| 检查项 | 状态 |
|--------|------|
| HTTPS 安全加速 | 开启 / 关闭 ? |
| 强制跳转 HTTPS | 开启 / 关闭 ? |

### 5. 缓存配置
**路径：** CDN 域名详情 → 缓存配置

检查是否有过于激进的缓存规则导致旧内容。

### 6. 诊断工具
**路径：** CDN 域名详情 → 诊断工具

运行"CDN 检测"，查看：
- DNS 解析是否正常
- CDN 节点是否生效
- 回源是否正常

---

## 快速诊断命令（服务器上运行）

```bash
# 1. 检查域名解析
dig resource.cornpup.com

# 2. 测试 CDN 节点连通性
curl -I http://resource.cornpup.com

# 3. 直接测试源站（绕过CDN）
curl -H "Host: resource.cornpup.com" http://47.242.202.209/

# 4. 检查 nginx 配置
cat /www/server/panel/vhost/nginx/www.cornpup.com.conf | grep server_name
```

---

## 预期结果

**如果一切正常：**
1. `dig` 应该返回阿里云 CDN 的 CNAME
2. `curl -I` 应该返回 200 而不是 502
3. 直接测试源站应该返回 200
4. nginx 配置应该包含 resource.cornpup.com

**哪个步骤出错，问题就在哪里。**
