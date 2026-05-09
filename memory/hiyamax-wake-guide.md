# hiyamax.com 快速唤醒指南

> 给 Scott 的快速参考：如何让我（Jetton）在 reset 后立刻进入正确状态

---

## 一句话唤醒模板

复制粘贴下面这段，我会立刻知道该做什么：

```
@Jetton 处理 hiyamax.com 的网站问题
- 仓库：hiyamax-home（不是 scott-portfolio/research/max-home）
- 域名：www.hiyamax.com 指向 hiyamax-home 仓库
- 陀螺仪代码位置：assets/js/main.js
- 测试页：https://hiyascott.github.io/scott-portfolio/research/gyro-test.html
```

---

## 关键事实（不要让我猜）

| 项目 | 正确值 | 我曾犯的错误 |
|------|--------|-------------|
| 目标仓库 | `hiyaScott/hiyamax-home` | 错改成 `scott-portfolio/research/max-home` |
| 域名指向 | `www.hiyamax.com` → `hiyamax-home` GitHub Pages | 误以为指向 scott-portfolio |
| JS 文件 | `assets/js/main.js` | 在错误仓库里找文件 |
| 版本号位置 | `_includes/footer.html` | 搜索不到 |
| 陀螺仪测试页 | `https://hiyascott.github.io/scott-portfolio/research/gyro-test.html` | — |

---

## 我的教训（请提醒我）

如果我开始做传感器/陀螺仪相关的修改，请提醒我检查 `memory/2026-04-30-gyro-lessons.md`：

1. **测试页原则**：gyro-test.html 能工作 → 先原样移植到正式页
2. **不要改动确认能工作的代码**：iOS 权限请求逻辑在 v1.5.1 是能工作的
3. **等 5 分钟 CDN**：GitHub Pages 缓存 2-5 分钟，不要急于下一版修改
4. **隔离新增**：如果要加 fallback，用独立函数，不要改原有逻辑

---

## 常用命令（我已记住）

```bash
# 检查仓库远程地址
cd /root/.openclaw/workspace/hiyamax-home-jekyll && git remote -v

# 查看当前版本
cd /root/.openclaw/workspace/hiyamax-home-jekyll && cat _includes/footer.html

# 快速验证线上 JS
curl -sL https://www.hiyamax.com/assets/js/main.js | grep -A 5 "deviceorientation"
```

---

## 文件位置备忘

```
workspace/
├── hiyamax-home-jekyll/          ← hiyamax.com 源码（GitHub Pages）
│   ├── assets/js/main.js         ← 陀螺仪代码
│   ├── _includes/footer.html     ← 版本号
│   ├── _layouts/home.html        ← 首页布局
│   └── _config.yml               ← baseurl: "", url: "https://www.hiyamax.com"
│
└── portfolio-blog/
    └── research/
        └── max-home/             ← 测试页面（不是正式站）
```

---

## 快速检查指令

你发：**"检查一下hiyamax网站的状态"**

我回：
```
版本: vX.X.X | 仓库: hiyaScott/hiyamax-home ✅
JS文件: assets/js/main.js | 测试页: gyro-test.html
当前状态: [今日摘要]
```

---

## 唤醒信号

以下关键词会让我立刻加载本文件：
- "hiyamax"
- "陀螺仪"
- "头像"
- "gyro"
- "deviceorientation"
- "鸿蒙"
- "传感器"
- "检查网站状态"

---

*Created: 2026-04-30*
*Updated: 2026-05-01*
