---
name: volcengine-jimeng
description: 火山引擎即梦AI图像/视频生成服务。用于调用火山引擎视觉大模型API生成图片和视频。支持文生图、图生图、文生视频等功能。当用户需要生成AI图片/视频、使用即梦AI、或调用火山引擎视觉API时使用此Skill。
---

# 火山引擎即梦AI生成服务

## 概述

本Skill封装了火山引擎即梦AI的API调用，支持通过视觉大模型API生成图片和视频内容。

**核心功能：**
- 🎨 **文生图** - 通过文本描述生成图片
- 🖼️ **图生图** - 基于参考图生成新图片
- 🎬 **文生视频** - 通过文本描述生成视频
- 🎞️ **图生视频** - 将静态图片转为动态视频

**技术基础：**
- 基于火山引擎视觉大模型API (visual.volcengineapi.com)
- 使用HMAC-SHA256签名认证
- 支持异步任务处理和状态查询

**重要提示：**
经过实测，`jimeng_t2i_v40`（即梦4.0）可能需要在控制台单独开通。当前可用的模型是 `jimeng_high_aes_general_v21_L`（即梦高美学2.1L）。

## 前置条件

### 1. 获取API凭证

推荐使用**主账号AK/SK**（无需额外IAM策略配置）：

1. 登录 https://console.volcengine.com/iam/keymanage/
2. 确保是**主账号**（不是IAM子用户）
3. 点击"创建密钥"获取AK/SK

**如果使用IAM子用户：**
1. 创建子用户并绑定 `CVFullAccess` 策略
2. **关键**：绑定策略后必须**重新生成AK/SK**
3. 旧AK/SK不会自动继承新权限

### 2. 确认服务开通

确保已在火山引擎控制台开通即梦AI服务：
- 访问 https://www.volcengine.com/product/jimeng
- 点击"立即开通"或"免费试用"

**注意：** 不同模型可能需要单独开通，如 `jimeng_t2i_v40` 可能需要额外权限。

### 3. 配置环境变量

```bash
export JIMENG_AK="你的AccessKey"
export JIMENG_SK="你的SecretKey"
```

### 3. 配置环境变量

```bash
export JIMENG_AK="你的AccessKey"
export JIMENG_SK="你的SecretKey"
```

## 使用方法

### 快速生成图片

```python
from scripts.jimeng_client import JimengClient

client = JimengClient()
result = client.generate_image(
    prompt="一只可爱的柴犬在樱花树下，阳光明媚",
    width=1024,
    height=1024
)

if result['success']:
    print(f"图片URL: {result['image_url']}")
else:
    print(f"生成失败: {result['error']}")
```

### 生成视频

```python
result = client.generate_video(
    prompt="一只熊猫在竹林中玩耍，阳光明媚",
    width=512,
    height=512
)

if result['success']:
    print(f"任务ID: {result['task_id']}")
    # 轮询查询结果
    video_url = client.wait_for_video(result['task_id'])
```

### 直接使用API（完整示例）

```python
import requests, json, hashlib, hmac, datetime, time

def sign(ak, sk, action, version, body):
    now = datetime.datetime.utcnow()
    x_date = now.strftime('%Y%m%dT%H%M%SZ')
    short_x_date = x_date[:8]
    host = "visual.volcengineapi.com"
    query = f"Action={action}&Version={version}"
    body_bytes = json.dumps(body, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    sha256 = hashlib.sha256(body_bytes).hexdigest()
    signed_headers = "content-type;host;x-content-sha256;x-date"
    canonical = f"POST\n/\n{query}\ncontent-type:application/json\nhost:{host}\nx-content-sha256:{sha256}\nx-date:{x_date}\n\n{signed_headers}\n{sha256}"
    k_date = hmac.new(sk.encode(), short_x_date.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, b"cn-north-1", hashlib.sha256).digest()
    k_service = hmac.new(k_region, b"cv", hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"request", hashlib.sha256).digest()
    scope = f"{short_x_date}/cn-north-1/cv/request"
    string_to_sign = f"HMAC-SHA256\n{x_date}\n{scope}\n{hashlib.sha256(canonical.encode()).hexdigest()}"
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    auth = f"HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={signed_headers}, Signature={signature}"
    return f"https://{host}/?{query}", {"Host": host, "X-Date": x_date, "X-Content-Sha256": sha256, "Content-Type": "application/json", "Authorization": auth}, body_bytes

# 提交任务
ak = "你的AccessKey"
sk = "你的SecretKey"
body = {
    "req_key": "jimeng_high_aes_general_v21_L",  # ✅ 实测可用的模型
    "prompt": "一只可爱的柴犬在樱花树下",
    "width": 1024,
    "height": 1024,
    "return_url": True
}
url, headers, body_bytes = sign(ak, sk, "CVSync2AsyncSubmitTask", "2022-08-31", body)
resp = requests.post(url, headers=headers, data=body_bytes, timeout=30)
result = resp.json()
print(f"Task ID: {result['data']['task_id']}")

# 查询结果（3秒后）
time.sleep(3)
query_body = {
    "req_key": "jimeng_high_aes_general_v21_L",
    "task_id": result['data']['task_id'],
    "req_json": json.dumps({"return_url": True})
}
url, headers, body_bytes = sign(ak, sk, "CVSync2AsyncGetResult", "2022-08-31", query_body)
resp = requests.post(url, headers=headers, data=body_bytes, timeout=30)
result = resp.json()
print(f"图片URL: {result['data']['image_urls'][0]}")
```

