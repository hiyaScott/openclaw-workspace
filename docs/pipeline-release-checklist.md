# AI短片Pipeline页面更新 - 发布检查流程

> **适用场景**: hiyamax-blog 的 pipeline.html 及相关数据文件更新
> **创建时间**: 2026-03-31
> **版本**: v1.0

---

## 📋 流程概览

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  1.代码修改  │ → │  2.本地验证  │ → │  3.提交部署  │ → │  4.线上验证  │ → │ 5.效果确认   │ → │  6.发布报告  │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
       ↓                 ↓                 ↓                 ↓                 ↓                 ↓
   修改HTML/JS      检查语法逻辑      git commit       HTTP 200检查     浏览器肉眼确认     更新文档记录
   或JSON数据       确认数据格式      git push          数据可访问        截图验证          流程闭环
```

**关键节点**：第5步"效果确认"为强制步骤，不可跳过。

---

## 第一步：代码修改

### 1.1 确定修改范围

| 修改类型 | 涉及文件 | 影响范围 |
|---------|---------|---------|
| **页面渲染逻辑** | `pipeline.html` | 所有项目展示 |
| **项目数据** | `pipeline/data/*.json` | 特定项目 |
| **图片资源** | `assets/` 目录 | 特定项目 |

### 1.2 修改前检查清单

- [ ] 是否已备份原文件？
- [ ] 修改是否影响其他项目？
- [ ] JSON 格式是否正确？（使用 JSON 校验工具）
- [ ] 图片路径是否正确？

### 1.3 常见修改场景

#### 场景 A：添加新的数据字段显示（如三视图 combined）

**修改位置**: `pipeline.html` 中的渲染函数

**示例**:
```javascript
// 修改前
const views = [
    { key: 'front', label: '正视图' },
    { key: 'side', label: '侧视图' },
    { key: 'back', label: '背视图' }
];

// 修改后
const views = [
    { key: 'front', label: '正视图' },
    { key: 'side', label: '侧视图' },
    { key: 'back', label: '背视图' },
    { key: 'combined', label: '完整三视图' }  // ← 新增
];
```

#### 场景 B：更新项目 JSON 数据

**文件**: `pipeline/data/the_147th_day.json`

**检查点**:
- 版本号是否正确递增？
- `currentVersion` 是否指向最新版本？
- `status` 是否为 "当前版本"？
- 图片路径是否以 `/hiyamax-blog/` 开头？

---

## 第二步：本地验证

### 2.1 语法检查

```bash
# JSON 格式验证
python3 -m json.tool pipeline/data/the_147th_day.json > /dev/null && echo "✅ JSON格式正确"

# 或使用 jq
jq . pipeline/data/the_147th_day.json > /dev/null && echo "✅ JSON格式正确"
```

### 2.2 数据完整性检查

```bash
# 检查图片文件是否存在
ls -la assets/the_147th_day/robo_no5_three_views_combined.png
ls -la assets/the_147th_day/thumbnails/robo_no5_three_views_combined_thumb.jpg
```

### 2.3 代码逻辑检查

- [ ] 新增字段在 JSON 中存在
- [ ] 页面渲染代码正确处理新字段
- [ ] 图片路径拼接逻辑正确
- [ ] 无语法错误（分号、括号匹配等）

---

## 第三步：提交部署

### 3.1 Git 提交流程

```bash
# 1. 添加修改的文件
git add pipeline.html
git add pipeline/data/the_147th_day.json
git add assets/the_147th_day/robo_no5_three_views_combined.png
git add assets/the_147th_day/thumbnails/robo_no5_three_views_combined_thumb.jpg

# 2. 提交（写清晰的提交信息）
git commit -m "fix: 在三视图渲染中添加完整三视图(combined)显示

- 在views数组中添加combined键，显示完整三视图合成图
- 确保threeViews.combined数据能正确渲染到页面"

# 3. 推送到 GitHub
git push origin main
```

### 3.2 提交信息规范

| 类型 | 格式 | 示例 |
|------|------|------|
| **功能添加** | `feat: 描述` | `feat: 添加三视图合成图显示` |
| **修复问题** | `fix: 描述` | `fix: 修正分镜3首帧JSON结构` |
| **数据更新** | `data: 描述` | `data: 更新角色设计V6版本数据` |
| **样式调整** | `style: 描述` | `style: 调整卡片间距` |

---

## 第四步：线上验证（关键！）

### 4.1 等待部署完成

- GitHub Pages 部署通常需要 **1-2 分钟**
- 可通过 GitHub Actions 查看部署状态

### 4.2 验证清单

#### 基础验证

- [ ] 页面能正常打开（HTTP 200）
- [ ] 无 JavaScript 报错（浏览器控制台）
- [ ] 页面标题正确

#### 功能验证

- [ ] **数据是否正确加载？**
  - 访问：`https://hiyascott.github.io/hiyamax-blog/pipeline/data/the_147th_day.json`
  - 确认：新字段存在且格式正确

- [ ] **图片是否正确显示？**
  - 访问：`https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_three_views_combined.png`
  - 确认：HTTP 200，图片内容正确

- [ ] **页面渲染是否正确？**
  - 访问：`https://hiyascott.github.io/hiyamax-blog/pipeline.html?project=the-147th-day`
  - 确认：新增内容可见，布局正常

---

## 第五步：页面显示效果确认（关键！）

> ⚠️ **此步骤为强制要求，不可跳过**
> 
> 必须肉眼确认页面上实际显示效果符合预期，才能算发布完成。

### 5.1 确认方式（二选一）

#### 方式 A：浏览器直接访问（推荐）

1. 打开浏览器访问页面
2. 定位到更新内容的模块/位置
3. 肉眼确认：
   - [ ] 图片正常显示，无裂图
   - [ ] 文字排版正确，无乱码/重叠
   - [ ] 布局正常，无错位/变形
   - [ ] 交互功能正常（如点击、展开）

#### 方式 B：截图确认

- 如无法直接访问，可要求用户截图确认
- 收到截图后检查显示效果

### 5.2 确认内容示例

**示例：分镜首帧图片更新**

| 检查点 | 标准 | 结果 |
|--------|------|------|
| 图片显示 | 清晰无 distortion | ✅ |
| 比例正确 | 16:9 宽屏比例 | ✅ |
| 位置正确 | 在镜头03卡片中显示 | ✅ |
| 缩略图正常 | 点击可放大查看原图 | ✅ |

### 5.3 确认后才能说"已完成"

> ❌ **未完成确认前，严禁说"已完成"或"部署成功"**
> 
> ✅ **确认完成后，必须附带确认方式**:
> - "已在浏览器确认页面显示正常"
> - "截图已验证，图片清晰显示"

---

### 4.3 验证命令示例

```bash
# 验证 JSON 数据
curl -s https://hiyascott.github.io/hiyamax-blog/pipeline/data/the_147th_day.json | jq '.steps[1].content.versions[5].data.threeViews.combined'

# 验证图片可访问
curl -I https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/robo_no5_three_views_combined.png
# 应返回 HTTP 200

# 验证缩略图
curl -I https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/thumbnails/robo_no5_three_views_combined_thumb.jpg
```

---

## 第六步：发布确认报告（更新 MEMORY.md）

### 6.1 报告模板

```markdown
## ✅ 发布确认报告 - [功能名称]

### 验证结果

| 检查项 | 状态 | 详情 |
|--------|------|------|
| **GitHub提交** | ✅/❌ | 提交SHA |
| **JSON数据** | ✅/❌ | 字段存在/格式正确 |
| **图片原图** | ✅/❌ | HTTP 200, 文件大小 |
| **缩略图** | ✅/❌ | HTTP 200 |
| **Pipeline页面** | ✅/❌ | 渲染正常 |
| **效果确认** | ✅/❌ | 浏览器肉眼确认/截图验证 |

### 部署位置

| 项目 | 位置 |
|------|------|
| **所属页面** | Step X: [模块名] |
| **数据路径** | `steps[X].content...` |
| **图片文件** | `/assets/the_147th_day/...` |

### 访问地址

- **页面**: https://hiyascott.github.io/hiyamax-blog/pipeline.html?project=the-147th-day
- **数据**: https://hiyascott.github.io/hiyamax-blog/pipeline/data/the_147th_day.json
- **图片**: https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/...

### 确认方式

- [ ] 浏览器直接访问确认
- [ ] 截图验证确认

**确认人**: [你的名字]
**确认时间**: [日期时间]

---

**确认发布成功，页面显示效果符合预期。**
```

### 6.2 必须确认后才算完成

> ⚠️ **重要**: 只有在完成以上所有验证（包括第5步的效果确认），并确认页面上**实际可见**后，才能告知用户"已完成"。
> 
> 严禁在以下情况下说"已完成":
> - 仅完成代码提交，未验证线上部署
> - 未检查页面实际渲染效果
> - 未确认图片可访问
> - **未进行第5步的"页面显示效果确认"**

---

## 📌 常见问题排查

### 问题 1：页面显示"加载中..."

**原因**: JSON 格式错误或数据加载失败

**排查**:
```bash
# 检查 JSON 格式
curl -s https://hiyascott.github.io/hiyamax-blog/pipeline/data/the_147th_day.json | python3 -m json.tool
```

### 问题 2：图片不显示

**原因**: 路径错误或文件未部署

**排查**:
```bash
# 检查图片是否存在
curl -I https://hiyascott.github.io/hiyamax-blog/assets/the_147th_day/[图片名]
```

### 问题 3：新添加的字段不显示

**原因**: 页面渲染代码未正确处理新字段

**排查**:
- 检查 `pipeline.html` 中对应渲染逻辑
- 确认字段名与 JSON 中的键名一致
- 检查浏览器控制台是否有 JS 报错

---

## 📝 流程执行记录

| 日期 | 执行人 | 内容 | 结果 | 效果确认 |
|------|--------|------|------|----------|
| 2026-03-31 | Jetton | 创建发布检查流程文档 | ✅ | - |
| 2026-03-31 | Jetton | 修复三视图 combined 显示问题 | ✅ | 浏览器确认 |
| 2026-03-31 | Jetton | 添加分镜3首帧V4 - 基于三视图生成 | ✅ | 待确认 |

---

## ✅ 本次更新总结

**新增强制步骤**：第5步"页面显示效果确认"

- 必须用浏览器访问页面，肉眼确认显示效果
- 或要求用户截图，验证后确认
- **未完成此步骤前，严禁说"已完成"**

**流程版本**: v1.1
