#!/bin/bash
# The 147th Day - 完整后期剪辑脚本（含音乐）
set -e

INPUT_DIR="/root/.openclaw/workspace/hiyamax-blog-repo/assets/the_147th_day"
OUTPUT_DIR="$INPUT_DIR"
FINAL_OUTPUT="$OUTPUT_DIR/the_147th_day_mvp_final.mp4"

echo "=========================================="
echo "🎬 THE 147TH DAY - MVP后期剪辑"
echo "=========================================="

# 检查依赖
if ! which ffmpeg >/dev/null 2>&1; then
    echo "❌ FFmpeg 未安装，无法继续"
    exit 1
fi
echo "✅ FFmpeg 已就绪"

# 检查素材
SHOT01="$INPUT_DIR/shot01_opening.mp4"
SHOT08="$INPUT_DIR/shot08_midpoint.mp4"  
SHOT16="$INPUT_DIR/shot16_ending.mp4"

echo ""
echo "📁 素材检查:"
for shot in "$SHOT01" "$SHOT08" "$SHOT16"; do
    [ -f "$shot" ] && echo "  ✅ $(basename $shot)" || echo "  ⚠️  $(basename $shot) 不存在"
done

# 准备音乐
echo ""
echo "🎵 准备背景音乐..."

# 方式1: 检查是否有外部提供的音乐
if [ -f "$INPUT_DIR/background_music.mp3" ]; then
    MUSIC_FILE="$INPUT_DIR/background_music.mp3"
    echo "  ✅ 使用提供的背景音乐"
# 方式2: 使用SoX生成简单钢琴音
elif which sox >/dev/null 2>&1; then
    echo "  🎹 生成简单背景音乐..."
    MUSIC_FILE="$INPUT_DIR/generated_music.mp3"
    
    # 生成30秒的简单环境音
    sox -n "$MUSIC_FILE" synth 30 sine 440 fade 0 30 3 2>&1 || \
    ffmpeg -f lavfi -i "sine=frequency=440:duration=30" -af "afade=t=in:ss=0:d=2,afade=t=out:st=28:d=2" "$MUSIC_FILE" -y 2>/dev/null
    
    echo "  ✅ 已生成环境音背景"
else
    echo "  ⚠️ 无背景音乐可用，将输出无声版本"
    MUSIC_FILE=""
fi

# 合并视频
echo ""
echo "✂️ 合并3个镜头..."
CONCAT_LIST=$(mktemp)
for shot in "$SHOT01" "$SHOT08" "$SHOT16"; do
    [ -f "$shot" ] && echo "file '$shot'" >> "$CONCAT_LIST"
done

ffmpeg -y -f concat -safe 0 -i "$CONCAT_LIST" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 128k \
    -pix_fmt yuv420p \
    "${FINAL_OUTPUT}.tmp.mp4"

rm "$CONCAT_LIST"

# 添加字幕
echo ""
echo "📝 添加字幕..."
SUBTITLE_TEXT="第147天。花还活着。"

ffmpeg -y -i "${FINAL_OUTPUT}.tmp.mp4" \
    -vf "drawtext=text='$SUBTITLE_TEXT':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.5:boxborderw=10:enable='between(t,5,25)'" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a copy \
    "${FINAL_OUTPUT}.tmp2.mp4"

rm "${FINAL_OUTPUT}.tmp.mp4"

# 添加音乐（如果有）
if [ -n "$MUSIC_FILE" ] && [ -f "$MUSIC_FILE" ]; then
    echo ""
    echo "🎵 添加背景音乐..."
    
    ffmpeg -y -i "${FINAL_OUTPUT}.tmp2.mp4" -i "$MUSIC_FILE" \
        -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]" \
        -map 0:v -map "[a]" \
        -c:v copy -c:a aac -b:a 192k \
        "$FINAL_OUTPUT"
    
    # 清理生成的音乐
    [ "$MUSIC_FILE" = "$INPUT_DIR/generated_music.mp3" ] && rm -f "$MUSIC_FILE"
else
    mv "${FINAL_OUTPUT}.tmp2.mp4" "$FINAL_OUTPUT"
fi

rm -f "${FINAL_OUTPUT}.tmp2.mp4"

# 完成
echo ""
echo "=========================================="
echo "✅ 剪辑完成！"
echo "=========================================="
echo ""
echo "📁 输出: $FINAL_OUTPUT"
ls -lh "$FINAL_OUTPUT" | awk '{print "📊 大小: " $5}'
ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL_OUTPUT" | awk '{print "⏱️  时长: " int($1) "秒"}'
echo ""
echo "🎬 结构: 开场(10s) + 中点(10s) + 结局(10s)"
echo "💬 字幕: $SUBTITLE_TEXT"
[ -n "$MUSIC_FILE" ] && echo "🎵 音乐: 已添加" || echo "🔇 音乐: 无"
