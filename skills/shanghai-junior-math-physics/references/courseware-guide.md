# 课件制作指南

> HTML/CSS/JS 可交互网页课件制作规范

---

## 一、课件结构模板

### 最小可运行模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>课件标题 - 沪教版X年级</title>
<style>
  /* 基础变量 */
  :root {
    --primary: #2563eb;
    --accent: #f59e0b;
    --success: #10b981;
    --error: #ef4444;
    --bg: #f8fafc;
    --card: #ffffff;
    --text: #0f172a;
    --muted: #64748b;
    --border: #e2e8f0;
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
  }
  /* 重置与基础 */
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
  .container { max-width: 960px; margin: 0 auto; padding: 24px; }
  /* 卡片 */
  .card { background: var(--card); border-radius: 12px; padding: 28px; margin-bottom: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); }
  .card h2 { font-size: 1.4rem; color: var(--primary); margin-bottom: 16px; }
  /* 响应式 */
  @media (max-width: 640px) { .card { padding: 20px; } }
</style>
</head>
<body>
<div class="container">
  <!-- 课件内容区 -->
</div>
<script>
  // 交互逻辑
</script>
</body>
</html>
```

---

## 二、页面组件库

### 2.1 头部 Banner
```html
<div style="text-align:center; padding:40px 0; background:linear-gradient(135deg, var(--primary) 0%, #1d4ed8 100%); color:white; border-radius:16px; margin-bottom:32px;">
  <h1 style="font-size:2rem; font-weight:700; margin-bottom:8px;">课件标题</h1>
  <div style="opacity:0.9;">X年级第X学期 · 第X章</div>
  <div style="display:inline-block; background:rgba(255,255,255,0.2); padding:4px 12px; border-radius:20px; font-size:0.85rem; margin-top:12px;">沪教版 2024</div>
</div>
```

### 2.2 公式展示框
```html
<div style="background:#f1f5f9; border-left:4px solid var(--primary); padding:20px; border-radius:8px; font-size:1.2rem; text-align:center; margin:16px 0; font-family:'Cambria Math','Times New Roman',serif;">
  ax² + bx + c = 0
</div>
```

### 2.3 步骤揭示组件
```html
<div class="step" style="display:flex; align-items:center; gap:16px; padding:16px; background:#f8fafc; border-radius:8px; border:1px solid var(--border); margin:8px 0;">
  <div style="width:36px; height:36px; background:var(--primary); color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:bold;">1</div>
  <div style="flex:1;">
    <div style="font-family:'Cambria Math',serif; font-size:1.1rem;">步骤公式</div>
    <div style="font-size:0.85rem; color:var(--muted); margin-top:4px;">说明文字</div>
  </div>
</div>
```

### 2.4 按钮
```html
<button style="background:var(--primary); color:white; border:none; padding:12px 28px; border-radius:8px; font-size:1rem; cursor:pointer; transition:all 0.2s;">
  点击交互
</button>
```

### 2.5 提示框
```html
<div style="background:#fffbeb; border-left:4px solid var(--accent); padding:16px; border-radius:8px; margin:16px 0;">
  <strong style="color:var(--accent);">💡 提示：</strong>提示内容
</div>
```

### 2.6 结果展示框
```html
<div id="result" style="background:#ecfdf5; border:2px solid var(--success); border-radius:12px; padding:24px; text-align:center; display:none;">
  <div style="font-size:1.3rem; font-weight:bold; color:var(--primary);">结果内容</div>
</div>
```

---

## 三、交互组件

### 3.1 逐步揭示（推导动画）

```javascript
let currentStep = 0;
const steps = document.querySelectorAll('.step');

