#!/bin/bash
# 游戏测试脚本 - 自动测试所有游戏第一关

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🎮 虾折腾游戏测试系统 v1.0                               ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

GAMES=(
  "gravity-flip:重力反转跑酷"
  "memory-maze:记忆迷宫"
  "chroma-blaster:颜色匹配射击"
  "chain-reaction:链式反应"
  "time-rewind:时间回溯"
  "bot-coder:编程机器人"
  "neon-defense:资源塔防"
  "shadow-puzzle:光影谜题"
  "card-alchemist:卡牌合成"
  "quantum-split:量子分裂"
  "magnetic-snap:磁力吸附"
  "wave-warrior:波形战士"
  "mirror-maze:镜像迷宫"
  "thermal-expansion:热胀冷缩"
  "circuit-connect:电路连接"
  "sonic-maze:声波迷宫"
  "pixel-painter:像素画"
  "rhythm-parkour:节奏跑酷"
  "gravity-slingshot:引力弹弓"
  "six-finger-midi:六指迷笛"
)

PASS=0
FAIL=0

echo "📋 测试清单（手动测试指南）："
echo ""
echo "对每个游戏，请检查以下项目："
echo "  1️⃣  游戏能否正常加载"
echo "  2️⃣  第一关能否正常开始"
echo "  3️⃣  控制是否响应（键盘/鼠标）"
echo "  4️⃣  游戏逻辑是否正常"
echo "  5️⃣  能否完成第一关"
echo "  6️⃣  音频是否正常"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for game in "${GAMES[@]}"; do
  IFS=':' read -r folder name <<< "$game"
  url="https://hiyascott.github.io/scott-portfolio/$folder/"
  
  echo "🎮 $name"
  echo "   链接: $url"
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 测试记录模板："
echo ""
echo "游戏名称: [填写]"
echo "测试日期: [填写]"
echo "浏览器: [填写]"
echo ""
echo "测试结果:"
echo "  [ ] 能正常加载"
echo "  [ ] 第一关正常"
echo "  [ ] 控制响应"
echo "  [ ] 逻辑正常"
echo "  [ ] 能完成第一关"
echo "  [ ] 音频正常"
echo ""
echo "发现问题:"
echo "  [填写具体问题]"
echo ""
echo "严重程度: [ ]轻微 [ ]中等 [ ]严重"
echo ""
