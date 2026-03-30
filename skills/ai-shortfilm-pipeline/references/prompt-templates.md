# 提示词模板库

> AI短片制作各环节的提示词模板，提高一致性和效率

---

## 一、角色设计提示词

### 1.1 基础角色公式

```
[风格] + [主体] + [核心特征] + [细节描述] + [光线/氛围] + [质量词]
```

### 1.2 风格词库

| 风格 | 关键词 | 适用工具 |
|------|--------|----------|
| 皮克斯卡通 | Pixar style, 3D render, cute | 豆包 |
| 写实渲染 | photorealistic, cinematic lighting | 即梦 |
| 赛博朋克 | cyberpunk, neon lights, dystopian | 即梦/豆包 |
| 末世废土 | post-apocalyptic, rusted metal, ruins | 即梦 |
| 治愈温情 | Studio Ghibli style, warm colors | 豆包 |
| 复古怀旧 | vintage, film grain, muted colors | 即梦 |

### 1.3 角色特征描述模板

**机器人角色**：
```
生锈的金属质感，温暖的做旧棕色调，
圆形复古眼睛（深色护目镜风格），
精致机械关节（工业美学细节），
履带底座（稳定移动方式），
双手捧花盆（虔诚守护姿态）
```

**人类角色**：
```
[年龄]岁[性别]，[面部特征]，
穿着[服装风格]，[表情/神态]，
[动作/姿势]，[光线描述]
```

### 1.4 完整示例

**皮克斯风格机器人**：
```
皮克斯3D风格，可爱的机器人角色，生锈的金属表面（温暖棕色），
圆形复古眼睛像老式相机，双手捧着一朵白色小花，
履带式底座，精致机械关节细节，
夕阳逆光，暖金色调，柔和轮廓光，
高清8K，细腻材质
```

**写实风格机器人**：
```
写实渲染，末世废墟中的机器人，严重生锈的金属表面，
圆形复古眼睛（深色玻璃质感），
身体布满划痕和风化痕迹，
双手捧着一朵在废墟中生长的白色小花，
夕阳金色逆光，体积光，景深效果，
电影感构图，8K超清画质
```

---

## 二、场景设计提示词

### 2.1 场景公式

```
[时间] + [地点] + [主体元素] + [光线] + [色彩] + [氛围] + [质量词]
```

### 2.2 时间词库

- 清晨：dawn, early morning, soft light
- 正午：noon, harsh sunlight
- 黄昏：golden hour, sunset, warm light
- 夜晚：night, moonlight, starry sky
- 阴天：overcast, diffused light
- 暴雨：heavy rain, storm, dramatic lighting

### 2.3 地点词库

**末世场景**：
```
destroyed city, post-apocalyptic ruins, abandoned buildings,
cracked concrete, overgrown vegetation, rusted vehicles
```

**自然场景**：
```
dense forest, misty mountains, calm lake, blooming field,
ancient tree, cascading waterfall
```

**城市场景**：
```
neon-lit street, cyberpunk cityscape, rooftop garden,
old town alley, modern skyscraper
```

### 2.4 光线词库

| 光线类型 | 关键词 | 效果 |
|----------|--------|------|
| 金色逆光 | golden hour backlighting, rim light | 温暖、轮廓感 |
| 体积光 | god rays, volumetric lighting | 神圣、梦幻 |
| 侧光 | side lighting, chiaroscuro | 立体感、戏剧性 |
| 顶光 | top lighting, overhead light | 压迫感、紧张 |
| 柔光 | soft diffused light, overcast | 平静、自然 |
| 轮廓光 | rim light, edge lighting | 分离主体和背景 |

### 2.5 氛围词库

**情绪氛围**：
- 温馨：warm, cozy, peaceful, heartwarming
- 孤独：lonely, isolated, melancholic
- 希望：hopeful, uplifting, inspiring
- 紧张：tense, dramatic, suspenseful
- 神秘：mysterious, ethereal, dreamlike

**环境氛围**：
- 末世：desolate, abandoned, decaying
- 赛博朋克：neon-drenched, futuristic, gritty
- 治愈：whimsical, magical, serene

### 2.6 完整示例

**夕阳废墟**：
```
末世城市废墟，黄昏金色时刻，
倒塌的建筑物和生锈的车辆，
地面裂缝中长出的野草和野花，
夕阳金色逆光，长长的影子，
暖色调（橙、金、棕），孤独但温暖的氛围，
电影感构图，广角镜头，景深效果，8K画质
```

**暴雨场景**：
```
末世废墟中的暴雨夜，
闪电照亮破碎的建筑轮廓，
雨水形成溪流流过地面，
冷色调（蓝、灰）对比暖色警示灯，
戏剧性光线，体积雨效果，
电影感，高对比度，8K
```

---

## 三、三视图生成提示词

### 3.1 三视图公式

**基础**：
```
[角色描述] + [视角：正视图/侧视图/背视图] + [纯白背景] + [技术规范]
```

**技术规范**：
```
纯白背景，角色居中，全身完整显示，
无阴影，无环境元素，
技术设计图风格，清晰轮廓，
正面/侧面/背面视角标注
```

### 3.2 三视图一致性技巧

1. **固定描述词**（95%相同）：
   - 风格、材质、核心特征保持一致
   - 只改变视角描述

2. **使用参考图**：
   - 正视图 → 作为侧视图的参考图
   - 保持种子值一致

3. **完整示例**：

