# Pipeline页面操作手册

> hiyamax-blog Pipeline页面的完整操作指南

---

## 页面架构

```
pipeline.html
├── 头部导航（项目切换）
├── 项目封面（cover + 缩略图）
├── Step 1: 创意概念（可折叠）
├── Step 2: 角色设计（可折叠）
├── Step 3: 场景设计（可折叠）
├── Step 4: 分镜首帧（可折叠）
├── Step 5: 视频生成（可折叠）
└── Step 6: 后期剪辑（可折叠）

每个Step包含:
├── 版本切换器（V1/V2/...）
├── 内容区域（图片/视频/文本）
└── 讨论记录（可折叠）
```

---

## 一、数据操作流程

### 1.1 添加新项目

**步骤**：
1. 在 `pipeline/data/` 创建 `{project_name}.json`
2. 在 `assets/{project_name}/` 创建目录结构
3. 复制标准模板并修改
4. 在 `pipeline.html` 头部添加项目入口

**标准目录结构**：
```
assets/{project_name}/
├── thumbnails/          # 缩略图（必须）
├── scenes/              # 场景原图
├── shots/               # 首帧原图
└── videos/              # 视频片段
```

### 1.2 修改现有项目

**安全修改流程**：
```bash
# 1. 备份原数据
cp pipeline/data/{project}.json pipeline/data/{project}.json.bak

# 2. 修改JSON
# 使用Python脚本验证JSON格式
python3 -c "import json; json.load(open('pipeline/data/{project}.json'))"

# 3. 检查缩略图关联
# 确保所有image都有对应的thumbnail

# 4. 本地测试（如果有HTTP服务器）
# python3 -m http.server 8888
```

### 1.3 版本管理

**版本切换逻辑**：
- JSON中每个Step包含 `versions` 数组
- 每个version有 `status` 字段："当前版本" 或 "已归档"
- 页面上版本切换器只显示当前Step的版本

**添加新版本**：
```json
{
  "version": "v3",
  "status": "当前版本",  // 标记新版本为当前
  "updated": "2026-03-31",
  "data": { ... }
}
```
**注意**：同一时间只有一个版本可以是"当前版本"

---

## 二、缩略图系统

### 2.1 缩略图生成

**生成脚本**（保存为 `scripts/generate_thumbnails.py`）：
```python
from PIL import Image
import os

def generate_thumbnail(input_path, output_path, size=(400, 250), quality=85):
    """生成标准缩略图"""
    with Image.open(input_path) as img:
        # 转换为RGB（处理PNG透明背景）
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # 等比例缩放
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # 保存
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
    original_size = os.path.getsize(input_path) / 1024  # KB
    thumb_size = os.path.getsize(output_path) / 1024    # KB
    print(f"{os.path.basename(input_path)}: {original_size:.0f}KB → {thumb_size:.1f}KB")

# 批量生成
thumb_dir = 'assets/{project}/thumbnails/'
for filename in os.listdir('assets/{project}/'):
    if filename.endswith(('.jpg', '.png')) and '_thumb' not in filename:
        input_path = f'assets/{project}/{filename}'
        output_path = f'{thumb_dir}{filename.rsplit(".", 1)[0]}_thumb.jpg'
        generate_thumbnail(input_path, output_path)
```

### 2.2 缩略图规格

| 用途 | 尺寸 | 格式 | 质量 | 目标大小 |
|------|------|------|------|----------|
| 场景/首帧 | 400x250px | JPEG | 85% | ~15KB |
| 三视图 | 300x400px | JPEG | 85% | ~12KB |
| 封面 | 600x340px | JPEG | 85% | ~27KB |

### 2.3 缩略图路径规则

**重要**：路径必须包含 `thumbnails/` 子目录

**正确路径**：
```
https://hiyascott.github.io/hiyamax-blog/assets/{project}/thumbnails/xxx_thumb.jpg
```

**错误路径**：
```
https://hiyascott.github.io/hiyamax-blog/assets/{project}/xxx_thumb.jpg  ❌
./assets/{project}/thumbnails/xxx_thumb.jpg  ❌ 移动端解析失败
```

---

## 三、部署流程

### 3.1 标准部署流程

```bash
# 1. 检查变更
git status

# 2. 添加所有变更
git add -A

# 3. 提交（描述清晰）
git commit -m "feat: 添加XX项目场景V2"

# 4. 推送
git push origin main

# 5. 验证部署（等待10秒）
curl -sI https://hiyascott.github.io/hiyamax-blog/pipeline.html | grep last-modified
```

### 3.2 缓存刷新验证

**GitHub Pages缓存策略**：
- 静态文件：`max-age=600`（10分钟）
- 强制刷新：`?t={timestamp}` 或 `Ctrl+F5`

**验证命令**：
```bash
# 检查页面更新时间
curl -sI https://hiyascott.github.io/hiyamax-blog/pipeline.html | grep -E "last-modified|age"

# age=0 表示已获取最新内容
# last-modified 显示实际文件修改时间
```

