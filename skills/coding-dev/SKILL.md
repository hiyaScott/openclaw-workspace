---
name: coding-dev
description: 软件开发工程师核心技能栈，涵盖Godot游戏开发、Python脚本、Web前端/后端开发、自动化工具开发。从原型到生产级应用的完整开发能力。
---

# 代码开发

## 概述

软件开发是将想法转化为可运行程序的过程，涵盖从原型到生产级应用的完整开发周期。本技能涵盖游戏开发、Web开发、脚本编程和自动化工具开发。

## 核心能力

### 1. Godot 游戏开发

**引擎架构**：
- **Scene System** - 场景树组织游戏对象
- **Node Hierarchy** - 节点继承与组合
- **GDScript** - 类Python的脚本语言
- **Signal System** - 解耦的事件通信

**核心代码模式**：
```gdscript
# 玩家控制器示例
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")

func _physics_process(delta):
    # 重力
    if not is_on_floor():
        velocity.y += gravity * delta
    
    # 跳跃
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    # 移动
    var direction = Input.get_axis("ui_left", "ui_right")
    if direction:
        velocity.x = direction * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
    
    move_and_slide()
```

### 2. Python 开发

**核心应用场景**：
- 数据处理与分析
- 自动化脚本
- Web后端（FastAPI/Django）
- AI/ML原型

**代码示例**：
```python
# FastAPI REST API
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}
```

### 3. Web 前端开发

**现代技术栈**：

| 层级 | 技术 |
|------|------|
| **框架** | React, Vue, Next.js |
| **样式** | Tailwind CSS, styled-components |
| **状态** | Zustand, Redux, React Query |
| **构建** | Vite, Webpack |

**组件开发示例**（React）：
```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  children,
  onClick 
}) => {
  const baseStyles = "px-4 py-2 rounded font-medium transition-colors";
  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300"
  };
  
  return (
    <button 
      className={`${baseStyles} ${variants[variant]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

### 4. 自动化工具开发

**脚本开发场景**：
- 文件批量处理
- 数据同步
- 报告生成
- 部署自动化

**Python自动化示例**：
```python
import os
import shutil
from pathlib import Path

def organize_downloads():
    """自动整理下载文件夹"""
    downloads = Path.home() / "Downloads"
    
    file_types = {
        "images": [".jpg", ".png", ".gif"],
        "documents": [".pdf", ".docx", ".txt"],
        "archives": [".zip", ".rar", ".7z"]
    }
    
    for file in downloads.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            for folder, extensions in file_types.items():
                if ext in extensions:
                    target = downloads / folder
                    target.mkdir(exist_ok=True)
                    shutil.move(str(file), str(target / file.name))
                    print(f"Moved {file.name} to {folder}/")
                    break

if __name__ == "__main__":
    organize_downloads()
```

## 开发最佳实践

### 代码质量
- **DRY原则** - Don't Repeat Yourself
- **单一职责** - 函数/类只做一件事
- **清晰命名** - 自解释的变量和函数名
- **注释文档** - 解释"为什么"而非"是什么"

### 版本控制
```bash
# 语义化版本
# MAJOR.MINOR.PATCH
# 1.0.0 -> 重大变更
# 1.1.0 -> 新功能
# 1.1.1 -> Bug修复

# Git工作流
git checkout -b feature/new-feature
git commit -m "feat: add user authentication"
git push origin feature/new-feature
```

### 调试技巧
- 使用断点而非print
- 阅读错误堆栈从下到上
- 最小复现测试用例
- 善用日志分级

## 工具生态

| 类别 | 工具 |
|------|------|
| **IDE** | VS Code, JetBrains系列 |
| **调试** | Chrome DevTools, pdb |
| **测试** | Jest, pytest, Playwright |
| **容器** | Docker, Docker Compose |
| **CI/CD** | GitHub Actions, GitLab CI |

## 参考资源

- [Clean Code - Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Godot Documentation](https://docs.godotengine.org/)
- [Python Cookbook](https://dabeichen.readthedocs.io/)
