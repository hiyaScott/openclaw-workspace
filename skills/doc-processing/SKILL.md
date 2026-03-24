---
name: doc-processing
description: 批量文档处理与格式转换，涵盖Pandoc文档转换、Markdown处理、模板生成、多语言翻译、自动化文档工作流。实现从格式转换到模板渲染的完整文档工程。
---

# 批量文档处理

## 概述

批量文档处理是自动化转换、生成和管理大量文档的能力，涵盖格式转换、模板渲染、内容提取和批量操作，是文档工程化的核心组件。

## 核心能力

### 1. Pandoc 格式转换

**万能文档转换器**：
```bash
# Markdown → PDF
pandoc input.md -o output.pdf --pdf-engine=xelatex

# Markdown → Word
pandoc input.md -o output.docx --reference-doc=template.docx

# Markdown → HTML
pandoc input.md -o output.html --standalone --css=style.css

# Word → Markdown
pandoc input.docx -o output.md --wrap=none

# 批量转换
for file in *.md; do
    pandoc "$file" -o "output/${file%.md}.pdf"
done
```

**中文文档处理**：
```bash
pandoc chinese.md -o chinese.pdf \
    --pdf-engine=xelatex \
    -V mainfont="Source Han Serif SC" \
    -V geometry:margin=2.5cm \
    --toc \
    --number-sections
```

### 2. 模板系统

**Jinja2模板引擎**（Python）：
```python
from jinja2 import Environment, FileSystemLoader
import json

# 加载模板
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('report.html')

# 渲染数据
data = {
    'title': '项目报告',
    'author': '张三',
    'date': '2024-01-15',
    'sections': [
        {'heading': '概述', 'content': '项目背景说明...'},
        {'heading': '分析', 'content': '数据分析结果...'}
    ]
}

output = template.render(**data)
with open('report.html', 'w', encoding='utf-8') as f:
    f.write(output)
```

**模板示例**（report.html）：
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: "Microsoft YaHei", sans-serif; }
        h1 { color: #333; border-bottom: 2px solid #0066cc; }
        .meta { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="meta">
        <p>作者: {{ author }} | 日期: {{ date }}</p>
    </div>
    
    {% for section in sections %}
    <section>
        <h2>{{ section.heading }}</h2>
        <p>{{ section.content }}</p>
    </section>
    {% endfor %}
</body>
</html>
```

### 3. 批量处理脚本

**Python自动化**：
```python
import os
from pathlib import Path
import subprocess

def batch_convert(input_dir, output_dir, from_fmt='md', to_fmt='pdf'):
    """批量转换文档格式"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for file in input_path.glob(f'*.{from_fmt}'):
        output_file = output_path / f"{file.stem}.{to_fmt}"
        
        cmd = [
            'pandoc',
            str(file),
            '-o', str(output_file),
            '--pdf-engine=xelatex'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✓ Converted: {file.name} → {output_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed: {file.name} - {e}")

def merge_docs(file_list, output_file):
    """合并多个文档"""
    cmd = ['pandoc'] + file_list + ['-o', output_file, '--toc']
    subprocess.run(cmd, check=True)
```

**Makefile工作流**：
```makefile
# 批量文档转换Makefile

SOURCES := $(wildcard docs/*.md)
TARGETS := $(patsubst docs/%.md,output/%.pdf,$(SOURCES))

.PHONY: all clean

all: $(TARGETS)

output/%.pdf: docs/%.md templates/default.latex
	@mkdir -p output
	pandoc $< -o $@ --template=templates/default.latex --toc

clean:
	rm -rf output/

# 并行处理（使用 make -j4）
MAKEFLAGS += -j$(shell nproc)
```

### 4. 元数据处理

**YAML Front Matter**：
```markdown
---
title: "技术白皮书"
author: "研发团队"
date: 2024-03-15
categories: ["技术", "架构"]
tags: ["微服务", "云原生"]
version: "2.0"
---

# 正文内容
...
```

**元数据提取**（Python）：
```python
import yaml
import re

def extract_front_matter(file_path):
    """提取Markdown文件的YAML front matter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        metadata = yaml.safe_load(match.group(1))
        body = content[match.end():]
        return metadata, body
    
    return {}, content
```

### 5. 文档翻译工作流

**自动化翻译处理**：
```python
def process_translation(source_file, target_lang='en'):
    """文档翻译处理流程"""
    # 1. 提取原文
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 2. 分段翻译（调用翻译API）
    segments = split_into_segments(content)
    translated = [translate(s, target_lang) for s in segments]
    
    # 3. 合并输出
    output_file = f"{source_file}.{target_lang}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated))
    
    return output_file
```

## 支持的格式

| 输入格式 | 输出格式 | 说明 |
|----------|----------|------|
| Markdown | PDF, DOCX, HTML, EPUB | 通用文档 |
| Word | Markdown, PDF, HTML | Office文档 |
| LaTeX | PDF, DOCX | 学术论文 |
| HTML | Markdown, PDF | Web内容 |
| reStructuredText | 多种格式 | Python文档 |
| Jupyter | HTML, PDF, Markdown | 笔记本 |

## 最佳实践

1. **模板标准化** - 建立统一的文档模板
2. **版本控制** - 将文档纳入Git管理
3. **自动化CI** - 提交自动转换
4. **质量检查** - 链接检查、格式验证
5. **元数据管理** - 统一的文档属性

## 参考资源

- [Pandoc Documentation](https://pandoc.org/manual.html)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