### 查询任务状态

```python
status = client.get_task_status(task_id)
print(f"状态: {status['status']}")  # PENDING/RUNNING/SUCCEEDED/FAILED
```

## 支持的模型与接口

### 实测可用的模型

通过实际测试验证可用的模型：

| req_key | 模型 | 状态 | 备注 |
|---------|------|------|------|
| `jimeng_high_aes_general_v21_L` | 即梦高美学2.1L | ✅ **可用** | 推荐使用 |
| `jimeng_t2i_v40` | 即梦4.0 | ❌ Access Denied | 可能需单独开通 |
| `high_aes_general_v30l_zt2i` | 通用3.0高美学 | ❌ 未验证 | - |

### API接口对照表

| 功能 | Action | Version | req_key |
|------|--------|---------|---------|
| 提交图片任务 | CVSync2AsyncSubmitTask | 2022-08-31 | jimeng_high_aes_general_v21_L |
| 查询图片结果 | CVSync2AsyncGetResult | 2022-08-31 | jimeng_high_aes_general_v21_L |

**重要提示：** 虽然文档提到 `jimeng_t2i_v40` 是即梦4.0模型，但实际测试返回 `Access Denied`，可能需要在控制台单独开通该模型权限。

### 图片生成模型

| req_key | 模型 | 说明 |
|---------|------|------|
| `jimeng_high_aes_general_v21_L` | 即梦高美学2.1L | ✅ 实测可用，高质量通用图片 |
| `jimeng_t2i_v40` | 即梦4.0 | ❌ 实测不可用（Access Denied） |
| `high_aes_general_v30l_zt2i` | 通用3.0高美学 | 中文优化版本 |
| `lumi_i2i_v20` | 图生图2.0 | 基于参考图生成 |

### 视频生成模型

| req_key | 模型 | 说明 |
|---------|------|------|
| `jimeng_vgfm_t2v_l20` | 文生视频2.0 | 文本生成视频 |
| `jimeng_vgfm_i2v_l20` | 图生视频2.0 | 图片生成视频 |
| `jimeng_ti2v_v30_pro` | 文生视频3.0 Pro | 高清版本(1080P) |

**注意：** 实际可用的模型取决于你的账号权限。如果遇到 `Access Denied`、`NoFeatAuth` 或 `FeatNotFound` 错误，请参考"常见错误"章节解决。

## 常见错误

### Access Denied (50400)
- **原因**: AK/SK没有即梦AI的调用权限
- **解决**: 
  1. 进入访问控制 → 权限策略
  2. 创建或附加策略 `JimengFullAccess` 或 `CVFullAccess`
  3. 确保策略关联到使用AK/SK的用户
  4. 等待几分钟策略生效

### SignatureDoesNotMatch (401)
- **原因**: 签名验证失败
- **解决**: 检查AK/SK是否正确，SK使用原始Base64字符串（不需要解码）

### NoFeatAuth (200但code=30403)
- **原因**: 签名正确，但账号没有该功能的权限
- **解决**: 在火山引擎控制台开通相应服务，或升级到付费版

### FeatNotFound (200但code=30404)
- **原因**: 请求的模型(req_key)不存在或已下架
- **解决**: 更换其他模型尝试

### InvalidActionOrVersion (404)
- **原因**: Action或Version参数错误
- **解决**: 使用正确的Action和Version组合

## 技术实现

### 签名算法

火山引擎使用标准的AWS Signature Version 4签名流程：

1. **创建Canonical Request**
   ```
   HTTP_METHOD + "\n" +
   URI_PATH + "\n" +
   QUERY_STRING + "\n" +
   CANONICAL_HEADERS + "\n" +
   SIGNED_HEADERS + "\n" +
   HEX(HASH(payload))
   ```

