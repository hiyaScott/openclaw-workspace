---
name: docs-engineering
description: 技术文档工程化实践，涵盖Docs-as-Code理念、API文档设计、知识库构建、文档自动化与版本控制。使用Markdown、OpenAPI、Docusaurus等工具构建专业文档体系。
---

# 文档工程

## 概述

文档工程（Docs Engineering）是将软件工程最佳实践应用于技术文档创建的学科。它强调Docs-as-Code理念，将文档纳入版本控制、CI/CD流程和质量保障体系。

## 核心能力

### 1. Docs-as-Code 理念

**核心原则**：
- 文档与代码同等重要
- 使用版本控制管理文档
- 通过CI/CD自动构建部署
- Code Review检查文档质量

**工具链**：

| 类型 | 工具 |
|------|------|
| 编写 | Markdown、AsciiDoc |
| 版本控制 | Git |
| 构建 | MkDocs、Docusaurus、VuePress |
| 部署 | GitHub Pages、Vercel、Netlify |

### 2. 文档类型与结构

**Diátaxis框架分类**：

| 类型 | 目的 | 示例 |
|------|------|------|
| **Tutorials** | 学习导向 | 入门教程 |
| **How-to Guides** | 任务导向 | 操作指南 |
| **Reference** | 信息导向 | API文档 |
| **Explanation** | 理解导向 | 概念说明 |

**标准文档结构**：
```
docs/
├── README.md           # 项目概览
├── getting-started/    # 入门指南
├── tutorials/          # 教程
├── how-to/            # 操作指南
├── reference/         # 参考文档
├── explanation/       # 概念解释
└── api/               # API文档
```

### 3. API文档工程

**OpenAPI规范**：
```yaml
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
paths:
  /users:
    get:
      summary: 获取用户列表
      responses:
        200:
          description: 成功
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

**工具集成**：
- **Swagger UI** - 交互式API文档
- **Redoc** - 美观的API参考
- **Postman** - API测试与文档

### 4. 文档质量保障

**代码示例验证**：
- 所有代码片段必须可执行
- 使用CI自动测试代码
- 版本与代码同步更新

**质量标准**：
- 准确性：技术信息正确
- 完整性：覆盖所有功能
- 一致性：术语和风格统一
- 可访问性：支持多设备阅读

### 5. 自动化工作流

**CI/CD集成示例**（GitHub Actions）：
```yaml
name: Documentation
on:
  push:
    paths:
      - 'docs/**'
      
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: pip install mkdocs-material
      - name: Build docs
        run: mkdocs build
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

## 工具矩阵

| 工具 | 用途 | 推荐场景 |
|------|------|----------|
| **MkDocs** | 静态站点生成 | 简单项目文档 |
| **Docusaurus** | 完整文档站点 | 开源项目、产品文档 |
| **VuePress** | Vue生态文档 | Vue相关项目 |
| **Sphinx** | Python项目 | Python库文档 |
| **Read the Docs** | 托管平台 | 开源项目托管 |

## 最佳实践

### 编写原则
1. **目标读者明确** - 了解你的读者是谁
2. **渐进式披露** - 从简单到复杂
3. **Show, Don't Tell** - 用示例说明
4. **保持更新** - 与代码同步

### 协作规范
1. 使用Pull Request审核文档变更
2. 定义术语表保持用词一致
3. 定期审查和清理过时内容
4. 建立文档贡献指南

## 参考资源

- [Docs-as-Code - Anne Gentle](https://www.docslikecode.com/)
- [Google Technical Writing Course](https://developers.google.com/tech-writing)
- [Write the Docs Community](https://www.writethedocs.org/)
- [Diátaxis Documentation Framework](https://diataxis.fr/)
