# Jekyll 静态网站重构技能

> 将纯HTML静态网站迁移到Jekyll模板化架构的完整方法论。
> 适用于10+页面的网站项目，解决重复代码、维护困难问题。

## 核心能力

1. **模板继承架构设计** - 四层布局体系 (default → specific)
2. **组件化开发** - 提取可复用include组件
3. **数据驱动内容** - YAML数据文件集中管理
4. **渐进式迁移** - 零停机迁移策略
5. **视觉资产保留** - 特效/动画无缝迁移

## 典型应用场景

- **多页面静态网站** - 导航/页脚重复代码遍布全站
- **内容频繁更新** - 新增页面需手动更新多处
- **主题管理混乱** - 深色/浅色模式文件分离
- **团队协作困难** - 修改设计需同步多个文件

## 迁移收益

| 指标 | 迁移前 | 迁移后 | 改善 |
|------|--------|--------|------|
| 修改导航工作量 | N个文件 | 1个文件 | **(N-1)/N ↓** |
| 新增内容步骤 | 5步 | 1步 | **80%↓** |
| 代码重复率 | ~60% | ~5% | **92%↓** |
| 主题切换 | 文件复制 | CSS变量 | **即时** |

## 执行步骤

### 阶段1：诊断与备份

```bash
# 统计重复代码行数
find . -name "*.html" -exec grep -l "<nav" {} \; | wc -l

# 创建备份
git tag -a "pre-jekyll-$(date +%Y%m%d)" -m "Pre-Jekyll backup"
git archive --format=tar.gz -o backup-pre-jekyll.tar.gz HEAD
```

### 阶段2：框架搭建

```
jekyll-site/
├── _config.yml              # 站点配置
├── _data/
│   └── navigation.yml       # 导航数据
├── _includes/
│   ├── head.html            # 头部模板
│   ├── header.html          # 导航模板
│   ├── footer.html          # 页脚模板
│   └── game-card.html       # 卡片组件
├── _layouts/
│   ├── default.html         # 基础布局
│   ├── home.html            # 主页布局
│   └── game.html            # 游戏页布局
└── _games/                  # 游戏集合
    └── *.md                 # 游戏内容
```

### 阶段3：模板实现

**default.html** - 基础骨架:
```html
<!DOCTYPE html>
<html lang="{{ site.lang }}">
<head>{% include head.html %}</head>
<body>
  {% include header.html %}
  <main>{{ content }}</main>
  {% include footer.html %}
  {% include scripts.html %}
</body>
</html>
```

**home.html** - 继承扩展:
```html
---
layout: default
body_class: home-page
---
<section class="hero">...</section>
<section class="featured-games">
  {% for game in site.data.games limit:6 %}
    {% include game-card.html game=game %}
  {% endfor %}
</section>
```

### 阶段4：数据迁移

```yaml
# _data/games.yml
games:
  - id: word-alchemy
    title: 词语炼金术
    category: puzzle
    description: 文字合成游戏
    path: /games/word-alchemy/
    thumbnail: /assets/images/games/word-alchemy.png
    featured: true
```

### 阶段5：内容迁移

将 `games/word-alchemy/index.html` → `_games/word-alchemy.md`:

```markdown
---
layout: game
title: 词语炼金术
description: 文字合成与创意游戏
category: puzzle
---

<!-- 游戏HTML嵌入 -->
<div class="game-container">
  ...
</div>
```

### 阶段6：样式迁移

**Critical CSS** (内联于head.html):
```css
:root {
  --color-header: #1a1a1a;
  --color-bg: #f8f8f8;
  --neon-accent: #00f0ff;  /* 保留霓虹主题 */
}
```

**特效保留清单**:
- CRT扫描线 → `_sass/_crt-effect.scss`
- 霓虹发光 → `_sass/_neon-theme.scss`
- 故障艺术 → `_sass/_glitch.scss`
- 粒子背景 → `assets/js/particles.js`

### 阶段7：测试验证

```bash
# 本地构建
bundle exec jekyll serve

# 验证清单
curl -s http://localhost:4000/ | grep -q "Player & Creator" && echo "✓ 主页OK"
curl -s http://localhost:4000/games/ | grep -q "词语炼金术" && echo "✓ 游戏列表OK"
```

### 阶段8：部署切换

```bash
# GitHub Pages配置
git remote add jekyll-origin https://github.com/user/jekyll-site.git
git push jekyll-origin main

# 域名切换（一次性）
# GitHub Pages Settings → 新仓库
```

## 关键技术决策

### 为什么选Jekyll？

| 方案 | 学习曲线 | SEO | 托管 | 维护 |
|------|---------|-----|------|------|
| 纯HTML | 低 | 好 | 任意 | 高 |
| JS注入 | 低 | 差 | 任意 | 中 |
| Jekyll | 中 | 好 | GitHub Pages | 低 |
| Hugo | 中 | 好 | 任意 | 低 |
| 自建脚本 | 高 | 好 | 任意 | 高 |

**选择Jekyll的关键因素**:
- GitHub Pages原生支持（零托管成本）
- Liquid模板语言简单直观
- Ruby生态成熟稳定
- 与Minimal Mistakes等主题兼容

### 模板继承深度

推荐四层结构:
```
default (HTML骨架)
  └── home/game/page (页面类型)
        └── specific-variant (特殊变体)
```

避免过深 (>4层)，保持可维护性。

## 常见问题

### Q: 如何保留原有URL结构？
**A**: 使用Jekyll的permalink配置:
```yaml
# _config.yml
permalink: /:categories/:title/

# 或单文件覆盖
---
permalink: /games/word-alchemy/
---
```

### Q: 如何处理大量现有内容？
**A**: 编写迁移脚本:
```python
# scripts/migrate-games.py
import os, re, yaml

for html_file in glob('portfolio-blog/games/*/index.html'):
    game_data = extract_from_html(html_file)
    create_md_file(game_data)
```

### Q: 如何确保视觉一致性？
**A**: 
1. 提取原站CSS变量映射到 `:root`
2. 保留关键动画keyframes
3. 视觉回归测试（截图对比）

## 最佳实践

1. **备份优先** - 永远先打tag再迁移
2. **数据先行** - 先迁移YAML数据，再处理模板
3. **渐进验证** - 每阶段完成都本地build验证
4. **文档同步** - 迁移计划与执行同步更新
5. **保留痕迹** - 旧站备份至少保留6个月

## 参考资源

- [Jekyll官方文档](https://jekyllrb.com/docs/)
- [Minimal Mistakes主题](https://mmistakes.github.io/minimal-mistakes/)
- [Liquid模板指南](https://shopify.github.io/liquid/)
- [GitHub Pages + Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll)

## 版本历史

- 2026-04-18: 初版 - Scott Portfolio重构实践总结