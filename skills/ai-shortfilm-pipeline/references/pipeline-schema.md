# Pipeline JSON数据结构规范

## 根对象

```json
{
  "project": "项目名称",
  "emoji": "项目emoji",
  "status": "进行中|已完成|已发布",
  "cover": {
    "image": "封面图文件名",
    "thumbnail": "封面缩略图文件名"
  },
  "steps": [Step对象数组]
}
```

## Step对象

```json
{
  "number": 1,
  "title": "步骤标题",
  "description": "步骤描述",
  "content": {
    "versions": [Version对象数组]
  }
}
```

## Version对象

```json
{
  "version": "v1",
  "status": "当前版本|已归档",
  "updated": "2026-03-30",
  "data": {
    // 具体内容根据Step类型变化
  }
}
```

## 各Step数据结构

### Step 1: 创意概念

```json
{
  "concept": {
    "hook": "一句话钩子",
    "theme": "主题",
    "logline": "一句话故事",
    "duration": "目标时长"
  },
  "structure": {
    "acts": [
      {"act": 1, "title": "第一幕", "content": "...", "duration": "0-30s"},
      {"act": 2, "title": "第二幕", "content": "...", "duration": "30-90s"},
      {"act": 3, "title": "第三幕", "content": "...", "duration": "90-120s"}
    ]
  }
}
```

### Step 2: 角色设计

```json
{
  "referenceImages": [
    {
      "title": "参考图标题",
      "src": "/path/to/image.jpg",
      "thumbnail": "image_thumb.jpg",
      "desc": "描述"
    }
  ],
  "threeViews": {
    "front": {
      "image": "xxx_front.png",
      "thumbnail": "xxx_front_thumb.jpg",
      "desc": "正视图描述"
    },
    "side": {
      "image": "xxx_side.png",
      "thumbnail": "xxx_side_thumb.jpg",
      "desc": "侧视图描述"
    },
    "back": {
      "image": "xxx_back.png",
      "thumbnail": "xxx_back_thumb.jpg",
      "desc": "背视图描述"
    }
  },
  "bestPractice": {
    "title": "最佳实践",
    "points": ["要点1", "要点2"]
  }
}
```

### Step 3: 场景设计

```json
{
  "scenes": [
    {
      "title": "场景名称",
      "desc": "场景描述",
      "image": "scene_xxx.png",
      "thumbnail": "scene_xxx_thumb.jpg",
      "shot": "镜头01",
      "mood": "氛围描述",
      "lighting": "光线描述"
    }
  ]
}
```

### Step 4: 分镜首帧

```json
{
  "shots": [
    {
      "number": 1,
      "title": "镜头标题",
      "desc": "镜头描述",
      "time": "0-6s",
      "status": "首帧V2已生成",
      "firstFrame": {
        "image": "shot_xxx.jpg",
        "thumbnail": "shot_xxx_thumb.jpg",
        "src": "/path/to/image.jpg"
      }
    }
  ]
}
```

### Step 5: 视频生成

```json
{
  "clips": [
    {
      "title": "视频标题",
      "desc": "视频描述",
      "src": "./assets/videos/xxx.mp4",
      "filename": "xxx.mp4",
      "duration": "6s",
      "tool": "海螺AI",
      "prompt": "生成提示词"
    }
  ],
  "discussion": {
    "title": "讨论记录",
    "records": [
      {"date": "2026-03-30", "content": "讨论内容"}
    ]
  }
}
```

### Step 6: 后期剪辑

```json
{
  "finalVideo": {
    "src": "./assets/videos/final.mp4",
    "duration": "17s",
    "resolution": "1920x1080"
  },
  "subtitles": {
    "style": "字幕样式",
    "font": "Noto Serif CJK"
  },
  "music": {
    "type": "临时BGM|原创音乐",
    "src": "./assets/audio/bgm.mp3"
  }
}
```

## 文件命名规范

### 缩略图命名
```
{original_name}_thumb.jpg
```

例如：
- `scene_sunset_01.png` → `scene_sunset_01_thumb.jpg`
- `robo_front.png` → `robo_front_thumb.jpg`

### 缩略图规格
- 尺寸：400x250px（场景/首帧），300x400px（三视图）
- 格式：JPEG
- 质量：85%
- 目标大小：~15KB
