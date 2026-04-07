# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## AI工具API配置

### 配置文件位置
- **环境变量文件**: `/root/.openclaw/workspace/.env`
- **模板文件**: `/root/.openclaw/workspace/.env.example`
- **读取脚本**: `/root/.openclaw/workspace/skills/ai-shortfilm-pipeline/scripts/api_config.py`

### 配置项

| 变量名 | 用途 | 获取方式 |
|--------|------|----------|
| `JIMENG_ACCESS_KEY` | 即梦AI访问密钥 | https://console.volcengine.com/iam/keymanagement/ |
| `JIMENG_SECRET_KEY` | 即梦AI安全密钥 | 同上 |
| `DMXAPI_TOKEN` | DMXAPI Token (海螺/可灵等) | https://www.dmxapi.cn/ |

### 使用方法

**Python脚本中读取**：
```python
from skills.ai-shortfilm-pipeline.scripts.api_config import get_dmxapi_token, get_jimeng_keys

# 获取DMXAPI Token
token = get_dmxapi_token()

# 获取即梦AI密钥
ak, sk = get_jimeng_keys()
```

**检查配置状态**：
```bash
cd /root/.openclaw/workspace
python3 skills/ai-shortfilm-pipeline/scripts/api_config.py
```

### 安全说明
- `.env` 文件已被添加到 `.gitignore`，不会被提交到Git
- 不要将真实token硬编码在代码中
- 如需分享配置，使用 `.env.example` 模板文件

---

## GitHub 推送指南

### 问题：无交互式终端的 Git 推送

在 headless 环境（无 TTY）中，`git push` 无法交互式输入用户名密码。

### ❌ 已失效的方法

| 方法 | 状态 | 原因 |
|------|------|------|
| URL 嵌入 token | ❌ 失效 | `https://user:token@github.com/...` 被 GitHub 禁用 |
| 环境变量 GIT_USERNAME | ❌ 失效 | Git 不再支持 |
| gh auth login | ❌ 复杂 | 需要交互式浏览器授权 |

### ✅ 可靠方法：Git Credential Store

**步骤：**

```bash
# 1. 启用 credential store
git config credential.helper store

# 2. 存储凭据（一次性）
echo -e "protocol=https\nhost=github.com\nusername=hiyascott\npassword=YOUR_TOKEN\n" | \
  git credential-store --file ~/.git-credentials store

# 3. 推送
git push origin master
```

**验证存储：**
```bash
cat ~/.git-credentials
# 输出: https://hiyascott:YOUR_TOKEN@github.com
```

### 备用方法：SSH 密钥（推荐长期配置）

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "your@email.com"

# 添加到 GitHub
gh ssh-key add ~/.ssh/id_ed25519.pub --title "OpenClaw Server"

# 使用 SSH 推送
git remote set-url origin git@github.com:hiyaScott/openclaw-workspace.git
git push origin master
```

### Token 要求

- **类型**: Personal Access Token (classic)
- **权限**: 必须勾选 `repo` (完整仓库访问)
- **有效期**: 建议设置不过期，或及时更新

---

Add whatever helps you do your job. This is your cheat sheet.
