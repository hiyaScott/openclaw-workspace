---
name: media-processing
description: 图像音频处理与多媒体操作，涵盖Python Pillow图像处理、FFmpeg音视频转换、OCR文字识别、格式转换与优化。游戏资源优化与批量媒体处理。
---

# 图像音频处理

## 概述

多媒体处理涉及图像、音频、视频的转换、优化和分析。本技能涵盖从基础格式转换到高级处理技术的完整多媒体工程能力。

## 核心能力

### 1. 图像处理 (Pillow)

**基础操作**：
```python
from PIL import Image, ImageFilter, ImageEnhance
import os

# 打开图像
img = Image.open('input.jpg')

# 基础变换
img_resized = img.resize((800, 600))                    # 调整尺寸
img_cropped = img.crop((100, 100, 400, 400))           # 裁剪
img_rotated = img.rotate(45, expand=True)              # 旋转

# 格式转换
img.save('output.png')
img.save('output.webp', quality=85, method=6)          # WebP优化

# 滤镜效果
img_blur = img.filter(ImageFilter.GaussianBlur(5))
img_sharp = img.filter(ImageFilter.SHARPEN)
img_edges = img.filter(ImageFilter.FIND_EDGES)
```

**批量处理**：
```python
def batch_process_images(input_dir, output_dir, operations):
    """批量处理图像"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(input_dir, filename)
            img = Image.open(filepath)
            
            for op in operations:
                if op['type'] == 'resize':
                    img = img.resize(op['size'], Image.Resampling.LANCZOS)
                elif op['type'] == 'compress':
                    img = img.convert('RGB')
            
            output_path = os.path.join(output_dir, filename)
            img.save(output_path, optimize=True, quality=85)
            print(f"Processed: {filename}")
```

**图像优化**：
```python
def optimize_image(input_path, output_path, max_size=(1920, 1080), quality=85):
    """优化图像用于Web"""
    img = Image.open(input_path)
    
    # 保持比例调整尺寸
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # 转换为RGB（去除透明通道）
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    
    # 保存优化
    img.save(output_path, 'JPEG', optimize=True, quality=quality)
    
    # 计算压缩率
    original_size = os.path.getsize(input_path)
    optimized_size = os.path.getsize(output_path)
    ratio = (1 - optimized_size / original_size) * 100
    
    print(f"Original: {original_size/1024:.1f}KB")
    print(f"Optimized: {optimized_size/1024:.1f}KB")
    print(f"Saved: {ratio:.1f}%")
```

### 2. 音频处理 (pydub + FFmpeg)

**基础音频操作**：
```python
from pydub import AudioSegment
import os

# 加载音频
audio = AudioSegment.from_file("input.mp3")

# 基本编辑
audio_clipped = audio[10000:30000]           # 截取10-30秒
audio_faded = audio.fade_in(2000).fade_out(2000)  # 淡入淡出
audio_normalized = audio.normalize()         # 音量标准化
audio_reversed = audio.reverse()             # 倒放
audio_slower = audio._spawn(audio.raw_data, overrides={'frame_rate': int(audio.frame_rate * 0.8)})
audio_slower = audio_slower.set_frame_rate(audio.frame_rate)

# 格式转换
audio.export("output.wav", format="wav")
audio.export("output.ogg", format="ogg", bitrate="192k")

# 合并音频
combined = audio1 + audio2 + audio3
combined.export("combined.mp3", format="mp3")
```

**批量音频处理**：
```python
def batch_convert_audio(input_dir, output_format='mp3', bitrate='192k'):
    """批量转换音频格式"""
    for filename in os.listdir(input_dir):
        if filename.endswith(('.wav', '.ogg', '.flac', '.m4a')):
            filepath = os.path.join(input_dir, filename)
            audio = AudioSegment.from_file(filepath)
            
            output_filename = os.path.splitext(filename)[0] + f'.{output_format}'
            output_path = os.path.join(input_dir, output_filename)
            
            audio.export(output_path, format=output_format, bitrate=bitrate)
            print(f"Converted: {filename} → {output_filename}")
```

