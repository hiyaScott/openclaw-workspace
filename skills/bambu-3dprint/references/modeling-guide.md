# 建模工具深度对比

## 选型决策树

```
你的需求是什么？
│
├─ 完全零基础 ───────→ Tinkercad
│
├─ 要做工程零件 ─────┬─ 想要免费 → FreeCAD
│                    └─ 专业需求 → Fusion 360
│
├─ 喜欢编程 ─────────→ OpenSCAD
│
└─ 要做艺术/有机造型 → Blender
```

---

## Tinkercad

**网址**: https://www.tinkercad.com

### 优点
- 浏览器运行，无需安装
- 拖拽式操作，10分钟上手
- 适合教学和儿童

### 局限
- 只能做简单几何组合
- 无法精确参数控制
- 复杂模型困难

### 适合场景
- 第一次接触3D打印
- 快速验证想法
- 教学演示

---

## Fusion 360 (推荐)

**网址**: https://www.autodesk.com/products/fusion-360

### 优点
- 工业级功能
- 参数化设计，随时修改
- 装配体、工程图、仿真一体
- 学生/爱好者免费

### 学习路径
1. **第一周**: 草图绘制、拉伸/旋转
2. **第二周**: 圆角/倒角、孔特征
3. **第三周**: 装配体、约束关系
4. **第四周**: 工程图、渲染

### 关键快捷键
| 快捷键 | 功能 |
|--------|------|
| L | 直线 |
| R | 矩形 |
| C | 圆 |
| E | 拉伸 |
| F | 圆角 |
| J | 装配约束 |

---

## FreeCAD

**网址**: https://www.freecad.org

### 优点
- 完全开源免费
- 功能接近商业软件
- 活跃的社区

### 缺点
- 界面较老旧
- 学习曲线陡峭
- 稳定性不如商业软件

### 工作台选择
| 工作台 | 用途 |
|--------|------|
| Part Design | 参数化零件设计 |
| Sketcher | 2D草图 |
| Assembly | 装配体 |
| Mesh Design | 网格修复 |

---

## OpenSCAD

**网址**: https://openscad.org

### 代码示例
```openscad
// Arduino UNO 外壳底板
$fn = 50;  // 圆的分段数

// 外壳主体
difference() {
    // 外形
    cube([70, 55, 12]);
    
    // 内部挖空
    translate([2, 2, 2])
        cube([66, 51, 11]);
    
    // USB口开口
    translate([-1, 35, 4])
        cube([5, 12, 10]);
}

// 螺丝柱
module standoff(x, y) {
    translate([x, y, 0])
        difference() {
            cylinder(h=8, d=6);
            cylinder(h=9, d=2.8);
        }
}

standoff(5, 5);
standoff(5, 50);
standoff(65, 5);
standoff(65, 50);
```

### 适合人群
- 程序员背景
- 需要版本控制CAD文件
- 参数化设计需求强

---

## Blender

**网址**: https://www.blender.org

### 特点
- 功能极其强大
- 学习曲线极陡峭
- 非参数化（修改困难）

### 3D打印专用插件
- **3D Print Toolbox**: 检查模型可打印性
- **Mesh Tools**: 修复网格问题

### 适合场景
- 有机造型（人物、生物）
- 艺术设计
- 已经熟悉Blender的用户

---

## 推荐组合

| 用户类型 | 主工具 | 辅助工具 |
|----------|--------|----------|
| 初学者 | Tinkercad → Fusion 360 | Bambu Studio |
| 工程师 | Fusion 360 | FreeCAD |
| 程序员 | OpenSCAD | Fusion 360 |
| 艺术家 | Blender | Fusion 360 (工程件) |
| 预算敏感 | FreeCAD | Tinkercad |
