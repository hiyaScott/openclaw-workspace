# SRPG 设计工具与资源

本目录收集了战棋游戏设计相关的工具、模板和参考资料。

---

## 🛠️ 数值设计与模拟工具

### Machinations
**网站**: https://machinations.io/

SRPG经济系统与战斗数值模拟的首选工具。

**适用场景**:
- 战斗循环模拟
- 资源经济平衡
- 抽卡概率验证
- 成长曲线可视化

**学习资源**:
- [Machinations 官方文档](https://docs.machinations.io/)
- [游戏经济设计教程](https://machinations.io/blog)

---

### Excel / Google Sheets
**免费工具**

战棋数值设计的基础工具，适合搭建数值模型。

**推荐模板**:
- `职业数值平衡表.xlsx` - 属性、成长率、技能威力
- `战斗公式验证表.xlsx` - 伤害、命中、TTK计算
- `关卡难度曲线表.xlsx` - 敌人配置、推荐战力

**模板位置**: `../assets/numerical-templates.md`

---

### Python + Pandas / NumPy
**开源工具**

适合批量模拟和数据可视化的编程方案。

**使用场景**:
- 大规模战斗模拟 (1000+场)
- 敏感性分析
- 胜率统计
- 数值异常检测

**本地脚本**: `../scripts/balance_test.py`

---

## 🎮 原型开发工具

### Godot Engine
**网站**: https://godotengine.org/

开源游戏引擎，有成熟的战棋框架。

**推荐教程**:
- GDQuest 战术RPG系列教程
- 社区战棋模板项目

**优势**:
- 免费开源
- 轻量快速
- GDScript易学
- 内置网格系统

---

### Unity
**网站**: https://unity.com/

商业引擎，资源丰富。

**推荐资源**:
- Grid-Based Movement 插件
- Turn-Based Toolkit
- A* Pathfinding Project

**适用**: 需要高质量原型的项目

---

### Tiled Map Editor
**网站**: https://www.mapeditor.org/

专业的2D地图编辑器，SRPG关卡设计利器。

**功能**:
- 多层地图编辑
- 图块集管理
- 对象层标注
- 多格式导出

---

## 📊 数据分析与可视化

### Tableau Public
**网站**: https://public.tableau.com/

免费版数据可视化工具。

**用途**:
- 角色属性分布可视化
- 关卡难度热力图
- 玩家行为分析 (如有数据)

---

### Desmos
**网站**: https://www.desmos.com/calculator

在线数学图形计算器。

**用途**:
- 伤害公式曲线可视化
- 成长曲线对比
- 数值函数调试

---

## 📚 参考资料与数据库

### 在线数据库
| 数据库 | 链接 | 内容 |
|--------|------|------|
| 天地劫英灵数据库 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/tdj-hero-database.html) | 158位角色 |
| 梦幻模拟战英雄数据库 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/langrisser-hero-database.html) | 208位角色 |
| 铃兰之剑角色数据库 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/sword-of-convallaria-hero-database.html) | 87位角色 |
| 三国志战棋版武将数据库 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/sanguo-hero-database.html) | 126位角色 |
| 三国望神州武将数据库 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/sanwang-hero-database.html) | 42位角色 |
| 五款游戏技能总览 | [查看](https://hiyascott.github.io/scott-portfolio/research/srpg-analysis/character-skills-enumeration.html) | 621位合集 |

---

## 📝 设计文档模板

### 本地模板

| 模板文件 | 用途 |
|----------|------|
| `level-design-template.md` | 关卡设计文档 |
| `numerical-templates.md` | 数值表模板说明 |
| `combat-formula.md` | 战斗公式设计 |

---

## 🌐 社区与论坛

### 中文社区
- **NGA游戏区**: https://bbs.nga.cn/ - 梦幻模拟战/天地劫板块
- **百度贴吧**: 火焰纹章吧、梦幻模拟战吧
- **Bilibili**: SRPG相关攻略与解析

### 国际社区
- **Reddit r/tacticalrpg**: https://www.reddit.com/r/tacticalrpg/
- **Reddit r/fireemblem**: https://www.reddit.com/r/fireemblem/
- **GameDev.net**: 游戏开发论坛

---

## 📖 推荐书籍

| 书名 | 作者 | 说明 |
|------|------|------|
| 《游戏设计艺术》 | Jesse Schell | 游戏设计基础 |
| 《平衡性设计的艺术》 | Ian Schreiber | 数值平衡专业书 |
| 《游戏机制——高级游戏设计技术》 | Ernest Adams | 机制设计深入 |

---

## 🔧 辅助工具

### 随机数测试
- **Random.org**: https://www.random.org/ - 真随机数
- **Dice Roller**: 游戏内骰子模拟

### 颜色工具
- **Coolors**: https://coolors.co/ - 配色方案
- **Color Hunt**: https://colorhunt.co/ - 调色板

### 字体资源
- **Google Fonts**: 免费商用字体
- **思源黑体/宋体**: 中文游戏推荐

---

## 💡 使用建议

1. **数值设计流程**:
   ```
   Excel建模 → Python验证 → Machinations可视化 → 游戏内测试
   ```

2. **工具组合**:
   - 快速验证: Excel + Python
   - 深度模拟: Machinations
   - 原型制作: Godot/Unity + Tiled
   - 数据可视化: Tableau/Desmos

3. **版本控制**:
   - 数值表使用 Git 管理
   - 定期备份模拟结果
   - 记录每次调整的影响

---

*最后更新: 2024年*
