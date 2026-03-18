# HEARTBEAT.md - 任务执行清单

> 心跳时强制执行此清单，不依赖记忆

---

## 1. 读取状态文件

```bash
读取 /root/.openclaw/workspace/task-state.json
```

## 2. 检查进行中的任务

### Godot 模板下载
- **检查状态**: `task-state.json` 中的 `godot_templates.status`
- **如果为 `pending`**: 触发下载
- **如果为 `downloading`**: 检查进度，超时则重试
- **如果为 `failed`**: 记录错误，等待人工干预
- **如果为 `completed`**: 检查是否已安装，未安装则安装

### 导出任务
- **检查状态**: `task-state.json` 中的 `export_tasks`
- **H5 导出**: 模板就绪后自动执行
- **Windows 导出**: H5 完成后执行

## 3. 汇报机制

- **有进展**: 立即发送消息汇报
- **无进展**: 记录到状态文件，不打扰
- **错误**: 立即发送错误信息

## 4. 执行规则

- 不等待，立即执行
- 失败时更新状态文件并记录原因
- 成功时更新状态并推进下一步

---

## 当前任务状态

见 `task-state.json`
