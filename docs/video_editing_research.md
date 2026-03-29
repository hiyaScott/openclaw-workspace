# 后期剪辑工具链研究报告

## 工具清单

### 1. FFmpeg (核心)
- **用途**: 视频剪辑、合并、转码、加字幕、调色
- **状态**: 正在安装
- **功能**:
  - 剪辑视频片段: `-ss 00:00:00 -t 10`
  - 合并多个视频: `concat`
  - 添加字幕: `subtitles` filter
  - 调整分辨率/码率
  - 添加音轨

### 2. SoX (音频处理)
- **用途**: 音频剪辑、混音、格式转换
- **功能**:
  - 生成简单音效
  - 音频淡入淡出
  - 混音合并

### 3. ImageMagick (图像)
- **用途**: 图片处理、字幕生成
- **功能**:
  - 文字转图片字幕
  - 图像合成

---

## MVP后期剪辑流程

### 阶段1: 素材准备
```bash
# 1. 统一视频格式和分辨率
ffmpeg -i input1.mp4 -vf "scale=1920:1080" -c:v libx264 -crf 23 shot01.mp4

# 2. 如果视频太长，截取前10秒
ffmpeg -i input.mp4 -ss 00:00:00 -t 10 -c copy shot01_10s.mp4
```

### 阶段2: 粗剪拼接
```bash
# 创建文件列表
echo "file 'shot01.mp4'" > list.txt
echo "file 'shot08.mp4'" >> list.txt
echo "file 'shot16.mp4'" >> list.txt

# 合并 (需要相同编码)
ffmpeg -f concat -safe 0 -i list.txt -c copy rough_cut.mp4
```

### 阶段3: 添加字幕
```bash
# 方式1: 硬字幕 (嵌入视频)
ffmpeg -i rough_cut.mp4 -vf "subtitles=subtitles.srt" final.mp4

# 方式2: 直接文字叠加
ffmpeg -i rough_cut.mp4 -vf "drawtext=text='第147天。花还活着。':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100" final.mp4
```

### 阶段4: 添加音乐
```bash
# 合并视频和音频
ffmpeg -i final.mp4 -i music.mp3 -c:v copy -c:a aac -shortest final_with_music.mp4
```

---

## 具体MVP方案

### 输入素材
- shot01_opening.mp4 (10秒)
- shot08_midpoint.mp4 (10秒)
- shot16_ending.mp4 (10秒)

### 输出
- the_147th_day_mvp.mp4 (30秒)

### 步骤
1. 检查并统一3个素材的分辨率和编码
2. 按顺序合并
3. 添加字幕: "第147天。花还活着。"
4. 添加简单背景音乐 (可用Suno生成或免费音乐)
5. 输出最终文件

---

## 脚本文件

见 `tools/edit_147th_day.sh`
