# 花园灌溉CAD设计系统

基于CAD图纸自动生成灌溉管路和点位的软件原型。

## 项目概述

将现有的**花园灌溉报价计算器**升级为CAD级别的自动化设计工具：
- 用户上传CAD图纸（或手动绘制区域）
- 系统自动计算喷头点位、管路走向
- 输出DXF/PDF格式的专业设计图纸
- 同时生成材料清单和报价

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Python + FastAPI | API服务 |
| 几何计算 | shapely + 纯Python | 多边形运算、喷头布局 |
| DXF输出 | 纯文本DXF生成器 | 不依赖AutoCAD，兼容所有CAD软件 |
| PDF输出 | matplotlib | 矢量图纸渲染 |
| 前端 | HTML5 Canvas + 原生JS | 区域绘制、方案预览 |

## 核心算法

### 喷头布局算法
1. **区域识别**：从CAD线条提取封闭多边形
2. **喷头选型**：根据宽度+植物类型，复用灌溉计算器逻辑
3. **位置计算**：六边形密铺 + 边界裁剪
4. **管路生成**：最小生成树连接喷头

### 阀门分组
- 按喷头类型分组（同类型喷头共用阀门）
- 每组流量不超过水源流量
- 自动计算控制器型号

## 文件结构

```
irrigation-cad/
├── backend/
│   ├── app/
│   │   └── main.py           # FastAPI入口
│   ├── core/
│   │   ├── sprinkler_layout.py  # 喷头布局算法（核心）
│   │   ├── pipe_routing.py      # 管路规划（待完善）
│   │   └── dxf_writer.py        # DXF/PDF输出
│   └── models/
│       └── schemas.py        # Pydantic模型
├── frontend/
│   └── index.html            # Canvas交互前端
├── docs/                     # 文档
└── tests/                    # 测试
```

## 当前进度

### ✅ 已完成
- [x] 喷头布局核心算法（纯Python）
- [x] DXF文件生成器（纯文本格式，零依赖）
- [x] FastAPI后端框架（API定义）
- [x] Pydantic请求/响应模型
- [x] 前端Canvas交互原型（区域绘制）

### ⏳ 待完成
- [ ] 依赖安装（网络恢复后安装 shapely, fastapi, matplotlib）
- [ ] 管道路径优化算法（避障、最小管长）
- [ ] DWG转DXF（AutoCAD/ODA SDK集成）
- [ ] 后端API联调
- [ ] 前端对接真实API
- [ ] 材料清单自动生成
- [ ] 水力计算验证

## 启动方式

```bash
# 1. 安装依赖
pip install ezdxf shapely fastapi uvicorn matplotlib numpy pydantic

# 2. 启动后端
cd backend
uvicorn app.main:app --reload

# 3. 打开前端
# 直接用浏览器打开 frontend/index.html
# 或部署到任意静态服务器
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/api/config` | GET | 获取喷头配置 |
| `/api/design` | POST | 生成设计方案 |
| `/api/export/dxf` | POST | 导出DXF |
| `/api/export/pdf` | POST | 导出PDF |
| `/api/download/{file}` | GET | 下载文件 |

## 使用流程

```
用户操作                          系统响应
─────────────────────────────────────────────────
上传CAD图纸 (.dwg/.dxf)
     ↓
系统自动识别绿化区域（或用户手动圈选）
     ↓
设置参数（植物类型、水源、管径等）
     ↓
点击"生成方案"
     ↓
系统计算：喷头位置 → 管路走向 → 阀门分组
     ↓
预览设计图（Canvas实时渲染）
     ↓
确认后下载：DXF（CAD编辑）/ PDF（交付客户）
     ↓
同时生成：材料清单 + 报价表
```

## 参考对象

- **算法设计**：参考了传统灌溉CAD软件（如Rain Bird、Hunter的专用设计工具）
- **UI风格**：参考 AutoCAD Web 版的暗色主题 + 精确工具栏
- **交互模式**：参考 Figma / Blender 的多边形绘制工具

## 下一步

1. 等待网络恢复，安装Python依赖
2. 跑通第一个测试用例（单个矩形区域 → DXF输出）
3. 优化管路算法（最小生成树 + Steiner点）
4. 集成DWG解析（ezdxf读取DXF已支持，DWG需转格式）
