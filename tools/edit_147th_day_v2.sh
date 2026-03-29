#!/bin/bash
# The 147th Day - 完整后期剪辑脚本
# 由AI助手自动执行

set -e

INPUT_DIR="/root/.openclaw/workspace/hiyamax-blog-repo/assets/the_147th_day"
OUTPUT_DIR="$INPUT_DIR"
FINAL_OUTPUT="$OUTPUT_DIR/the_147th_day_mvp_v1.mp4"

echo "=========================================="
echo "🎬 THE 147TH DAY - MVP后期剪辑"
echo "=========================================="
echo ""

# 检查依赖
echo "🔧 检查工具..."
if ! which ffmpeg >/dev/null 2>&1; then
    echo "❌ FFmpeg 未安装"
    exit 1
fi
echo "  ✅ FFmpeg 已就绪"

# 检查素材
echo ""
echo "📁 检查素材..."
SHOT01="$INPUT_DIR/shot01_opening.mp4"
SHOT08="$INPUT_DIR/shot08_midpoint.mp4"  
SHOT16="$INPUT_DIR/shot16_ending.mp4"

for shot in "$SHOT01" "$SHOT08" "$SHOT16"; do
    if [ -f "$shot" ]; then
        duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$shot" 2>/dev/null | cut -d. -f1)
        echo "  ✅ $(basename $shot) (${duration}s)"
    else
        echo "  ⚠️  $(basename $shot) 不存在"
    fi
done

# 生成字幕图片 (更美观)
echo ""
echo "📝 生成字幕..."
SUBTITLE_TEXT="第147天。花还活着。"

# 使用ImageMagick生成带透明背景的字幕图片
convert -size 1920x200 xc:transparent \
    -gravity center \
    -pointsize 60 \
    -fill white \
    -stroke black \
    -strokewidth 2 \
    -font "Noto-Sans-CJK-Bold" \
    -annotate +0+0 "$SUBTITLE_TEXT" \
    "$OUTPUT_DIR/subtitle.png" 2>/dev/null || \
convert -size 1920x200 xc:transparent \
    -gravity center \
    -pointsize 60 \
    -fill white \
    -annotate +0+0 "$SUBTITLE_TEXT" \
    "$OUTPUT_DIR/subtitle.png"

echo "  ✅ 字幕图片已生成"

# 阶段1: 合并视频片段
echo ""
echo "✂️ 合并3个镜头..."

# 创建concat文件
CONCAT_LIST=$(mktemp)
for shot in "$SHOT01" "$SHOT08" "$SHOT16"; do
    if [ -f "$shot" ]; then
        echo "file '$shot'" >> "$CONCAT_LIST"
    fi
done

# 合并并转码
ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 128k \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "${FINAL_OUTPUT}.tmp.mp4"

rm "$CONCAT_LIST"

# 阶段2: 添加字幕
echo ""
echo "🎨 添加字幕层..."

ffmpeg -y -i "${FINAL_OUTPUT}.tmp.mp4" -i "$OUTPUT_DIR/subtitle.png" \
    -filter_complex "[0:v][1:v]overlay=0:H-h-50:enable='between(t,5,25)'[v]" \
    -map "[v]" -map 0:a \
    -c:v libx264 -preset fast -crf 23 \
    -c:a copy \
    "${FINAL_OUTPUT}.tmp2.mp4"

rm "${FINAL_OUTPUT}.tmp.mp4" "$OUTPUT_DIR/subtitle.png"

# 阶段3: 添加淡入淡出效果
echo ""
echo "✨ 添加淡入淡出..."

ffmpeg -y -i "${FINAL_OUTPUT}.tmp2.mp4" \
    -vf "fade=t=in:st=0:d=1,fade=t=out:st=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${FINAL_OUTPUT}.tmp2.mp4" | awk '{print $1-1}')":d=1" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a copy \
    "$FINAL_OUTPUT"

rm "${FINAL_OUTPUT}.tmp2.mp4"

# 输出信息
echo ""
echo "=========================================="
echo "✅ 剪辑完成！"
echo "=========================================="
echo ""
echo "📁 输出文件:"
echo "   $FINAL_OUTPUT"
echo ""
echo "📊 文件信息:"
ls -lh "$FINAL_OUTPUT" | awk '{print "   大小: " $5}'
ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL_OUTPUT" | awk '{print "   时长: " int($1) "秒"}'
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$FINAL_OUTPUT" | awk '{print "   分辨率: " $1}'

echo ""
echo "🎬 视频结构:"
echo "   [0-10s]  Shot 01 - 开场：机器人捧花"
echo "   [10-20s] Shot 08 - 中点：雨中护花"  
echo "   [20-30s] Shot 16 - 结局：倒下与绽放"
echo ""
echo "💡 如需添加背景音乐，请提供音频文件"