### 3.3 大文件推送（>100MB）

如果遇到 `GnuTLS recv error`：
```bash
# 方案1：分批推送
git push origin main --thin

# 方案2：使用SSH（配置后）
git remote set-url origin git@github.com:username/repo.git

# 方案3：增大缓冲区
git config http.postBuffer 524288000
```

---

## 四、页面配置详解

### 4.1 渲染逻辑

**核心函数**：`renderStepContent(stepNum, data)`

**渲染流程**：
1. 根据Step类型选择渲染模板
2. 提取当前版本的数据
3. 生成HTML字符串
4. 插入到DOM中

**关键代码片段**（参考图渲染）：
```javascript
// Reference images
if (data.referenceImages) {
    const thumbBasePath = 'https://hiyascott.github.io/hiyamax-blog/assets/{project}/thumbnails/';
    data.referenceImages.forEach(img => {
        const thumbUrl = img.thumbnail ? thumbBasePath + img.thumbnail : img.src;
        html += `
            <img src="${thumbUrl}" 
                 onerror="this.onerror=function(){this.src='${img.src}';};" 
                 decoding="async">
        `;
    });
}
```

### 4.2 版本切换机制

**切换逻辑**：
```javascript
function switchVersion(stepNum, version) {
    // 1. 更新按钮状态
    // 2. 重新渲染该Step的内容
    // 3. 保持其他Step不变
}
```

**数据流**：
```
用户点击版本按钮 → 更新currentVersion[stepNum] → 重新渲染该Step → 插入DOM
```

### 4.3 折叠/展开机制

**实现方式**：
- CSS: `max-height` 过渡动画
- JS: 切换 `collapsed` 类
- 状态: 默认折叠Step内容，只显示标题

---

## 五、故障排查

### 5.1 图片显示问号

**排查步骤**：
1. **检查文件是否存在**
   ```bash
   ls assets/{project}/thumbnails/xxx_thumb.jpg
   ```

2. **检查JSON中的thumbnail字段**
   ```python
   # 确保不是"N/A"或空字符串
   ```

3. **检查路径是否正确**
   ```bash
   # 路径必须包含thumbnails/
   curl -I https://hiyascott.github.io/.../thumbnails/xxx_thumb.jpg
   ```

4. **检查GitHub Pages是否已更新**
   ```bash
   curl -sI ... | grep last-modified
   ```

### 5.2 缓存不更新

**解决方案**：
1. **Service Worker升级**
   ```javascript
   // sw.js中更新版本号
   const CACHE_NAME = 'hiyamax-pipeline-v{version}';
   ```

2. **用户强制刷新**
   - 完全关闭浏览器App
   - 或使用时间戳参数：`?t=123456`

3. **等待CDN过期**
   - GitHub Pages缓存10分钟

### 5.3 JSON格式错误

**验证命令**：
```bash
python3 -m json.tool pipeline/data/{project}.json > /dev/null && echo "Valid JSON"
```

**常见错误**：
- 逗号放在最后一个元素后
- 引号不匹配
- 中文字符编码问题

### 5.4 移动端显示异常

**排查清单**：
- [ ] 使用绝对路径而非相对路径
- [ ] 移除 `loading="lazy"`（旧浏览器兼容性）
- [ ] 图片有 `decoding="async"`
- [ ] 视频有 `playsinline` 属性

---

## 六、性能优化配置

### 6.1 Service Worker缓存策略

```javascript
// sw.js
const IMAGE_CACHE = 'hiyamax-images-v{version}';

// 图片：Cache First
if (request.url.includes('thumbnails/')) {
    return caches.match(request).then(response => {
        return response || fetch(request);
    });
}

// JSON：Stale While Revalidate
if (request.url.includes('.json')) {
    return fetch(request).then(response => {
        caches.open(JSON_CACHE).then(cache => cache.put(request, response.clone()));
        return response;
    }).catch(() => caches.match(request));
}
```

### 6.2 图片加载优化

**推荐配置**：
```html
<img src="{thumbUrl}" 
     onerror="this.onerror=function(){this.src='{originalUrl}';};" 
     decoding="async"
     alt="{description}">
```

**优化效果**：
- 首屏加载：从~40MB降至~117KB
- 缩略图压缩：266倍（4MB→15KB）

---

## 七、检查清单

### 7.1 发布前检查

- [ ] JSON格式验证通过
- [ ] 所有图片都有缩略图
- [ ] 缩略图路径包含 `thumbnails/`
- [ ] 运行QA验证脚本通过
- [ ] Git提交并推送
- [ ] GitHub Pages已更新（last-modified检查）
- [ ] 移动端测试通过

### 7.2 QA验证脚本

```bash
# 运行验证
python3 scripts/qa_verify.py . {project_name}

# 预期输出：
# ✅ 所有验证通过！
```

---

*最后更新：2026-03-31*