### 3. 视频处理 (FFmpeg)

**FFmpeg命令行操作**：
```bash
# 视频格式转换
ffmpeg -i input.avi output.mp4

# 压缩视频
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -strict -2 output.mp4

# 提取音频
ffmpeg -i video.mp4 -vn -acodec copy audio.aac

# 视频截图
ffmpeg -i video.mp4 -ss 00:01:30 -vframes 1 screenshot.jpg

# 裁剪视频
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:00:30 -c copy output.mp4

# 调整分辨率
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4

# 批量转换
for file in *.avi; do
    ffmpeg -i "$file" "${file%.avi}.mp4"
done
```

**Python调用FFmpeg**：
```python
import subprocess

def compress_video(input_file, output_file, crf=23):
    """压缩视频文件"""
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx264',
        '-crf', str(crf),      # 质量（18-28，越小越好）
        '-preset', 'medium',   # 压缩速度
        '-acodec', 'aac',
        '-b:a', '128k',
        '-movflags', '+faststart',  # Web优化
        '-y', output_file
    ]
    
    subprocess.run(cmd, check=True)
```

### 4. OCR文字识别

**使用EasyOCR/pytesseract**：
```python
import easyocr
import cv2

# 初始化识别器
reader = easyocr.Reader(['ch_sim', 'en'])

# 读取图像
def extract_text(image_path):
    results = reader.readtext(image_path)
    
    texts = []
    for (bbox, text, prob) in results:
        if prob > 0.5:  # 置信度过滤
            texts.append({
                'text': text,
                'confidence': prob,
                'bbox': bbox
            })
    
    return texts

# 批量OCR
def batch_ocr(input_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for filename in sorted(os.listdir(input_dir)):
            if filename.endswith(('.jpg', '.png')):
                filepath = os.path.join(input_dir, filename)
                texts = extract_text(filepath)
                
                f.write(f"\n=== {filename} ===\n")
                for item in texts:
                    f.write(f"{item['text']}\n")
```

### 5. 游戏资源优化

**纹理优化**：
```python
def optimize_game_assets(asset_dir):
    """优化游戏资源"""
    for root, dirs, files in os.walk(asset_dir):
        for file in files:
            filepath = os.path.join(root, file)
            
            # 压缩纹理
            if file.endswith(('.png', '.jpg')):
                img = Image.open(filepath)
                
                # 确保2的幂次方尺寸（游戏引擎优化）
                w, h = img.size
                new_w = 2 ** (w - 1).bit_length()
                new_h = 2 ** (h - 1).bit_length()
                
                if (w, h) != (new_w, new_h):
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True)
                    print(f"Resized: {file} ({w}x{h} → {new_w}x{new_h})")
            
            # 压缩音频
            elif file.endswith('.wav'):
                audio = AudioSegment.from_wav(filepath)
                output_path = filepath.replace('.wav', '.ogg')
                audio.export(output_path, format='ogg', bitrate='128k')
                os.remove(filepath)
                print(f"Compressed: {file} → {os.path.basename(output_path)}")
```

## 格式支持

| 类型 | 格式 | 处理工具 |
|------|------|----------|
| **图像** | JPG, PNG, WebP, GIF, BMP | Pillow |
| **音频** | MP3, WAV, OGG, FLAC, AAC | pydub, FFmpeg |
| **视频** | MP4, AVI, MKV, MOV, WebM | FFmpeg |
| **文档** | PDF | pypdf2, pdf2image |

## 最佳实践

1. **批量处理** - 使用脚本自动化重复任务
2. **质量平衡** - 文件大小与质量的权衡
3. **格式选择** - WebP(图)、OGG(音)、MP4(H.264)(视频)
4. **元数据保留** - 注意保留重要的EXIF信息
5. **错误处理** - 批量处理时捕获异常

## 参考资源

- [Pillow Documentation](https://pillow.readthedocs.io/)
- [pydub Documentation](https://github.com/jiaaro/pydub)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
