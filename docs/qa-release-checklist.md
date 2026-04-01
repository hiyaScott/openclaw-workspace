# 发布确认 QA 流程

> 部署后必须完成 QA 检查，确认成功后才通知用户

## 标准流程

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  1.部署代码  │ → │  2.等待同步  │ → │  3.QA检查   │ → │  4.通知用户  │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
      ↓                  ↓                ↓                ↓
   git push          检查last-      自动验证所有      成功/失败
   成功确认          modified时间      关键指标         详细报告
```

## QA 检查清单

### Web 页面部署
- [ ] HTML 文件 HTTP 200
- [ ] 关键资源可访问（CSS/JS/图片）
- [ ] 页面无 404 错误

### 数据文件更新
- [ ] JSON 格式有效
- [ ] 新增字段存在
- [ ] 数据完整性检查

### 图片/视频资源
- [ ] 所有引用图片 HTTP 200
- [ ] 缩略图/海报可访问
- [ ] 文件大小合理

### CDN 缓存
- [ ] 检查 Last-Modified 时间
- [ ] 确认版本已更新
- [ ] 必要时添加 cache-buster

## 输出模板

### 成功通知
```
✅ [任务名称] 部署成功

QA 检查通过：
| 检查项 | 状态 |
|--------|------|
| xxx | ✅ |

访问地址：[URL]
```

### 失败通知
```
❌ [任务名称] 部署异常

问题：
- xxx 检查失败（HTTP 404）
- xxx 数据缺失

需要人工介入
```

## 自动化工具

### 使用 QA-Release-Check Skill

**Skill 位置**: `/root/.openclaw/workspace/skills/qa-release-check/`

**适用场景**:
- AI短片 Pipeline 页面部署
- GitHub Pages 静态站点发布
- 任何需要验证的 web 部署

**使用方法**:

```bash
# 标准 Pipeline QA 检查
python3 /root/.openclaw/workspace/skills/qa-release-check/scripts/qa_check_pipeline.py

# 验证特定项目
python3 /root/.openclaw/workspace/skills/qa-release-check/scripts/qa_check_pipeline.py \
  --url https://hiyascott.github.io/hiyamax-blog \
  --project the_147th_day
```

**检查内容**:
- ✅ 页面 HTTP 200 状态
- ✅ JSON 数据格式和完整性
- ✅ 所有视频海报配置
- ✅ 海报图片可访问性
- ✅ 蓝图功能代码存在

**结果解读**:
- Exit 0 = 全部通过，可以通知用户
- Exit 1 = 有失败项，需要修复

### 手动检查脚本

```bash
# qa_check.sh - 基础检查模板
#!/bin/bash
URL=$1

echo "=== QA Check: $URL ==="

# 1. 检查页面状态
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ FAIL: HTTP $HTTP_CODE"
    exit 1
fi
echo "✅ Page: HTTP 200"

# 2. 检查关键资源
# ...

echo "=== QA Check Passed ==="
```

## 详细检查清单

详见: `/root/.openclaw/workspace/skills/qa-release-check/references/checklist.md`

包含:
- 完整的 Web/Assets/Data 检查清单
- 常见问题与解决方案
- 详细报告模板

1. **绝不提前通知** - 完成 QA 前不说"已完成"
2. **失败即停止** - 发现问题立即报告，不隐瞒
3. **提供证据** - 每个检查结果都要有数据支撑
4. **给出下一步** - 成功给链接，失败给解决方案
