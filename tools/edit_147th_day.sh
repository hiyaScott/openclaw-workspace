#!/bin/bash
# 后期剪辑脚本: The 147th Day MVP
# 将3个镜头粗剪成30秒预告片

set -e

# 配置
INPUT_DIR="/root/.openclaw/workspace/hiyamax-blog-repo/assets/the_147th_day"
OUTPUT_DIR="$INPUT_DIR"
FINAL_OUTPUT="$OUTPUT_DIR/the_147th_day_mvp.mp4"

# 素材文件
SHOT01="$INPUT_DIR/shot01_opening.mp4"
SHOT08="$INPUT_DIR/shot08_midpoint.mp4"
SHOT16="$INPUT_DIR/shot16_ending.mp4"

echo "=========================================="
echo "🎬 The 147th Day - MVP后期剪辑"
echo "=========================================="

# 检查素材
echo ""
echo "📁 检查素材..."
for file in "$SHOT01" "$SHOT08" "$SHOT16"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "  ✅ $(basename $file) ($size)"
    else
        echo "  ❌ $(basename $file) 不存在"
        exit 1
    fi
done

# 阶段1: 检查视频格式并统一
echo ""
echo "🔧 阶段1: 检查视频格式..."

# 获取第一个视频的信息
echo "  Shot 01 信息:"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration,r_frame_rate -of csv=s=x:p=0 "$SHOT01" | head -1

# 阶段2: 合并视频 (假设格式一致)
echo ""
echo "✂️ 阶段2: 合并3个镜头..."

# 创建临时文件列表
LIST_FILE=$(mktemp)
echo "file '$SHOT01'" > "$LIST_FILE"
echo "file '$SHOT08'" >> "$LIST_FILE"
echo "file '$SHOT16'" >> "$LIST_FILE"

# 合并 (重新编码以确保兼容)
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${FINAL_OUTPUT}.tmp.mp4"

rm "$LIST_FILE"

# 阶段3: 添加字幕
echo ""
echo "📝 阶段3: 添加字幕..."

SUBTITLE_TEXT="第147天。花还活着。"

ffmpeg -y -i "${FINAL_OUTPUT}.tmp.mp4" -vf \
    "drawtext=text='${SUBTITLE_TEXT}':fontcolor=white:fontsize=48:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.5:boxborderw=10" \
    -c:v libx264 -crf 23 -preset fast -c:a copy \
    "$FINAL_OUTPUT"

rm "${FINAL_OUTPUT}.tmp.mp4"

# 阶段4: 输出信息
echo ""
echo "✅ 剪辑完成!"
echo ""
echo "📁 输出文件: $FINAL_OUTPUT"
echo "📊 文件大小: $(du -h $FINAL_OUTPUT | cut -f1)"
echo "⏱️  时长: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $FINAL_OUTPUT | cut -d. -f1)秒"

echo ""
echo "=========================================="
echo "下一步: 添加背景音乐"
echo "=========================================="
echo "请提供背景音乐文件，或告诉我用Suno生成"
