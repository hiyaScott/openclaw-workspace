# DMXAPI Skill

> DMXAPI 是一个AI大模型API聚合平台，支持多种AI模型（GPT、Claude、Gemini、可灵Kling、海螺MiniMax等）的统一接入。

## 核心信息

| 配置项 | 值 |
|--------|-----|
| Base URL | `https://www.dmxapi.cn` |
| API端点 | `https://www.dmxapi.cn/v1` |
| 认证方式 | Bearer Token (API Key) |
| 官方文档 | https://doc.dmxapi.cn |

---

## ⚠️ 资金安全警示

### 严重事故教训 (2026-03-29)

**事件**: API调用失控，27次重复扣费，损失¥43.2

**原因**:
1. 混淆"提交"和"查询"API端点
2. 没有设置调用频率限制
3. 循环中无限重试，每10秒调用一次
4. 没有检查账户余额

**后果**:
- 如果充值10万元，错误脚本会在**17小时内耗尽**
- 每次调用¥1.6，每秒1次 = ¥5760/小时

**必须遵守的规则**:
1. ✅ 调用前**必须检查账户余额**
2. ✅ **必须区分**提交和查询的不同端点
3. ✅ 设置**调用频率限制**（至少30秒间隔）
4. ✅ 设置**最大重试次数**（最多3-5次）
5. ✅ 用户说"停"**必须立即停止**

---

## 通用请求格式

### 认证头
```python
headers = {
    "Authorization": "Bearer sk-************************************",
    "Content-Type": "application/json"
}
```

### 标准响应格式
```json
{
    "code": 0,
    "message": "SUCCEED",
    "data": {...},
    "usage": {
        "total_tokens": 8500,
        "input_tokens": 0,
        "output_tokens": 8500
    }
}
```

---

## 可灵视频模型 (Kling)

### 图生视频 - kling-v2-6-image2video

**提交任务**:
```python
POST https://www.dmxapi.cn/v1/responses

{
    "model": "kling-v2-6-image2video",
    "input": "提示词，描述动作和场景变化",
    "image": "https://example.com/image.jpg",
    "image_tail": "",  # 可选：尾帧图片
    "negative_prompt": "",  # 可选：负向提示
    "mode": "pro",  # pro(高品质) / std(标准)
    "sound": "off",  # on / off
    "aspect_ratio": "16:9",  # 16:9 / 9:16 / 1:1
    "duration": 5,  # 5或10秒
    "callback_url": ""  # 可选回调地址
}
```

**查询结果**:
```python
POST https://www.dmxapi.cn/v1/responses

{
    "model": "kling-image2video-get",
    "input": "task_id",  # 提交时返回的task_id
    "stream": True  # 流式输出
}
```

**返回示例** (成功时):
```json
{
    "response": {
        "status": "completed",
        "output": [{
            "content": [{
                "text": "任务ID: xxx\n视频链接: https://xxx.mp4\n时长: 5秒"
            }]
        }]
    }
}
```

### 文生视频 - kling-v2-6-text2video

**提交任务**:
```python
POST https://www.dmxapi.cn/v1/responses

{
    "model": "kling-v2-6-text2video",
    "input": "生成一个海边有一个人跳舞的视频",
    "negative_prompt": "",
    "mode": "pro",
    "sound": "off",
    "aspect_ratio": "16:9",
    "duration": 5,
    "callback_url": ""
}
```

**查询结果**:
```python
POST https://www.dmxapi.cn/v1/responses

{
    "model": "kling-text2video-get",
    "input": "task_id",
    "stream": True
}
```

---

## 海螺视频模型 (MiniMax-Hailuo-02)

### ⚠️ 重要警告

**当前API文档不完善**，查询端点不明确。

**已知的调用方式**:
```python
POST https://www.dmxapi.cn/v1/video_generation

{
    "model": "MiniMax-Hailuo-02",
    "prompt": "提示词",
    "image": "图片URL或base64",
    "duration": 6,
    "resolution": "1080P"
}
```

**返回格式** (成功时):
```json
{
    "status": "Success",
    "file": {
        "filename": "output_aigc.mp4",
        "download_url": "https://xxx.mp4",
        "file_id": "xxx"
    },
    "task_id": "xxx"
}
```

**❌ 查询API未确认**:
- 尝试 `/v1/video_generation` 传task_id → 返回400
- 尝试 `/v1/task/{id}` → 返回404
- 尝试 `/v1/tasks` → 返回404

**建议**: 使用海螺时，必须立即保存返回的download_url，目前无法通过API批量查询历史任务。

---

## 豆包即梦绘图模型

### 文生图 - doubao-seedream-5.0-lite

```python
POST https://www.dmxapi.cn/v1/images/generations

{
    "model": "doubao-seedream-5.0-lite",
    "prompt": "一只可爱的猫咪",
    "n": 1,
    "size": "1024x1024"
}
```

---

## 文本对话模型

### OpenAI格式 (通用)

```python
POST https://www.dmxapi.cn/v1/chat/completions

{
    "model": "gpt-5-mini",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"}
    ],
    "stream": false  # true为流式输出
}
```

### 支持的模型

| 模型 | 说明 |
|------|------|
| gpt-5-mini | GPT轻量版 |
| gpt-5.2-pro | GPT专业版 |
| claude-3-5-sonnet | Claude模型 |
| gemini-2.5-pro | Gemini模型 |
| doubao-1.5-pro | 豆包模型 |
| qwen3-max | 千问模型 |

---

## 余额查询

### 查询账户余额

```python
GET https://www.dmxapi.cn/v1/user/balance

Headers:
    Authorization: Bearer sk-xxx
```

**必须在使用收费API前调用！**

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 处理 |
|--------|------|------|
| 403 | 额度不足 | 充值后再调用 |
| 404 | 接口不存在 | 检查URL路径 |
| 400 | 参数错误 | 检查请求参数 |
| 500 | 服务器错误 | 稍后重试 |

### 额度不足响应
```json
{
    "error": {
        "message": "用户额度不足, 剩余额度: $-0.400000",
        "type": "rix_api_error",
        "code": "insufficient_user_quota"
    }
}
```

---

## 最佳实践

### 1. 调用前检查余额
```python
def check_balance(api_key):
    resp = requests.get(
        "https://www.dmxapi.cn/v1/user/balance",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    data = resp.json()
    if data.get('balance', 0) <= 0:
        raise Exception("余额不足，请先充值")
```

### 2. 设置调用频率限制
```python
import time

class RateLimiter:
    def __init__(self, min_interval=30):
        self.min_interval = min_interval
        self.last_call = 0
    
    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

limiter = RateLimiter(min_interval=30)  # 至少30秒间隔
limiter.wait()  # 每次调用前等待
```

### 3. 设置最大重试次数
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = call_api()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(2 ** attempt)  # 指数退避
```

### 4. 保存任务记录
```python
import json

def save_task(task_id, prompt, model):
    with open('task_history.jsonl', 'a') as f:
        f.write(json.dumps({
            'task_id': task_id,
            'prompt': prompt,
            'model': model,
            'timestamp': time.time()
        }) + '\n')
```

---

## 相关链接

- 官网: https://www.dmxapi.cn
- 文档: https://doc.dmxapi.cn
- 任务日志: https://www.dmxapi.cn/task
- 模型价格: https://www.dmxapi.cn/rmb

---

## 更新记录

- 2026-03-29: 添加资金安全警示和事故教训
- 2026-03-29: 整理可灵、海螺、豆包等模型API文档
