---
name: github-automation
description: GitHub自动化与CI/CD管理，涵盖Release发布、PR审查、工作流监控、Issue自动化、仓库管理。使用GitHub Actions、CLI和API实现开发流程全面自动化。
---

# GitHub 自动化

## 概述

GitHub自动化通过Actions、CLI和API实现开发工作流的全面自动化，从代码提交到生产部署的完整DevOps流程管理。

## 核心能力

### 1. GitHub Actions CI/CD

**工作流基础结构**：
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: npm run deploy
```

**缓存优化策略**：
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      ~/.cache/pip
      ~/.gradle
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

### 2. Release 自动化

**语义化版本发布**：
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate changelog
        id: changelog
        uses: metcalfc/changelog-generator@v4
        with:
          myToken: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
```

**自动版本管理**（使用semantic-release）：
```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

### 3. PR 自动化

**自动化检查清单**：
```yaml
name: PR Checks

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run linter
        run: npm run lint
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
  
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build project
        run: npm run build
```

**自动分配审查者**：
```yaml
- name: Auto Assign Reviewers
  uses: kentaro-m/auto-assign-action@v2
  with:
    configuration-path: '.github/auto-assign.yml'
```

### 4. GitHub CLI (gh) 自动化

**常用命令**：
```bash
# 认证
ght auth login

# 创建PR
gh pr create --title "Fix bug" --body "Description" --base main

# 合并PR
gh pr merge 123 --squash --delete-branch

# 查看工作流状态
gh run list --limit 10

# 触发工作流
gh workflow run deploy.yml -f environment=production

# 创建Release
gh release create v1.0.0 --title "Version 1.0.0" --generate-notes
```

**批量操作脚本**：
```bash
#!/bin/bash
# 批量同步fork仓库

REPOS=("repo1" "repo2" "repo3")
UPSTREAM="upstream"

for repo in "${REPOS[@]}"; do
    echo "Syncing $repo..."
    cd "$repo" || continue
    
    git fetch $UPSTREAM
    git checkout main
    git merge $UPSTREAM/main
    git push origin main
    
    cd ..
done
```

### 5. Issue 自动化

**自动标签分配**：
```yaml
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            const issue = context.payload.issue;
            const title = issue.title.toLowerCase();
            
            let labels = [];
            if (title.includes('bug')) labels.push('bug');
            if (title.includes('feature')) labels.push('enhancement');
            if (title.includes('docs')) labels.push('documentation');
            
            if (labels.length > 0) {
              github.rest.issues.addLabels({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                labels: labels
              });
            }
```

## 安全最佳实践

### Secrets管理
```yaml
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    echo "Deploying with secure credentials"
```

### OIDC认证（AWS示例）
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/my-role
    aws-region: us-east-1
```

## 监控与报告

**工作流状态通知**：
```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    fields: repo,message,commit,author,action,eventName
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 参考资源

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [GitHub API Reference](https://docs.github.com/en/rest)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
