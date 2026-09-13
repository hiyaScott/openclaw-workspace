# 数理课件系统 — 统一规范需求文档 v1.0

**状态：** 待 Scott 确认  
**制定日期：** 2026-05-18  
**适用范围：** 数学 grade6-9（34章）+ 物理 grade8-9（8章）

---

## 一、核心原则

1. **基础布局统一** — 数学和物理的页面骨架完全一致（标题、按钮、进度条、卡片）
2. **色彩主题差异化** — 数学用统一青色，物理按章节主题色
3. **单元数量灵活** — 不强制7单元，4-7个按需决定
4. **内容质量优先** — 不硬凑单元，该多少就多少

---

## 二、布局统一规范（数学+物理强制一致）

### 2.1 页面骨架

```html
<div id="app">
  <!-- 标题区域：必须居中 -->
  <div class="title-bar">
    <h1>第X章 标题</h1>
    <p class="subtitle">SUBTITLE · 年级 · 课时</p>
    <!-- 挑战按钮必须在 title-bar 内部，居中 -->
    <div style="text-align:center;margin-top:16px;">
      <a class="btn btn-warn" href="index.html">🎮 去挑战模式</a>
    </div>
  </div>

  <!-- 进度条：段数=实际单元数，居中 -->
  <div class="progress-bar" id="progress-bar">
    <div class="progress-seg active"></div>
    <div class="progress-seg"></div>
    ...
  </div>

  <!-- 单元卡片：数量按需（4-7个） -->
  <div class="card" id="ch1">...</div>
  <div class="card hidden" id="ch2">...</div>
  ...
</div>
```

