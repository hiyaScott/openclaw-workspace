---
name: openviking
description: OpenViking 上下文数据库集成 - 为 OpenClaw 提供高级语义搜索和知识管理能力。支持文档索引、语义检索、分层上下文和自动摘要。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "triggers": ["openviking", "viking", "语义搜索", "知识库", "文档索引"],
      },
  }
---

# OpenViking Skill

OpenViking 是火山引擎开源的 AI Agent 上下文数据库，为 OpenClaw 提供以下能力：

## 新增能力

### 1. 语义搜索与 RAG
- **语义文档搜索** - 基于向量相似度的智能检索
- **分层上下文** - L0摘要 / L1概览 / L2全文，按需加载节省 Token
- **多格式支持** - PDF、Word、PPT、Excel、Markdown、HTML、EPUB 等

### 2. 知识管理
- **文档索引** - 自动提取和索引文档内容
- **自动摘要** - VLM 自动生成文档摘要和概览
- **目录浏览** - 类似文件系统的资源组织方式

### 3. 记忆增强
- **长期记忆存储** - 持久化存储对话历史和关键信息
- **智能检索** - 自动提取对话中的长期记忆
- **跨会话记忆** - 不同会话间共享知识库

## 使用方法

### 初始化
```bash
# 初始化 OpenViking 数据库
python3 /root/.openclaw/workspace/skills/openviking/viking.py init
```

### 添加文档
```bash
# 添加单个文件
python3 /root/.openclaw/workspace/skills/openviking/viking.py add /path/to/file.pdf

# 批量添加目录
python3 /root/.openclaw/workspace/skills/openviking/viking.py add-dir /path/to/docs
```

### 搜索
```bash
# 语义搜索
python3 /root/.openclaw/workspace/skills/openviking/viking.py search "关键词" --limit 5
```

### 浏览
```bash
# 列出资源
python3 /root/.openclaw/workspace/skills/openviking/viking.py ls

# 获取摘要
python3 /root/.openclaw/workspace/skills/openviking/viking.py abstract <uri>

# 读取全文
python3 /root/.openclaw/workspace/skills/openviking/viking.py read <uri>
```

## 配置说明

配置文件位置：`~/.openviking/ov.conf`

需要配置 embedding 和 VLM API 才能使用完整功能。

### 获取 API Key

OpenViking 需要以下 API 之一：

**选项 1: OpenAI API (推荐)**
- 访问 https://platform.openai.com/api-keys
- 创建 API Key
- 编辑 `~/.openviking/ov.conf` 填入 `api_key`

**选项 2: NVIDIA NIM API (免费)**
- 访问 https://build.nvidia.com/
- 注册账号并生成 API Key
- 参考配置：
```json
{
  "embedding": {
    "dense": {
      "provider": "openai",
      "api_base": "https://integrate.api.nvidia.com/v1",
      "api_key": "你的NVIDIA_API_KEY",
      "model": "nvidia/nv-embed-v1",
      "dimension": 4096
    }
  },
  "vlm": {
    "provider": "openai",
    "api_base": "https://integrate.api.nvidia.com/v1",
    "api_key": "你的NVIDIA_API_KEY",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
```

### 当前状态

- ✅ OpenViking Python 库已安装 (v0.2.5)
- ✅ Skill 文件已创建
- ⚠️ 等待 API Key 配置以启用完整功能

## 与原有记忆系统的关系

- **原有 memory_search/memory_get** - 继续可用，用于轻量级、快速的本地记忆检索
- **OpenViking** - 用于大规模文档库、需要语义理解和复杂检索的场景

两者互补，可以根据任务需求选择使用。
