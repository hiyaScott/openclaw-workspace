#!/bin/bash
# deploy-check.sh - 发布前检查脚本
# 使用方法: ./deploy-check.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "  HiyaScott 发布前检查"
echo "========================================"
echo ""

PASS=0
FAIL=0
WARNING=0

# 1. HTML 文件存在性检查
echo "[1/6] 检查关键 HTML 文件..."
if [ -f "index.html" ]; then
  echo "  ✅ index.html"
  PASS=$((PASS + 1))
else
  echo "  ❌ index.html 缺失"
  FAIL=$((FAIL + 1))
fi

if [ -f "games/index.html" ]; then
  echo "  ✅ games/index.html"
  PASS=$((PASS + 1))
else
  echo "  ❌ games/index.html 缺失"
  FAIL=$((FAIL + 1))
fi

if [ -f "kimi-claw/index.html" ]; then
  echo "  ✅ kimi-claw/index.html"
  PASS=$((PASS + 1))
else
  echo "  ❌ kimi-claw/index.html 缺失"
  FAIL=$((FAIL + 1))
fi

if [ -f "research/index.html" ]; then
  echo "  ✅ research/index.html"
  PASS=$((PASS + 1))
else
  echo "  ❌ research/index.html 缺失"
  FAIL=$((FAIL + 1))
fi
echo ""

# 2. 链接检查
echo "[2/6] 检查主页关键链接..."
if [ -d "games" ]; then
  echo "  ✅ ./games/"
  PASS=$((PASS + 1))
else
  echo "  ❌ ./games/ 不存在"
  FAIL=$((FAIL + 1))
fi

if [ -d "kimi-claw" ]; then
  echo "  ✅ ./kimi-claw/"
  PASS=$((PASS + 1))
else
  echo "  ❌ ./kimi-claw/ 不存在"
  FAIL=$((FAIL + 1))
fi

if [ -d "research" ]; then
  echo "  ✅ ./research/"
  PASS=$((PASS + 1))
else
  echo "  ❌ ./research/ 不存在"
  FAIL=$((FAIL + 1))
fi

if [ -f "status-monitor/cognitive-status.html" ]; then
  echo "  ✅ ./status-monitor/cognitive-status.html"
  PASS=$((PASS + 1))
else
  echo "  ❌ ./status-monitor/cognitive-status.html 不存在"
  FAIL=$((FAIL + 1))
fi
echo ""

# 3. HTTP 链接检查
echo "[3/6] 检查 HTTP 链接（应使用 HTTPS）..."
HTTP_COUNT=$(grep -r 'href="http://' --include="*.html" . 2>/dev/null | grep -vc 'https://' || echo "0")
if [ "$HTTP_COUNT" = "0" ]; then
  echo "  ✅ 未发现 HTTP 链接"
  PASS=$((PASS + 1))
else
  echo "  ⚠️ 发现 $HTTP_COUNT 个 HTTP 链接:"
  grep -r 'href="http://' --include="*.html" . 2>/dev/null | grep -v 'https://' | head -3
  WARNING=$((WARNING + 1))
fi
echo ""

# 4. Sitemap 检查
echo "[4/6] 检查 sitemap.xml..."
if [ -f "sitemap.xml" ]; then
  URL_COUNT=$(grep -c '<loc>' sitemap.xml || echo "0")
  echo "  ✅ sitemap.xml 存在，包含 $URL_COUNT 个 URL"
  PASS=$((PASS + 1))
  
  # 检查是否包含技能页面
  if grep -q 'deploy-sentinel' sitemap.xml; then
    echo "  ✅ sitemap 包含最新技能页面"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️ sitemap 可能缺少最新技能页面"
    WARNING=$((WARNING + 1))
  fi
else
  echo "  ❌ sitemap.xml 缺失"
  FAIL=$((FAIL + 1))
fi
echo ""

# 5. Git 状态检查
echo "[5/6] 检查 Git 状态..."
if [ -d ".git" ]; then
  UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
  MODIFIED=$(git diff --name-only | wc -l)
  
  if [ "$UNTRACKED" = "0" ] && [ "$MODIFIED" = "0" ]; then
    echo "  ✅ 工作区干净"
    PASS=$((PASS + 1))
  else
    echo "  ⚠️ 有未提交的更改:"
    if [ "$UNTRACKED" != "0" ]; then
      echo "     - $UNTRACKED 个未跟踪文件"
    fi
    if [ "$MODIFIED" != "0" ]; then
      echo "     - $MODIFIED 个修改未提交"
    fi
    WARNING=$((WARNING + 1))
  fi
else
  echo "  ❌ 不是 Git 仓库"
  FAIL=$((FAIL + 1))
fi
echo ""

# 6. .gitignore 检查
echo "[6/6] 检查 .gitignore..."
if [ -f ".gitignore" ]; then
  echo "  ✅ .gitignore 存在"
  PASS=$((PASS + 1))
else
  echo "  ⚠️ .gitignore 缺失，建议添加"
  WARNING=$((WARNING + 1))
fi
echo ""

# 总结
echo "========================================"
echo "  检查结果"
echo "========================================"
echo -e "  ${GREEN}✅ 通过: $PASS${NC}"
echo -e "  ${YELLOW}⚠️  警告: $WARNING${NC}"
echo -e "  ${RED}❌ 失败: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  if [ $WARNING -eq 0 ]; then
    echo -e "${GREEN}🎉 所有检查通过，可以安全发布！${NC}"
    exit 0
  else
    echo -e "${YELLOW}⚠️  检查通过，但存在警告，建议处理后再发布${NC}"
    exit 0
  fi
else
  echo -e "${RED}❌ 检查未通过，请修复问题后再发布${NC}"
  exit 1
fi