### 2.2 Title Bar 规范

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
  color: var(--theme-color);
  text-shadow: 0 0 20px var(--theme-color), 0 0 40px var(--theme-color);
}
```

**副标题：**
```css
.title-bar .subtitle {
  font-size: 14px;
  color: var(--text-dim);
  margin-top: 8px;
  letter-spacing: 2px;
}
```

### 2.3 挑战按钮位置（强制）

- **必须在 `.title-bar` 内部**
- **必须 `text-align: center`**
- ❌ 不能放在 `</header>` 之后（会左对齐）
- ❌ 不能放在 header 外面（脱离标题区域）

### 2.4 进度条规范

```css
.progress-bar {
  display: flex; gap: 8px;
  margin-bottom: 32px;
  justify-content: center;
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

**关键：进度条段数 = 实际单元数（4-7段），不强制7段。**

### 2.5 卡片容器

```css
.card {
  background: rgba(20, 10, 31, 0.9);
  border: 1px solid var(--theme-border);
  border-radius: 8px;
  padding: 28px;
  margin-bottom: 24px;
}
.card.hidden { display: none; }
```

### 2.6 导航切换

```javascript
let currentCh = 1;
function goTo(n) {
  document.getElementById('ch' + currentCh).classList.add('hidden');
  document.getElementById('ch' + n).classList.remove('hidden');
  currentCh = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
  updateProgress();
}
```

---

## 三、色彩差异化方案

### 3.1 数学（全局统一）

| 变量 | 值 | 用途 |
|---|---|---|
| `--theme-color` | `#00f5d4` | 主强调色（标题、边框、进度条）|
| `--theme-glow` | `rgba(0,245,212,0.4)` | 发光效果 |
| `--theme-border` | `rgba(0,245,212,0.2)` | 卡片边框 |
| `--text-dim` | `#586070` | 副标题、元信息 |

### 3.2 物理（按章节主题色）

| 章节 | 主题色 | 说明 |
|---|---|---|
| ch10 内能 | `#9d00ff` 紫罗兰 | 热力学 |
| ch11 静电与电流 | `#9d00ff` 紫罗兰 | 电学统一 |
| ch12 欧姆定律 | `#9d00ff` 紫罗兰 | 电学统一 |
| ch13 电功率 | `#9d00ff` 紫罗兰 | 电学统一 |
| ch14 电与磁 | `#9d00ff` 紫罗兰 | 电学统一 |
| ch15 电磁波 | `#9d00ff` 紫罗兰 | 电学统一 |
| ch16 从原子到星系 | `#00f0c8` 青绿 | 微观/宇宙 |
| ch17 能源 | `#ff6b35` 橙红 | 能源/环保 |

---

## 四、单元数量规范（关键变更）

**不强制7单元。按内容量灵活决定：**

| 内容密度 | 建议单元数 | 进度条段数 | 示例章节 |
|---|---|---|---|
| 内容饱满 | 6-7 | 6-7段 | 内能、欧姆定律 |
| 内容中等 | 5 | 5段 | 电与磁 |
| 内容集中 | 4 | 4段 | 电磁波、能源 |

**每个单元内部结构（保持）：**
- 核心定义框
- 2个交互SVG实验（SMIL动画）
- 3个可展开例题（含Step分步）
- 5道测试题（含1陷阱题）
- 核心概念总结

**综合测试单元（最后一单元）：**
- 8道测试题 + 2个易错点回顾

---

## 五、当前实施计划

### 阶段1：物理微调（已完成，可能需精简）
- ch10-ch17 已全部重构为7单元
- 需要评估哪些章节可以精简为5-6单元

### 阶段2：数学批量重构（待启动）
- **28章需要重构**（仅bridge-ch01/ch02 + grade6 ch01-ch04 已符合标准）
- 按此统一规范批量处理
- 单元数量按各章内容量灵活决定

---

## 六、质量检查清单

重构/新建任何 tutorial.html 时必须确认：

- [ ] `title-bar` 有 `text-align: center`
- [ ] `h1` 标题 `font-size: 32px; letter-spacing: 4px`
- [ ] 挑战按钮在 `title-bar` **内部**，且 `text-align: center`
- [ ] `.card.hidden { display: none; }` 已定义
- [ ] 进度条段数 = **实际单元数**（4-7），居中
- [ ] `goTo(n)` 函数正确实现卡片切换
- [ ] 色彩使用 `var(--theme-color)`，不硬编码
- [ ] 单元数量合理，不硬凑

---

## 七、内容质量标准（6条硬性规则）

### 7.1 交互实验
- **每个教学单元 ≥2 个交互 SVG 实验**
- 使用 SMIL `<animate>` 标签实现动画（禁止 CSS 动画）
- 实验必须有明确的操作引导（按钮/滑块/点击）
- 实验与当单元知识点直接相关

### 7.2 可展开例题
- **每个教学单元 ≥3 个可展开例题**
- 使用 `.example-item` 结构：
```html
<div class="example-item" onclick="this.classList.toggle('expanded')">
  <div class="q">题干 + 选项（完整题目）</div>
  <div class="a">答案 + 解析步骤（Step 1/2/3）</div>
</div>
```
- `.q` 放完整题干和选项；`.a` 放答案和分步解析
- 例题必须带 Step 分步展开

### 7.3 测试题
- **每个教学单元 ≥5 道测试题**
- **其中 1 道必须是陷阱题**（常见易错点）
- 使用 `onclick="checkQuiz(this, true/false)"`
- 反馈文本规范：
  - 正确：`✓ 正确！` + 简短鼓励
  - 错误：`✗ 不对，再想想？` + 提示

### 7.4 Feedback ID 唯一性
- 格式：`fb[单元]-[题号]`，如 `fb3-1`、`fb3-2`
- **同一文件内禁止重复**
- 综合测试单元：`fb7-1` ~ `fb7-8`

### 7.5 例题结构正确性
- `.q` 必须包含完整题干 + 所有选项
- `.a` 必须包含正确答案 + 解析
- **严禁把题干藏在 `.a` 里**
- CSS 使用 `display:none/block` 切换，不用 `max-height` 过渡

### 7.6 JS/CSS 一致性
- `goTo(n)` 函数统一实现卡片切换
- `.card.hidden { display: none; }` 必须定义
- `updateProgress()` 染色当前进度段
- 禁止混用 `scrollIntoView`、`location.href` 等旧导航

---

## 八、单元内部结构模板

```html
<!-- 单元卡片 -->
<div class="card" id="ch1">
  <!-- 单元标题 -->
  <div class="card-header">
    <h2>🔥 单元N：标题</h2>
    <span class="meta">代号 XXX · 课时 1</span>
  </div>

  <!-- 核心定义框 -->
  <div class="concept-box">
    <div class="label">核心定义 / CORE DEFINITION</div>
    <p>定义内容...</p>
  </div>

  <!-- 交互实验 1 -->
  <div class="interactive-box">
    <div class="label">交互实验 / INTERACTIVE LAB</div>
    <svg>...</svg>
  </div>

  <!-- 交互实验 2 -->
  <div class="interactive-box">...</div>

  <!-- 可展开例题（3个） -->
  <div class="example-list">
    <div class="label">例题 / EXAMPLES</div>
    <div class="example-item" onclick="this.classList.toggle('expanded')">
      <div class="q">例题1题干...</div>
      <div class="a">
        <div class="step">Step 1: ...</div>
        <div class="step">Step 2: ...</div>
      </div>
    </div>
    <!-- 例题2、例题3 ... -->
  </div>

  <!-- 测试题（5道） -->
  <div class="quiz-box">
    <div class="label">单元测试 / QUIZ</div>
    <div class="quiz-question">题1...</div>
    <div class="quiz-options">
      <button class="quiz-btn" onclick="checkQuiz(this, true)">A</button>
      <button class="quiz-btn" onclick="checkQuiz(this, false)">B</button>
    </div>
    <div class="quiz-feedback" id="fb1-1"></div>
    <!-- 题2-5 ... -->
  </div>

  <!-- 核心概念总结 -->
  <div class="summary-box">
    <div class="label">核心概念 / KEY CONCEPTS</div>
    <ul>
      <li>要点1...</li>
      <li>要点2...</li>
    </ul>
  </div>

  <!-- 单元导航 -->
  <div class="btn-row">
    <button class="btn btn-ghost" onclick="goTo(0)">← 上一单元</button>
    <button class="btn" onclick="goTo(2)">下一单元 →</button>
  </div>
</div>
```

---

## 九、常见错误清单（禁止项）

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | 按钮放在 `<header>` 外面 | 放在 `.title-bar` 内部 |
| 2 | 进度条固定7段 | 段数 = 实际单元数 |
| 3 | 用 `max-height` 做例题展开 | 用 `display:none/block` |
| 4 | 题干藏在 `.a` 里 | `.q` 放完整题干+选项 |
| 5 | Feedback ID 重复 | 每题唯一，`fb单元-题号` |
| 6 | 混用 `scrollIntoView` | 统一用 `goTo(n)` |
| 7 | 硬凑7单元 | 按内容量定4-7个 |
| 8 | 交互实验用 CSS 动画 | 用 SMIL `<animate>` |
| 9 | 缺少陷阱题 | 每单元至少1道 |
| 10 | 例题没有 Step 分步 | 必须带 Step 1/2/3 |

---

## 十、当前实施计划

### 阶段1：物理微调
- ch10-ch17 已全部重构
- 需要评估哪些章节可以精简为5-6单元

### 阶段2：数学批量重构
- **28章需要重构**（仅6章已符合标准）
- 按此统一规范批量处理
- 单元数量按各章内容量灵活决定

---

*文档版本：v1.1*  
*待确认事项：*
1. 单元数量范围（4-7）是否合适？
2. 数学28章是否全部重构？还是分批处理？
3. 物理ch11-ch17是否需要精简单元数？
4. 内容质量标准（6条）是否完整？有无遗漏？
