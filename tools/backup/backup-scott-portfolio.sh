#!/bin/bash
# Backup script for scott-portfolio before Jekyll migration

BACKUP_DIR="/root/.openclaw/workspace/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPO_DIR="/root/.openclaw/workspace/portfolio-blog"

echo "Creating backup of scott-portfolio..."
echo "Timestamp: $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create git archive
cd "$REPO_DIR"
git archive --format=tar.gz -o "$BACKUP_DIR/scott-portfolio-pre-jekyll-$TIMESTAMP.tar.gz" HEAD

# Create tag
git tag -a "pre-jekyll-$TIMESTAMP" -m "Backup before Jekyll migration"

echo "Backup created:"
echo "  Archive: $BACKUP_DIR/scott-portfolio-pre-jekyll-$TIMESTAMP.tar.gz"
echo "  Git tag: pre-jekyll-$TIMESTAMP"
echo ""
echo "To restore:"
echo "  tar -xzf $BACKUP_DIR/scott-portfolio-pre-jekyll-$TIMESTAMP.tar.gz -C /target/path"
echo "  OR"
echo "  git checkout pre-jekyll-$TIMESTAMP"