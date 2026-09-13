# 数理课件统一视觉规范 v1.0

> 适用：数学（grade6-9）+ 物理（grade8-9）全部 tutorial.html
> 核心原则：**基础布局统一，色彩主题差异化**
> 单元数量：**4-7个，按需决定，不强制7个**

---

## 一、必须统一的基础样式

### 1. 页面结构

```html
<!-- 标准骨架 -->
<div id="app">
  <div class="title-bar">
    <h1>第X章 标题</h1>
    <p class="subtitle">SUBTITLE · 年级 · 课时</p>
    <!-- 挑战按钮必须放在 title-bar 内，居中 -->
    <div style="text-align:center;margin-top:16px;">
      <a class="btn btn-warn" href="index.html">🎮 去挑战模式</a>
    </div>
  </div>

  <div class="progress-bar" id="progress-bar">
    <!-- 进度条段数 = 实际单元数（4-7），不强制7 -->
  </div>

  <!-- 单元卡片，数量按需（4-7个），不强制7个 -->
  <div class="card" id="ch1">...</div>
  <div class="card hidden" id="ch2">...</div>
  ...
</div>
```

### 2. Title Bar 规范

| 属性 | 值 | 说明 |
|---|---|---|
| `text-align` | `center` | 必须居中 |
| `border-bottom` | `1px solid var(--theme-color)` | 主题色下划线 |
| `padding-bottom` | `16px` | |
| `margin-bottom` | `24px` | |

**H1 标题：**
```css
.title-bar h1 {
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  letter-spacing: 4px;
  color: var(--theme-color);        /* 数学=#00f5d4, 物理=各章色 */
  text-shadow: 0 0 20px var(--theme-color), 0 0 40px var(--theme-color);
}
```

**副标题：**
```css
.title-bar .subtitle {
  font-size: 14px;
  color: var(--text-dim);           /* 统一用低对比度灰 */
  margin-top: 8px;
  letter-spacing: 2px;
}
```

### 3. 挑战按钮位置

**强制规则：按钮必须在 `.title-bar` 内部，且居中。**

```html
<div class="title-bar">
  <h1>... chapter title ...</h1>
  <p class="subtitle">... subtitle ...</p>

  <!-- ✅ 正确：按钮在 title-bar 内居中 -->
  <div style="text-align:center;margin-top:16px;">
    <a class="btn btn-warn" href="index.html" style="padding:10px 28px;font-size:14px;">
      🎮 去挑战模式
    </a>
  </div>
</div>
```

**❌ 错误示范：**
- 按钮放在 `</header>` 之后 → 左对齐
- 按钮放在 header 外面 → 脱离标题区域

### 4. 卡片容器规范

```css
.card {
  background: rgba(20, 10, 31, 0.9);    /* 统一深色半透明 */
  border: 1px solid var(--theme-border); /* 主题色边框 */
  border-radius: 8px;
  padding: 28px;
  margin-bottom: 24px;
}
.card.hidden { display: none; }          /* 必须 */
```

### 5. 进度条规范

```css
.progress-bar {
  display: flex; gap: 8px;
  margin-bottom: 32px;
  justify-content: center;                /* 居中 */
}
.progress-seg {
  width: 60px; height: 4px;
  background: rgba(88,96,112,0.3);
  border-radius: 2px;
  transition: all 0.3s;
}
.progress-seg.active {
  background: var(--theme-color);
  box-shadow: 0 0 10px var(--theme-color);
}
```

**进度条段数 = 实际单元数（4-7个，按需），不强制7段。**

| 章节内容 | 建议单元数 | 进度条段数 |
|---|---|---|
| 内容饱满（如内能、欧姆定律） | 6-7 | 6-7段 |
| 内容中等（如电与磁） | 5 | 5段 |
| 内容集中（如电磁波、能源） | 4 | 4段 |

---

## 二、色彩差异化方案

### 数学主题色

| 变量 | 值 | 用途 |
|---|---|---|
| `--theme-color` | `#00f5d4` | 主强调色（标题、边框、进度条）|
| `--theme-glow` | `rgba(0,245,212,0.4)` | 发光效果 |
| `--theme-border` | `rgba(0,245,212,0.2)` | 卡片边框 |
| `--text-dim` | `#586070` | 副标题、元信息 |

### 物理主题色（按章节）

| 章节 | 主题色 | 说明 |
|---|---|---|
| ch10 内能 | `#9d00ff` (紫罗兰) | 热力学 |
| ch11 静电 | `#9d00ff` (紫罗兰) | 电学统一 |
| ch12 欧姆 | `#9d00ff` (紫罗兰) | 电学统一 |
| ch13 电功率 | `#9d00ff` (紫罗兰) | 电学统一 |
| ch14 电与磁 | `#9d00ff` (紫罗兰) | 电学统一 |
| ch15 电磁波 | `#9d00ff` (紫罗兰) | 电学统一 |
| ch16 原子 | `#00f0c8` (青绿) | 微观/宇宙 |
| ch17 能源 | `#ff6b35` (橙红) | 能源/环保 |

物理每章独立定义 `--theme-color`，数学全课程统一 `--accent: #00f5d4`。

---

## 三、导航统一

| 元素 | 规范 |
|---|---|
| 单元容器 | `<div class="card" id="ch1">` / `<div class="card hidden" id="chN">` |
| 单元数量 | **4-7个，按需决定**，不强制7个 |
| 进度段数 | 与单元数一致 |
| 切换函数 | `goTo(n)`：隐藏当前卡片，显示目标卡片，scrollTo(0,0)，更新进度 |
| 按钮文字 | "上一单元" / "下一单元" |
| 跨章链接 | ch1 上一单元 → 无；chN 下一单元 → 无（或跳下一章）|

---

## 四、质量检查清单

重构/新建任何 tutorial.html 时必须确认：

- [ ] `title-bar` 有 `text-align: center`
- [ ] `h1` 标题 `font-size: 32px; letter-spacing: 4px`
- [ ] 挑战按钮在 `title-bar` **内部**，且 `text-align: center`
- [ ] `.card.hidden { display: none; }` 已定义
- [ ] 进度条段数 = **实际单元数**，居中
- [ ] `goTo(n)` 函数正确实现卡片切换
- [ ] 色彩使用 `var(--theme-color)` 或对应 `--accent`，**不硬编码**

---

*规范版本：v1.1*
*适用日期：2026-05-18*
*制定依据：bridge-ch01（数学标杆）+ ch10（物理标杆）*
*更新：取消强制7单元，改为4-7个按需*