**正视图**：
```
皮克斯风格机器人，正视图，
生锈金属质感（温暖棕色），
圆形复古眼睛，双手捧花盆，履带底座，
纯白背景，角色居中，全身显示，
技术设计图风格，清晰轮廓线，正视图标注，
高清8K
```

**侧视图**：
```
皮克斯风格机器人，侧视图，
生锈金属质感（温暖棕色），
圆形复古眼睛，双手捧花盆（侧面可见），履带底座侧面，
纯白背景，角色居中，全身显示，
技术设计图风格，清晰轮廓线，侧视图标注，
高清8K
```

**背视图**：
```
皮克斯风格机器人，背视图，
生锈金属质感（温暖棕色），
背部机械结构，履带底座背面，
纯白背景，角色居中，全身显示，
技术设计图风格，清晰轮廓线，背视图标注，
高清8K
```

---

## 四、视频生成提示词

### 4.1 图生视频公式

```
[镜头运动] + [主体动作] + [环境互动] + [光线/氛围变化] + [速度/节奏]
```

### 4.2 镜头运动词库

| 运动 | 关键词 | 效果 |
|------|--------|------|
| 推进 | slow push in, dolly in | 强调主体 |
| 拉出 | pull back, zoom out | 展示环境 |
| 平移 | pan left/right, track | 跟随移动 |
| 上升 | crane up, rise | 宏大感 |
| 环绕 | orbit, circle around | 展示360度 |
| 固定 | static shot, locked off | 稳定、观察 |

### 4.3 动作描述词库

**机器人动作**：
```
头部缓缓转向，机械臂轻轻抬起，履带缓慢前进，
警示灯微弱闪烁，身体微微前倾，关节灵活转动
```

**自然动作**：
```
花瓣随风飘动，树叶轻轻摇曳，阳光缓慢移动，
云朵缓缓飘动，水波微微荡漾
```

### 4.4 完整示例

**机器人守护镜头**：
```
慢速推进镜头，机器人缓缓转头看向花朵，
机械手指微微收紧，身体轻微前倾，
夕阳余晖在金属表面缓慢移动，
警示灯以2秒间隔微弱闪烁，
背景废墟逐渐变暗，暖色调转为冷色调，
电影感节奏，缓慢而温暖
```

**暴雨保护镜头**：
```
特写镜头，机器人用机械臂和身体护住花朵，
雨水顺着金属表面流下，形成小水流，
闪电瞬间照亮场景（每3-4秒一次），
机器人在风雨中轻微晃动但保持稳定，
冷色调主导，暖色警示灯闪烁，
紧张但坚定的氛围
```

---

## 五、分镜首帧提示词

### 5.1 首帧公式

```
[镜头类型] + [主体位置/动作] + [光线] + [氛围] + [构图]
```

### 5.2 镜头类型词库

- 远景：wide shot, establishing shot
- 中景：medium shot, waist up
- 特写：close-up, extreme close-up
- 过肩：over-the-shoulder
- 主观：POV, first-person view

### 5.3 构图词库

- 三分法：rule of thirds, off-center
- 中心：centered, symmetrical
- 框架：framed, through foreground
- 引导线：leading lines, perspective
- 留白：negative space, minimal

### 5.4 完整示例

**开场镜头（远景）**：
```
广角远景，机器人独自站在废墟中央，
夕阳从画面右侧照射，长长的影子向左延伸，
手中花朵是唯一亮色（白色），
废墟形成框架构图，
暖金色调，孤独但充满希望的氛围，
电影画幅（2.35:1）
```

**高潮镜头（特写）**：
```
特写镜头，机器人眼睛（圆形复古镜头），
反射出花朵的影像，
夕阳在镜头表面形成光斑，
浅景深，背景完全虚化，
暖色调，情感浓度高，
4K画质，细腻材质
```

---

## 六、质量词库

### 6.1 通用质量词

**基础**：
```
high quality, detailed, sharp focus, clear
```

**高级**：
```
8K resolution, ultra detailed, photorealistic,
cinematic lighting, professional photography,
award-winning composition
```

**艺术**：
```
masterpiece, best quality, highly detailed,
intricate details, beautiful lighting
```

### 6.2 负面提示词（避免什么）

```
blurry, low quality, distorted, deformed,
bad anatomy, extra limbs, missing limbs,
watermark, signature, text, logo
```

---

## 七、提示词优化技巧

### 7.1 权重控制

**强调**（增加权重）：
```
(关键词:1.2)  # 增加20%权重
[关键词]       # 某些工具的强调语法
```

**弱化**（减少权重）：
```
(关键词:0.8)  # 减少20%权重
```

### 7.2 分步描述

复杂场景分步骤描述：
```
Step 1: 背景和光线
Step 2: 主体和位置
Step 3: 细节和氛围
Step 4: 质量词
```

### 7.3 A/B测试方法

1. 固定80%的描述词
2. 改变20%的变量（光线/角度/氛围）
3. 对比结果，记录最佳组合
4. 形成个人词库

---

## 八、常用模板速查

### 快速启动模板

**角色设计**：
```
[风格]风格，[主体]，[核心特征]，[细节]，[光线]，高清8K
```

**场景设计**：
```
[时间]的[地点]，[主体]，[光线]，[色彩]，[氛围]，电影感8K
```

**视频生成**：
```
[镜头运动]，[主体动作]，[环境互动]，[光线变化]，电影感节奏
```

---

*最后更新：2026-03-31*