function revealNext() {
  if (currentStep < steps.length) {
    steps[currentStep].style.opacity = '0';
    steps[currentStep].style.transform = 'translateX(-20px)';
    steps[currentStep].style.transition = 'all 0.5s ease';
    
    requestAnimationFrame(() => {
      steps[currentStep].style.opacity = '1';
      steps[currentStep].style.transform = 'translateX(0)';
    });
    
    currentStep++;
  }
}
```

### 3.2 计算器组件

```javascript
function solveQuadratic(a, b, c) {
  const delta = b * b - 4 * a * c;
  
  if (delta > 0) {
    const x1 = (-b + Math.sqrt(delta)) / (2 * a);
    const x2 = (-b - Math.sqrt(delta)) / (2 * a);
    return { type: 'two', x1, x2, delta };
  } else if (delta === 0) {
    const x = -b / (2 * a);
    return { type: 'one', x, delta };
  } else {
    return { type: 'none', delta };
  }
}
```

### 3.3 选择题交互

```javascript
function createQuiz(question, options, correctIndex, explain) {
  const container = document.getElementById('quiz');
  container.innerHTML = `<p style="font-size:1.1rem; margin-bottom:16px;">${question}</p>`;
  
  options.forEach((opt, i) => {
    const btn = document.createElement('button');
    btn.className = 'quiz-option';
    btn.textContent = opt;
    btn.onclick = () => {
      // 禁用所有按钮
      document.querySelectorAll('.quiz-option').forEach(b => b.disabled = true);
      // 标记对错
      if (i === correctIndex) {
        btn.style.borderColor = 'var(--success)';
        btn.style.background = '#ecfdf5';
      } else {
        btn.style.borderColor = 'var(--error)';
        btn.style.background = '#fef2f2';
        document.querySelectorAll('.quiz-option')[correctIndex].style.borderColor = 'var(--success)';
        document.querySelectorAll('.quiz-option')[correctIndex].style.background = '#ecfdf5';
      }
      // 显示解析
      document.getElementById('explain').textContent = explain;
    };
    container.appendChild(btn);
  });
}
```

### 3.4 Canvas 几何作图

```javascript
function drawTriangle(ctx, x, y, a, b, c, angles) {
  // 简化的三角形绘制
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + a, y);
  ctx.lineTo(x + b * Math.cos(angles[0]), y - b * Math.sin(angles[0]));
  ctx.closePath();
  ctx.stroke();
  
  // 标注边长
  ctx.font = '14px sans-serif';
  ctx.fillText(`a=${a}`, x + a/2, y + 20);
}
```

### 3.5 函数图像绘制

```javascript
function plotFunction(canvas, fn, range, color = '#2563eb') {
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  
  // 坐标系转换
  const scaleX = width / (range.xMax - range.xMin);
  const scaleY = height / (range.yMax - range.yMin);
  
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  
  for (let px = 0; px < width; px++) {
    const x = range.xMin + px / scaleX;
    const y = fn(x);
    const py = height - (y - range.yMin) * scaleY;
    
    if (px === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  
  ctx.stroke();
}
```

---

## 四、常见课件类型

### 4.1 概念引入型
结构：情境问题 → 观察发现 → 归纳定义 → 巩固练习

### 4.2 公式推导型
结构：回顾预备 → 逐步推导 → 揭示公式 → 验证应用

### 4.3 实验探究型（物理）
结构：提出问题 → 猜想假设 → 虚拟实验 → 数据收集 → 得出结论

### 4.4 解题方法型
结构：典型例题 → 方法提炼 → 变式训练 → 方法迁移

### 4.5 复习总结型
结构：知识网络 → 易错回顾 → 综合练习 → 自我检测

---

## 五、设计原则

### 一页一概念
每张"幻灯片"（card）只讲一个知识点，信息密度控制在学生 3-5 分钟内能消化。

### 渐进揭示
内容不要一次性全展示。用按钮、滚动或自动动画分步出现。

### 交互优先
每页至少一个可操作的元素：
- 输入数字看结果变化
- 拖拽滑动条观察图像变化
- 点击选择题即时反馈
- 开关控制实验变量

### 即时反馈
学生操作后，0.5 秒内给出反馈：
- 正确：绿色、✓、简短鼓励
- 错误：红色、✗、提示思考方向（不直接给答案）

### 视觉引导
- 重点用蓝色（primary）
- 警告/错误用红色（error）
- 成功/正确用绿色（success）
- 提示/注意用琥珀色（accent）

---

## 六、技术注意事项

### 兼容性
- 不使用需要编译的前端框架（React/Vue/Angular）
- 纯 Vanilla JS，确保浏览器直接打开即可运行
- 避免 CSS Grid 的复杂嵌套（部分旧设备支持不好）
- 数学公式优先用 Unicode 字符（如 x²、√、π），复杂公式可引入 KaTeX

### 性能
- 图片使用 WebP 或 SVG
- 动画使用 CSS transform（GPU 加速）
- Canvas 绘制时避免每帧重绘静态内容

### 可访问性
- 所有交互元素有明确的 hover/active 状态
- 颜色不是唯一的信息传递方式（配合图标/文字）
- 文字与背景对比度 ≥ 4.5:1

---

## 七、文件命名规范

```
YYYY-MM-DD-章节名-课件类型.html

示例：
2026-05-03-ch17-quadratic-formula-derivation.html
2026-05-03-ch18-proportional-function-graph.html
```

---

## 八、部署流程

1. 课件完成后保存到 `research/shanghai-junior-math-physics/courseware/`
2. 复制到 `portfolio-blog/kimi-claw/shanghai-junior-math-physics/`
3. 更新 `index.html` 目录
4. git commit & push
5. QA 验证线上可访问

---

*好的课件不是把黑板搬到屏幕上，而是让学生动手发现规律。*
