# 海螺(Hailuo) API 技术参考

> DMXAPI 海螺视频生成服务的详细API文档，包含文生视频、图生视频、首尾帧生成的完整技术规范

---

## 一、API端点概览

| 功能 | 端点 | 方法 |
|------|------|------|
| 提交任务 | `https://www.dmxapi.cn/v1/video_generation` | POST |
| 查询任务 | `https://www.dmxapi.cn/v1/query/video_generation` | GET |
| 下载视频 | `https://www.dmxapi.cn/v1/files/retrieve` | GET |

---

## 二、支持的模型

| 模型名称 | 说明 | 适用场景 |
|----------|------|----------|
| `MiniMax-Hailuo-2.3` | 最新版本，支持更高质量的视频生成 | 优先使用 |
| `MiniMax-Hailuo-2.3-Fast` | 快速版本，生成速度更快 | 快速预览 |
| `MiniMax-Hailuo-02` | 基础版本，支持512P分辨率 | 兼容性场景 |

---

## 三、文生视频 API

### 3.1 提交任务

**请求示例**：
```python
import requests
import json

API_TOKEN = "sk-*******************************************"
url = "https://www.dmxapi.cn/v1/video_generation"

payload = {
    "model": "MiniMax-Hailuo-2.3",
    
    # 提示词（最大2000字符）
    # 支持运镜指令语法：[指令]
    "prompt": "A man picks up a book [Pedestal up], then reads [Static shot].",
    
    # 视频时长（秒）
    # MiniMax-Hailuo-2.3: 6/10秒（768P）或 6秒（1080P）
    "duration": 6,
    
    # 分辨率：768P (默认), 1080P
    "resolution": "768P",
    
    # 可选参数
    # "prompt_optimizer": true,    # 是否自动优化prompt（默认: true）
    # "fast_pretreatment": false,  # 是否缩短优化耗时（默认: false）
    # "aigc_watermark": false,     # 是否添加水印（默认: false）
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"{API_TOKEN}"
}

response = requests.post(url, json=payload, headers=headers)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

**成功响应**：
```json
{
    "task_id": "335492703728059",
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
```

### 3.2 查询任务

**请求示例**：
```python
base_url = "https://www.dmxapi.cn"
endpoint = "/v1/query/video_generation"
task_id = "335492703728059"
token = "sk-*******************************************"

url = f"{base_url}{endpoint}?task_id={task_id}"
headers = {"Authorization": f"{token}"}

response = requests.get(url, headers=headers)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

**成功响应**：
```json
{
    "status": "Success",
    "file_id": "335560631603474",
    "task_id": "335558695837779",
    "base_resp": {
        "status_msg": "success",
        "status_code": 0
    },
    "video_width": 1366,
    "video_height": 768
}
```

**状态说明**：
- `Processing` - 任务正在处理中
- `Success` - 任务已完成
- `Failed` - 任务失败

### 3.3 下载视频

**请求示例**：
```python
BASE_URL = "https://www.dmxapi.cn"
FILE_ID = "335560631603474"
TASK_ID = "335558695837779"
TOKEN = "sk-*******************************************"

url = f"{BASE_URL}/v1/files/retrieve"
params = {
    "file_id": FILE_ID,
    "task_id": TASK_ID
}
headers = {"Authorization": f"{TOKEN}"}

response = requests.get(url, params=params, headers=headers)
result = response.json()

# 获取下载链接
download_url = result["file"]["download_url"]
print(f"Download URL: {download_url}")

# 下载视频
video_response = requests.get(download_url)
with open("output.mp4", "wb") as f:
    f.write(video_response.content)
```

**成功响应**：
```json
{
    "file": {
        "file_id": 335560631603474,
        "bytes": 0,
        "created_at": 1763477381,
        "filename": "output_aigc.mp4",
        "purpose": "video_generation",
        "download_url": "https://public-cdn-video-data-algeng.oss-cn-wulanchabu.aliyuncs.com/..."
    },
    "base_resp": {
        "status_code": 0,
        "status_msg": "success"
    }
}
```

**⚠️ 注意**：下载链接有有效期限制，请及时下载

---

## 四、图生视频 API

### 4.1 提交任务

**请求示例**：
```python
url = "https://www.dmxapi.cn/v1/video_generation"
headers = {
    "Authorization": "sk-*******************************************",
    "Content-Type": "application/json"
}

data = {
    "model": "MiniMax-Hailuo-2.3",
    
    # 提示词（支持运镜指令）
    "prompt": "A mouse runs toward the camera, smiling and blinking.",
    
    # 首帧图片（必需）
    # 支持公网URL或Base64编码
    # 要求：JPG/JPEG/PNG/WebP, <20MB, 短边>300px
    "first_frame_image": "https://cdn.hailuoai.com/.../image.jpeg",
    
    # 视频时长（秒）
    # 768P: 6或10秒, 1080P: 6秒
    "duration": 6,
    
    # 分辨率
    "resolution": "768P",
    
    # 可选参数
    # "prompt_optimizer": True,
    # "aigc_watermark": False
}

response = requests.post(url, headers=headers, json=data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

**模型与时长对应表**：

| 模型 | 6秒 | 10秒 |
|------|-----|------|
| MiniMax-Hailuo-2.3 | 768P(默认)/1080P | 768P(默认) |
| MiniMax-Hailuo-2.3-Fast | 768P(默认)/1080P | 768P(默认) |
| MiniMax-Hailuo-02 | 512P/768P(默认)/1080P | 512P/768P |

---

## 五、首尾帧生成 API

### 5.1 提交任务

**请求示例**：
```python
url = "https://www.dmxapi.cn/v1/video_generation"
headers = {
    "Content-Type": "application/json",
    "Authorization": "sk-*******************************************"
}

payload = {
    # 模型（首尾帧生成专用）
    "model": "MiniMax-Hailuo-02",
    
    # 视频描述（支持运镜指令）
    "prompt": "A little girl grow up.",
    
    # 首帧图片（可选但建议提供）
    "first_frame_image": "https://filecdn.minimax.chat/.../first.jpeg",
    
    # 尾帧图片（可选但建议提供）
    "last_frame_image": "https://filecdn.minimax.chat/.../last.jpeg",
    
    # 时长：768P支持6/10秒，1080P支持6秒
    "duration": 6,
    
    # 分辨率：768P(默认) 或 1080P
    "resolution": "768P"
}

response = requests.post(url, json=payload, headers=headers)
```

**图片要求**：
- 格式：JPG, JPEG, PNG, WebP
- 大小：小于 20MB
- 尺寸：短边 > 300px，长宽比在 2:5 ~ 5:2 之间
- ⚠️ 首尾帧尺寸不一致时，模型会参考首帧对尾帧进行裁剪
- ⚠️ 首尾帧生成不支持 512P 分辨率

---

## 六、运镜指令详解

### 6.1 支持的15种运镜指令

| 类别 | 指令 | 效果 |
|------|------|------|
| **左右移** | `[左移]`, `[右移]` | 摄像机左右平移 |
| **左右摇** | `[左摇]`, `[右摇]` | 摄像机左右旋转 |
| **推拉** | `[推进]`, `[拉远]` | 摄像机前后移动 |
| **升降** | `[上升]`, `[下降]` | 摄像机上下移动 |
| **上下摇** | `[上摇]`, `[下摇]` | 摄像机俯仰旋转 |
| **变焦** | `[变焦推近]`, `[变焦拉远]` | 镜头变焦 |
| **其他** | `[晃动]`, `[跟随]`, `[固定]` | 特殊效果 |

### 6.2 运镜指令使用规则

**组合运镜**：
- 同一组 `[]` 内的多个指令会同时生效
- 如：`[左摇,上升]`（建议不超过3个）

**顺序运镜**：
- prompt中前后出现的指令会依次生效
- 如：`"...[推进], 然后...[拉远]"`

**自然语言**：
- 也支持通过自然语言描述运镜
- 但使用标准指令能获得更准确的响应

**使用建议**：
- 单个场景建议使用 1-2 个运镜指令
- 组合运镜时建议不超过 3 个指令
- 过多指令可能影响视频质量

---

## 七、完整工作流程示例

### 7.1 图生视频完整代码

```python
import requests
import json
import time

# ========== 配置 ==========
API_TOKEN = "sk-*******************************************"
BASE_URL = "https://www.dmxapi.cn"

# ========== 1. 提交任务 ==========
def submit_task():
    url = f"{BASE_URL}/v1/video_generation"
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "prompt": "A robot gently holds a flower [推进], then looks at it with soft eyes [固定].",
        "first_frame_image": "https://example.com/robot_with_flower.jpg",
        "duration": 6,
        "resolution": "768P"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    if result["base_resp"]["status_code"] == 0:
        return result["task_id"]
    else:
        raise Exception(f"提交失败: {result}")

# ========== 2. 查询任务 ==========
def query_task(task_id, max_retries=30, interval=10):
    url = f"{BASE_URL}/v1/query/video_generation?task_id={task_id}"
    headers = {"Authorization": API_TOKEN}
    
    for i in range(max_retries):
        response = requests.get(url, headers=headers)
        result = response.json()
        
        status = result.get("status")
        if status == "Success":
            return result["file_id"]
        elif status == "Failed":
            raise Exception(f"任务失败: {result}")
        
        print(f"等待中... ({i+1}/{max_retries})")
        time.sleep(interval)
    
    raise Exception("查询超时")

# ========== 3. 下载视频 ==========
def download_video(file_id, task_id, output_path="output.mp4"):
    url = f"{BASE_URL}/v1/files/retrieve"
    params = {"file_id": file_id, "task_id": task_id}
    headers = {"Authorization": API_TOKEN}
    
    response = requests.get(url, params=params, headers=headers)
    result = response.json()
    
    download_url = result["file"]["download_url"]
    
    # 下载视频
    video_response = requests.get(download_url)
    with open(output_path, "wb") as f:
        f.write(video_response.content)
    
    print(f"视频已保存: {output_path}")

# ========== 执行 ==========
if __name__ == "__main__":
    # 提交任务
    task_id = submit_task()
    print(f"任务ID: {task_id}")
    
    # 查询任务（等待完成）
    file_id = query_task(task_id)
    print(f"文件ID: {file_id}")
    
    # 下载视频
    download_video(file_id, task_id)
```

---

## 八、安全规范

### 8.1 API调用安全

```python
# ✅ 正确做法
import os

# 从环境变量读取API密钥
API_TOKEN = os.environ.get("DMXAPI_TOKEN")

# 设置调用间隔（≥30秒）
import time
time.sleep(30)

# 设置最大重试次数
MAX_RETRIES = 5
```

### 8.2 错误处理

```python
def safe_api_call(func, max_retries=3, interval=30):
    """安全的API调用封装"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            print(f"重试 {i+1}/{max_retries}: {e}")
            time.sleep(interval)
```

### 8.3 关键安全规则

1. **密钥管理**
   - 不要在代码中硬编码API密钥
   - 使用环境变量存储
   - 定期轮换密钥

2. **调用频率**
   - 每次调用间隔 ≥ 30秒
   - 最大重试次数 ≤ 5次

3. **查询与提交分离**
   ```python
   # ❌ 错误：查询时创建新任务
   while not completed:
       response = requests.post(API_SUBMIT_URL, ...)  # 每次都在提交！
       time.sleep(10)
   
   # ✅ 正确：先提交，再查询
   task_id = requests.post(API_SUBMIT_URL, json={...}).json()["task_id"]
   while not completed:
       response = requests.get(API_QUERY_URL, params={"task_id": task_id})
       time.sleep(30)
   ```

---

## 九、故障排查

### 9.1 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 非0 | 失败 | 查看status_msg获取详细错误信息 |

### 9.2 常见问题

**Q: 任务一直处于Processing状态？**
A: 视频生成通常需要1-5分钟，高分辨率或长时长可能需要更长时间。请耐心等待或增加查询间隔。

**Q: 下载链接失效？**
A: 下载链接有有效期限制，请在获取后立即下载。如果失效，重新调用下载接口获取新链接。

**Q: 首尾帧尺寸不一致？**
A: 模型会参考首帧对尾帧进行裁剪。建议上传尺寸接近的图片以获得最佳效果。

**Q: 运镜指令无效？**
A: 确保使用标准指令格式（如`[推进]`），检查是否在支持的15种指令范围内。

---

*文档来源：DMXAPI官方文档*
*最后更新：2026-03-31*
