---
name: sec-audit
description: 对 OpenClaw 部署进行只读安全审计，检测环境泄露、认证配置、恶意 Skill 等已知风险和漏洞。
metadata:
  version: "1.0.0"
  author: "nx4dm1n"
  category: "security"
  tags: ["security", "audit", "safety", "compliance"]
---

# sec-audit - OpenClaw 安全审计

## 功能概述

sec-audit 是一个只读安全审计工具，用于检测 OpenClaw 部署中的安全风险：

1. **环境泄露检测** - 扫描 `.env`、配置文件中的密钥、token、密码
2. **认证配置审计** - 检查 Gateway 配置、权限设置是否合理
3. **恶意 Skill 识别** - 检测已安装 skill 中的可疑行为模式
4. **已知漏洞检查** - 对照 CVE 数据库检查组件版本

## 审计范围

### 1. 凭据泄露扫描
- 扫描文件: `.env`, `.env.*`, `config.*`, `*.json`, `*.yaml`, `*.yml`
- 检测模式:
  - API keys: `api[_-]?key`, `apikey`, `api_token`
  - 私钥: `private[_-]?key`, `secret`, `password`
  - Token: `token`, `auth_token`, `access_token`, `github_token`
  - 密码: `passwd`, `pwd`, `credential`

### 2. 配置安全检查
- Gateway 配置权限 (`openclaw.json`)
- 技能权限设置 (过宽的 `network`, `shell`, `filesystem` 权限)
- 调试模式是否开启
- 日志级别设置

### 3. Skill 安全分析
- 检查 skill 的 metadata 完整性
- 分析权限组合 (如 `network` + `shell` = 高危)
- 检测可疑的网络请求模式
- 识别已知的恶意 skill 签名

### 4. 系统环境检查
- 文件权限检查 (如 `.ssh` 目录权限)
- 开放的端口检查
- Docker/container 配置检查
- 持久化机制检查 (cron, systemd)

## 使用方法

### 完整审计
```
运行 sec-audit 完整扫描
```

### 特定范围审计
```
只检查凭据泄露: sec-audit --scope credentials
只检查 skill 安全: sec-audit --scope skills
只检查配置: sec-audit --scope config
```

## 风险等级

| 等级 | 说明 | 示例 |
|------|------|------|
| 🔴 Critical | 可能导致完全控制或数据泄露 | 硬编码密码、RCE漏洞 |
| 🟠 High | 可能读取敏感数据或提升权限 | 过度权限、密钥泄露 |
| 🟡 Medium | 有限的数据访问或欺骗风险 | XSS、日志中的PII |
| 🟢 Low | 影响较小，需要特定条件 | 详细错误信息 |

## 输出格式

审计报告包含:
1. 执行摘要 (风险统计)
2. 详细发现 (按等级分类)
3. 修复建议
4. 合规性评分

## 注意事项

- **只读操作**: sec-audit 不会修改任何文件或配置
- **本地执行**: 所有检查都在本地完成，不会上传数据
- **定期运行**: 建议每周或每次安装新 skill 后运行

## 参考资料

- ClawHub: https://clawhub.ai/skills/nx4dm1n/sec-audit
- 安全最佳实践: https://docs.openclaw.ai/security
