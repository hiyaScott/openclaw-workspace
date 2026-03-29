# hiyamax AI短片制作与发布流程

> 标准化流程文档 - 从剧本到发布的完整工作流

---

## 流程概览

```
剧本创作 → 角色设计 → 视频生成 → 后期剪辑 → 发布部署
   (飞书)    (即梦AI)    (海螺/可灵)   (FFmpeg)   (GitHub Pages)
```

---

## 第一阶段：剧本创作

### 1.1 输入
- **来源**: 飞书对话讨论
- **内容**: 剧本大纲、分镜描述、角色设定
- **输出**: `docs/shortfilm-XXX.html` 或飞书文档

### 1.2 关键决策点
| 决策项 | 选项 | 影响 |
|--------|------|------|
| 视频平台 | 海螺 / 可灵 | 影响API调用方式 |
| 时长规划 | 总时长 / 分镜数 | 影响成本和制作周期 |
| 角色一致性方案 | 首尾帧 / 首帧 / 参考图 | 影响素材准备 |

### 1.3 交付物
- [ ] 完整剧本（含分镜表）
- [ ] 角色设计需求
- [ ] 分镜提示词草稿

---

## 第二阶段：角色设计

### 2.1 工具
- **即梦AI** (Jimeng) - 火山引擎
- **可图** (Kolors) - 备选

### 2.2 流程
1. 上传参考图（如有）
2. 输入角色描述prompt
3. 生成多个候选图
4. 选择/调整至满意
5. 导出高清角色图

### 2.3 交付物
- [ ] 主角正面图（用于视频生成参考）
- [ ] 主角多角度图（可选）
- [ ] 角色设计说明文档

### 2.4 文件命名规范
```
robo_no5_character.jpg       # 手绘风格角色图
robo_no5_realistic_front.jpg # 写实风格正面图
robo_no5_realistic_side.jpg  # 写实风格侧面图
```

---

## 第三阶段：视频生成

### 3.1 视频平台选择

#### 方案A: 海螺AI (推荐)
```python
# API端点
POST https://www.dmxapi.cn/v1/video_generation

# 参数
{
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "场景描述 [运镜指令]",
    "first_frame_image": "角色图URL",  # 可选
    "last_frame_image": "尾帧图URL",    # 可选（首尾帧模式）
    "duration": 10,  # 6或10秒
    "resolution": "768P"
}
```

#### 方案B: 可灵AI
```python
# API端点（DMXAPI）
POST https://www.dmxapi.cn/v1/responses

# 参数
{
    "model": "kling-v2-6-image2video",
    "input": "提示词",
    "image": "图片URL",
    "mode": "pro",
    "duration": 5,  # 5或10秒
    "aspect_ratio": "16:9"
}
```

### 3.2 角色一致性策略

#### 策略1: 首尾帧模式（推荐）
- **适用**: 需要精确控制角色起止状态
- **参数**: `first_frame_image` + `last_frame_image`
- **效果**: ⭐⭐⭐⭐⭐

#### 策略2: 首帧模式
- **适用**: 只需要固定起始画面
- **参数**: `first_frame_image`
- **效果**: ⭐⭐⭐⭐

#### 策略3: 参考图模式（海螺网页端）
- **适用**: 最佳角色一致性
- **方式**: 网页端【主体参考】功能
- **限制**: API不支持
- **效果**: ⭐⭐⭐⭐⭐

### 3.3 批量生成脚本
使用 `/root/.openclaw/workspace/tools/hailuo_shotXX.py` 脚本批量生成：

```bash
# 设置API密钥
export DMXAPI_KEY="sk-..."

# 执行生成脚本
python3 tools/hailuo_shot01.py
python3 tools/hailuo_shot02.py
...
```

### 3.4 交付物
- [ ] 各分镜视频文件 (MP4)
- [ ] 任务信息JSON（含task_id等）
- [ ] 视频质量检查报告

---

## 第四阶段：后期剪辑

### 4.1 工具
- **FFmpeg** - 视频合并、字幕、音频

### 4.2 剪辑流程

#### 步骤1: 合并视频片段
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

#### 步骤2: 添加硬字幕
```bash
ffmpeg -i output.mp4 -vf "drawtext=fontfile=NotoSerifCJK.ttf:text='字幕内容':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-100" -c:a copy final.mp4
```

#### 步骤3: 添加BGM
```bash
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -b:a 192k -shortest final_with_bgm.mp4
```

### 4.3 字幕规范
- **字体**: Noto Serif CJK（支持中文）
- **字号**: 48px
- **位置**: 底部居中
- **颜色**: 白色，带阴影

### 4.4 交付物
- [ ] 成片视频 (MP4, 1920x1080)
- [ ] 字幕文件（如有软字幕需求）
- [ ] 音频文件（分离保存）

---

## 第五阶段：发布部署

### 5.1 部署平台
- **GitHub Pages** - hiyamax-blog仓库

### 5.2 部署流程

#### 步骤1: 准备资源文件
```bash
# 复制视频到assets目录
cp final_video.mp4 hiyamax-blog-repo/assets/the_147th_day/

# 复制角色图
cp character.jpg hiyamax-blog-repo/assets/the_147th_day/
```

#### 步骤2: 更新Pipeline数据
编辑 `hiyamax-blog-repo/pipeline/data/the_147th_day.json`:
- 添加clips信息
- 更新discussions记录
- 更新版本信息

#### 步骤3: Git提交
```bash
cd hiyamax-blog-repo
git add -A
git commit -m "Add shortfilm XXX: description"
git push origin main
```

#### 步骤4: 验证部署
访问: `https://hiyascott.github.io/hiyamax-blog/pipeline.html`

### 5.3 Pipeline数据结构

```json
{
  "project": "the_147th_day",
  "currentVersion": "v4",
  "versions": [{
    "version": "v4",
    "status": "当前版本",
    "clips": [{
      "id": "shot01",
      "title": "镜头01-开场",
      "filename": "hailuo_shot01_v5_10s.mp4",
      "src": "./assets/the_147th_day/hailuo_shot01_v5_10s.mp4",
      "param": "first_frame_image"
    }]
  }],
  "discussions": [{
    "date": "2026-03-29",
    "platform": "飞书",
    "decisions": ["MiniMax-Hailuo-2.3", "10秒768P"]
  }]
}
```

### 5.4 交付物
- [ ] Pipeline页面可正常访问
- [ ] 视频可在线播放
- [ ] 所有素材已归档

---

## 费用记录模板

| 项目 | 费用 | 备注 |
|------|------|------|
| 即梦AI角色图 | ¥0（免费额度） | 每日免费额度 |
| 海螺视频生成 | ¥1.6/10秒 | 768P分辨率 |
| 可灵视频生成 | 较高 | 按次计费 |
| GitHub Pages | ¥0 | 免费托管 |

---

## 常见问题

### Q1: API调用失败怎么办？
- 检查API余额
- 检查参数格式
- 查看官方文档

### Q2: 角色不一致怎么办？
- 使用首尾帧模式
- 提供更详细的角色描述
- 考虑海螺网页端【主体参考】功能

### Q3: 字幕乱码怎么办？
- 使用Noto Serif CJK字体
- 检查字体文件路径
- 确保FFmpeg支持该字体

---

## 相关链接

- Pipeline页面: https://hiyascott.github.io/hiyamax-blog/pipeline.html
- 海螺文档: https://doc.dmxapi.cn/hailuo-img2video.html
- 可灵文档: https://doc.dmxapi.cn/kling-video-generation.html

---

*文档版本: v1.0*
*更新日期: 2026-03-29*
*维护者: Jetton*
