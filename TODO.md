# TODO List - Scott & Jetton

## 待处理

### 1. 下载页面优化 ⏰ 2026-03-16 22:00 提醒
**需求**：文件传输页面每次都要刷新，希望实现无需刷新页面的文件共享方案

**建议方案**：
- 阿里云 OSS / AWS S3 云存储
- 用户直接提供 Access Key，我直接上传
- 生成临时下载链接

**状态**：等待 Scott 提供云存储账号

### 2. Jetton Monitor Windows 版本构建
**需求**：创建独立仓库并触发 GitHub Actions 构建 Windows 版本

**执行步骤**：
1. 创建 `hiyaScott/jetton-monitor` 仓库
2. 推送完整源码
3. 配置 GitHub Actions
4. 触发 Windows 构建
5. 通知下载地址

**状态**：⏳ 等待 GitHub Token

---

## 已完成

- [x] Jetton Monitor Linux 版本开发
- [x] Windows/macOS 一键构建脚本
- [x] 详细版 Windows 构建脚本（带日志）
- [x] GitHub Actions 自动构建配置

---

*最后更新: 2026-03-16*
