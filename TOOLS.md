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

Add whatever helps you do your job. This is your cheat sheet.
