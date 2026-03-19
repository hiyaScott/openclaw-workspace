# 监控数据仓库分离 - 执行报告

## 执行时间
2026-03-19 12:06 CST

## 新仓库信息

**仓库名称**: scott-portfolio-data  
**仓库路径**: /root/.openclaw/workspace/scott-portfolio-data  
**目标 URL**: https://github.com/hiyaScott/scott-portfolio-data

**数据文件 URL**:
- 当前状态: https://raw.githubusercontent.com/hiyaScott/scott-portfolio-data/main/status-monitor/cognitive-data.json
- 历史数据: https://raw.githubusercontent.com/hiyaScott/scott-portfolio-data/main/status-monitor/cognitive-history.jsonl

## 修改的文件列表

### 1. 推送脚本
**文件**: `portfolio-blog/status-monitor/cognitive_push_v4.sh`
- 修改 `REPO_DIR` 指向新数据仓库
- 添加 `SOURCE_DIR` 变量指向数据源
- 添加数据复制逻辑（从 portfolio-blog 复制到 scott-portfolio-data）
- 修改 commit message 格式为 `data: update cognitive status`

### 2. 主页认知负载卡片
**文件**: `portfolio-blog/index.html`
- 修改数据 URL 从 `hiyascott.github.io/scott-portfolio/...` 改为 `raw.githubusercontent.com/hiyaScott/scott-portfolio-data/...`

### 3. 认知负载监控页面
**文件**: `portfolio-blog/status-monitor/cognitive-status.html`
- 修改 `DATA_URL` 指向新数据仓库
- 修改历史数据 `historyUrl` 指向新数据仓库

### 4. 新数据仓库
**文件**: `scott-portfolio-data/README.md` (新建)
- 仓库说明文档

**文件**: `scott-portfolio-data/status-monitor/cognitive-data.json` (新建)
- 当前认知负载状态数据

**文件**: `scott-portfolio-data/status-monitor/cognitive-history.jsonl` (新建)
- 认知负载历史记录数据

## 测试结果

### ✅ 通过测试
1. **脚本语法检查**: 推送脚本语法正确
2. **数据复制测试**: 数据文件能正确复制到目标仓库
3. **URL 修改验证**: 所有页面 URL 已更新为新地址
4. **本地数据仓库**: 已初始化并提交初始数据

### ⏳ 待完成
1. **GitHub 远程仓库创建**: 需要在 GitHub 上创建 hiyaScott/scott-portfolio-data 仓库
2. **首次推送**: 将本地数据仓库推送到 GitHub
3. **页面访问测试**: 验证 raw.githubusercontent.com 数据加载正常

## 手动操作步骤

### 1. 创建 GitHub 仓库（如未创建）
访问 https://github.com/new 创建名为 `scott-portfolio-data` 的公开仓库。

### 2. 推送本地仓库到 GitHub
```bash
cd /root/.openclaw/workspace/scott-portfolio-data
git remote add origin git@github.com:hiyaScott/scott-portfolio-data.git
git push -u origin main
```

### 3. 验证数据访问
访问以下 URL 确认数据可访问：
- https://raw.githubusercontent.com/hiyaScott/scott-portfolio-data/main/status-monitor/cognitive-data.json
- https://raw.githubusercontent.com/hiyaScott/scott-portfolio-data/main/status-monitor/cognitive-history.jsonl

### 4. 测试推送脚本
```bash
bash /root/.openclaw/workspace/portfolio-blog/status-monitor/cognitive_push_v4.sh
```

### 5. 验证页面加载
- 打开主页: https://hiyascott.github.io/scott-portfolio/
- 打开监控页: https://hiyascott.github.io/scott-portfolio/status-monitor/cognitive-status.html
- 检查认知负载卡片和历史图表是否正常显示

## 回滚方案

如需回滚到使用原仓库数据：

### 方案 A: 快速回滚（恢复 URL）
```bash
# 恢复 index.html
cd /root/.openclaw/workspace/portfolio-blog
git checkout -- index.html

# 恢复 cognitive-status.html
git checkout -- status-monitor/cognitive-status.html

# 恢复推送脚本
git checkout -- status-monitor/cognitive_push_v4.sh
```

### 方案 B: 保留新仓库但页面使用原地址
```bash
# 手动修改 URL 回原来的地址
# index.html: 改回 https://hiyascott.github.io/scott-portfolio/status-monitor/cognitive-data.json
# cognitive-status.html: 改回 https://hiyascott.github.io/scott-portfolio/...
```

### 方案 C: 完整回滚（删除新仓库）
1. 执行方案 A 恢复文件
2. 在 GitHub 上删除 scott-portfolio-data 仓库（如已创建）
3. 删除本地数据仓库: `rm -rf /root/.openclaw/workspace/scott-portfolio-data`

## 注意事项

1. **新仓库推送不会触发 GitHub Pages 构建** - 数据仓库无需 Pages 配置
2. **熔断机制保持不变** - 推送脚本中的熔断、退避机制未修改
3. **跨域访问** - raw.githubusercontent.com 支持 CORS，可直接访问
4. **数据一致性** - 每次推送前会复制最新数据到新仓库，确保数据一致
5. **commit 信息** - 使用 `data: update cognitive status` 格式

## 下一步建议

1. 在 GitHub 上创建 scott-portfolio-data 仓库
2. 推送本地数据到远程仓库
3. 测试页面数据加载
4. 更新 crontab 确保推送脚本定期执行
5. 监控推送日志 `/var/log/cognitive_health.log`
