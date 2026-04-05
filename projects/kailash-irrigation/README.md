# 冈仁波齐天山灌溉系统 - MHP 控制器对接

🌾 面向西藏高海拔地区的智能水肥一体化控制系统，对接 MHP 灌溉控制器 HTTP API。

## 项目结构

```
kailash-irrigation/
├── src/
│   ├── mhp_client/           # MHP 控制器客户端 SDK
│   │   ├── __init__.py
│   │   ├── client.py         # 核心客户端
│   │   └── service.py        # 服务端集成
│   └── api/
│       └── routes/
│           └── mhp.py        # FastAPI 路由
├── main.py                   # FastAPI 主应用
├── requirements.txt          # Python 依赖
└── .env.example             # 配置模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置 MHP_ACCOUNT 和 MHP_REGISTID
```

### 3. 启动服务

```bash
python main.py
```

服务将在 http://localhost:8000 启动，API 文档访问 http://localhost:8000/docs

## MHP 客户端使用

### 基础用法

```python
from src.mhp_client import create_client

# 创建客户端
with create_client("88888888888", "2119992778") as client:
    # 获取设备列表
    devices, summary = client.get_device_list()
    print(f"在线设备: {summary.online_devices}")
    
    # 获取设备详情（包含控制树）
    device = client.get_device_with_controls()
    for pump in device.get_pumps():
        print(f"水泵: {pump.name}, 状态: {pump.status}")
```

### 异步服务集成

```python
from src.mhp_client.service import MHPDeviceService

service = MHPDeviceService("88888888888", "2119992778")

# 获取系统健康状态
health = await service.get_system_health()
print(f"在线率: {health['online_rate']}")

# 获取灌溉状态
status = await service.get_irrigation_status("2119992778")
print(f"活跃区域: {len(status['active_zones'])}")
```

## API 接口

### 设备管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/mhp/devices` | 获取所有设备列表 |
| GET | `/mhp/devices/{id}` | 获取设备详情 |
| GET | `/mhp/devices/{id}/irrigation` | 获取灌溉状态 |
| GET | `/mhp/devices/{id}/pumps` | 获取水泵状态 |
| GET | `/mhp/devices/{id}/valves` | 获取阀门列表 |

### 系统监控

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/mhp/health` | 系统健康状态 |
| GET | `/mhp/summary` | 仪表盘汇总 |

## 控制器协议

- **协议**: MH Device HTTP API v1.3
- **Host**: mhelectr.top:13600
- **测试账号**: 88888888888 / 2119992778

详细协议文档: [MHP API 参考](../../skills/irrigation/docs/mhp-api-reference.html)

## 功能特性

- ✅ 设备列表自动轮询（30s）
- ✅ 控制对象树形解析
- ✅ 信号强度/电量监控
- ✅ 故障自动检测
- ✅ 灌溉状态实时查询
- ✅ FastAPI RESTful 接口
- ✅ 异步后台任务

## 相关资源

- [项目主页](https://hiyascott.github.io/scott-portfolio/research/kailash-irrigation/)
- [能力图谱](https://hiyascott.github.io/scott-portfolio/skills/irrigation/)
- [MHP 协议文档](https://hiyascott.github.io/scott-portfolio/skills/irrigation/docs/mhp-api-reference.html)