2. **创建String to Sign**
   ```
   "HMAC-SHA256" + "\n" +
   X_DATE + "\n" +
   CREDENTIAL_SCOPE + "\n" +
   HEX(HASH(Canonical Request))
   ```

3. **计算签名密钥**
   ```
   kDate = HMAC(SecretKey, Date)
   kRegion = HMAC(kDate, Region)
   kService = HMAC(kRegion, Service)
   kSigning = HMAC(kService, "request")
   ```

4. **生成Authorization Header**
   ```
   Authorization: HMAC-SHA256 
     Credential=AK/Scope, 
     SignedHeaders=content-type;host;x-content-sha256;x-date, 
     Signature=SIGNATURE
   ```

### 关键要点

- **时间格式**: `YYYYMMDD'T'HHMMSS'Z'` (UTC时间)
- **Secret Key**: 直接使用Base64编码的原始字符串，不要解码
- **Signed Headers**: 固定顺序 `content-type;host;x-content-sha256;x-date`
- **Region**: `cn-north-1`
- **Service**: `cv`

## 豆包图片生成API (Seedream)

豆包提供另一套图片生成API，使用OpenAI兼容格式，无需HMAC签名。

### 模型列表

| 模型 | 说明 |
|------|------|
| `doubao-seedream-5.0` | 最强图片生成模型，搭载联网检索功能 |
| `doubao-seedream-4-0-250828` | 4.0版本 |
| `doubao-seedream-3-0-t2i-250415` | 3.0版本 |

### API调用示例 (Python)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="你的ARK_API_KEY"  # 从火山引擎控制台获取
)

response = client.images.generate(
    model="doubao-seedream-5.0",
    prompt="一只可爱的柴犬在樱花树下，阳光明媚"
)

print(response.data[0].url)
```

### 图片传入方式 (图生图)

- **公网URL**: 直接传入图片可访问链接
- **Base64**: `data:image/png;base64,{base64编码}`

### 与即梦API的区别

| 特性 | 即梦API | 豆包Seedream API |
|------|---------|-----------------|
| 端点 | `visual.volcengineapi.com` | `ark.cn-beijing.volces.com/api/v3` |
| 认证 | HMAC-SHA256签名 | API Key (OpenAI兼容) |
| 协议 | 火山引擎自定义 | OpenAI兼容 |
| 适用场景 | 即梦特色功能、视频生成 | 标准图片生成、快速接入 |

## 参考资源

- 火山引擎签名文档：https://www.volcengine.com/docs/86081/2179673
- 即梦AI产品页：https://www.volcengine.com/product/jimeng
- 视觉大模型API文档：https://www.volcengine.com/docs/6791
- 豆包API文档：https://www.volcengine.com/docs/82379

## 调试经验与常见问题

### 实测调试记录

**成功配置（2026-03-28验证）：**
- AK/SK：主账号AccessKey（无需IAM策略配置）
- Endpoint：`https://visual.volcengineapi.com`
- Action：`CVSync2AsyncSubmitTask`
- Version：`2022-08-31`
- req_key：`jimeng_high_aes_general_v21_L` ✅

**失败案例：**
- `jimeng_t2i_v40` 即使主账号AK/SK也返回Access Denied
- 原因：该模型可能需要单独在控制台开通

### IAM子用户权限配置要点

如果使用IAM子用户而非主账号：

1. **创建策略**：创建自定义策略或绑定`CVFullAccess`
2. **绑定用户**：将策略关联到IAM子用户
3. **重新生成AK/SK**：**关键步骤** - 策略绑定后必须重新生成AK/SK，旧的AK/SK不会自动继承新权限
4. **等待生效**：通常5-10分钟

### 常见错误速查

| 错误码 | 含义 | 解决方案 |
|--------|------|---------|
| 50400 | Access Denied | 检查AK/SK权限、确认req_key正确、确认服务已开通 |
| 30403 | NoFeatAuth | 该模型未开通权限，尝试其他req_key |
| 30404 | FeatNotFound | req_key不存在或已下架 |
| 401 | SignatureDoesNotMatch | SK使用原始base64字符串，不要解码 |

### 签名关键点

1. **Secret Key**：直接使用base64编码的原始字符串，**不要解码**
2. **Signed Headers**：固定顺序 `content-type;host;x-content-sha256;x-date`
3. **时间格式**：UTC时间 `YYYYMMDD'T'HHMMSS'Z'`
4. **Region/Service**：固定 `cn-north-1` / `cv`