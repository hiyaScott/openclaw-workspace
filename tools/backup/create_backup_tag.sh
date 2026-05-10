: "# 创建今日备份标签

cd /root/.openclaw/workspace/portfolio-blog

TAG_NAME="backup-2026-03-27"
COMMIT_SHA="5e41a29eb6b7498d9d3466472ec29882b63aad40"

echo "Creating tag: $TAG_NAME -> $COMMIT_SHA"

git tag -a "$TAG_NAME" "$COMMIT_SHA" -m "[Auto] Daily Backup - 2026-03-27

虾折腾站点自动备份
- 源分支: origin/main
- Commit: ${COMMIT_SHA:0:7}
- 备份时间: 2026-03-27 23:17 CST
- 备份类型: 每日自动备份"