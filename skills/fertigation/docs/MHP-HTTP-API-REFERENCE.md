# MHP 灌溉控制器 HTTP API 协议参考

> **协议版本**: v1.3  
> **作者**: 黄华东  
> **创建日期**: 2023.11.29  
> **通讯方式**: HTTP  
> **文档类型**: 硬件控制器接口协议

---

## 1. 协议概览

### 1.1 通讯参数

| 参数 | 值 |
|------|-----|
| Host | `mhelectr.top` |
| Port | `13600` |
| HTTP 版本 | 1.1 |
| 请求方式 | GET / POST |
| Content-Type | `application/x-www-form-urlencoded` |

### 1.2 测试账号

```
测试帐号: 88888888888
测试灌溉服务器 ID: 2119992778
```

---

## 2. API 接口详解

### 2.1 获取设备列表

**请求方式**: `GET`  
**请求地址**: `/api/devicelist/get`

#### 请求参数

| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| `acctount` | string | 帐号 | 是 |
| `page` | int | 要访问的页码 (0 ~ 30) | 否 |

> **注意**: 当请求参数为空时，服务器返回第 0 页的内容

#### 请求示例

```http
GET http://mhelectr.top:13600/api/devicelist/get?acctount=88888888888&page=0
```

#### 响应数据结构

```json
{
  "summation": {
    "device": 25,           // 所有关注的设备总数
    "online": 10,           // 在线的设备总数
    "offline": 5,           // 离线的设备总数
    "ctrlcount": 120,       // 所有关注的设备包含的控制对象总数
    "ctrlopencount": 20,    // 控制对象打开总数
    "ctrlclosecount": 92,   // 控制对象关闭总数
    "ctrlerrcount": 10,     // 控制对象故障总数
    "motcount": 230         // 所有关注的设备包含的监测对象总数
  },
  "page": {
    "total": 1,             // 页总数
    "page": 0,              // 当前页序号 (0 ~ [total-1])
    "count": 3              // 当前页列表中包含的设备总数
  },
  "list": [
    {
      "deviceid": "88382930097",    // 设备唯一 ID 序列号
      "name": "设备",               // 设备名
      "status": "在线",             // 在线状态 (在线/离线)
      "biosversion": "BiosV1.0",    // 设备 BIOS 版本号
      "appversion": "AppV2.1",      // 设备应用版本号
      "city": "西乡塘",             // 所在城镇
      "ctrlcount": 10,              // 控制对象总数
      "ctrlopencount": 3,           // 控制对象-打开总数
      "ctrlclosecount": 4,          // 控制对象-关闭总数
      "ctrlerrcount": 3,            // 控制对象-故障总数
      "motcount": 5                 // 监测对象总数
    }
  ],
  "msg": "操作成功",
  "code": 200
}
```

---

### 2.2 获取设备注册表

**请求方式**: `GET`  
**请求地址**: `/api/registtab/get`

#### 请求参数

| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| `acctount` | string | 帐号 | 是 |
| `registid` | string | 灌溉服务器设备的唯一 ID | 是 |

#### 请求示例

```http
GET http://mhelectr.top:13600/api/registtab/get?acctount=88888888888&registid=2119992778
```

#### 响应数据结构

```json
{
  "pumptab": {
    "count": 2,
    "list": [
      {
        "nodeaddr": 1,              // 结点地址
        "subaddr": 1,               // 子地址
        "name": "水泵",             // 名称
        "type": "水泵",             // 类型
        "lan": "无线",              // 设备入网方式 (无线/有线)
        "power": "80%",             // 设备电量
        "signal": "-89dbm(强)",     // 无线信号强度
        "status": "关闭",           // 状态 (打开/关闭)
        "count": 3,                 // 管控包含的开关对象总数
        "list": [                   // 管控包含的开关对象列表 (子设备)
          {
            "nodeaddr": 1,
            "subaddr": 2,
            "name": "阀门",
            "type": "阀门",
            "lan": "无线",
            "power": "80%",
            "signal": "-89dbm(强)",
            "status": "关闭",
            "count": 0,               // 子设备数量
            "list": []                // 子设备列表 (支持多级嵌套)
          }
        ]
      }
    ]
  },
  "msg": "操作成功",
  "code": 200
}
```

---

## 3. 数据模型详解

### 3.1 设备对象 (Device)

| 字段 | 类型 | 描述 | 示例 |
|------|------|------|------|
| `deviceid` | string | 设备唯一 ID 序列号 | `"88382930097"` |
| `name` | string | 设备名称 | `"设备"` |
| `status` | string | 在线状态 | `"在线"` / `"离线"` |
| `biosversion` | string | BIOS 版本号 | `"BiosV1.0"` |
| `appversion` | string | 应用版本号 | `"AppV2.1"` |
| `city` | string | 所在城镇 | `"西乡塘"` |
| `ctrlcount` | int | 控制对象总数 | `10` |
| `ctrlopencount` | int | 控制对象打开数 | `3` |
| `ctrlclosecount` | int | 控制对象关闭数 | `4` |
| `ctrlerrcount` | int | 控制对象故障数 | `3` |
| `motcount` | int | 监测对象总数 | `5` |

### 3.2 控制对象 (Control Node)

| 字段 | 类型 | 描述 | 示例 |
|------|------|------|------|
| `nodeaddr` | int | 结点地址 | `1` |
| `subaddr` | int | 子地址 | `2` |
| `name` | string | 设备名称 | `"阀门"` / `"水泵"` |
| `type` | string | 设备类型 | `"阀门"` / `"水泵"` |
| `lan` | string | 入网方式 | `"无线"` / `"有线"` |
| `power` | string | 电量百分比 | `"80%"` |
| `signal` | string | 信号强度 | `"-89dbm(强)"` |
| `status` | string | 开关状态 | `"打开"` / `"关闭"` |
| `count` | int | 子设备数量 | `3` |
| `list` | array | 子设备列表 | `[...]` |

#### 信号强度解读

| 信号值 | 状态 | 建议 |
|--------|------|------|
| `-50dbm ~ -70dbm` | 极强/强 | 通信质量良好 |
| `-70dbm ~ -85dbm` | 中等 | 可正常使用 |
| `-85dbm ~ -100dbm` | 弱 | 注意信号稳定性 |
| `< -100dbm` | 极弱 | 建议检查设备位置 |

---

## 4. 设备层级结构

MHP 控制器采用树形层级结构管理设备：

```
灌溉服务器 (registid)
    └── 水泵 (nodeaddr: 01, subaddr: 01)
            ├── 阀门 1 (nodeaddr: 01, subaddr: 02)
            ├── 阀门 2 (nodeaddr: 01, subaddr: 03)
            └── 阀门 3 (nodeaddr: 01, subaddr: 04)
                └── 子阀门 (支持多级嵌套)
    └── 水泵 (nodeaddr: 02, subaddr: 01)
            └── ...
```

### 地址编码规则

- **nodeaddr**: 主设备地址（如水泵地址）
- **subaddr**: 从设备地址（如阀门地址）
- 一对 (nodeaddr, subaddr) 唯一标识一个控制节点

---

## 5. 状态管理

### 5.1 设备在线状态

| 状态 | 说明 | 处理建议 |
|------|------|----------|
| `在线` | 设备正常连接 | 可正常控制 |
| `离线` | 设备断开连接 | 检查网络/电源 |

### 5.2 控制对象状态流转

```
关闭 → 打开 → 关闭
  ↑              ↓
  └──────────────┘
```

### 5.3 故障处理

当 `ctrlerrcount > 0` 时，表示存在故障设备：

1. 遍历控制对象列表查找异常状态
2. 检查 `signal` 和 `power` 字段
3. 记录故障设备地址 (nodeaddr, subaddr)
4. 发送告警通知

---

## 6. 最佳实践

### 6.1 轮询策略

| 接口 | 建议频率 | 说明 |
|------|----------|------|
| `/api/devicelist/get` | 30 秒 | 监控设备在线状态 |
| `/api/registtab/get` | 5 分钟 | 获取完整设备拓扑 |
| 状态变更检测 | 实时 | 对比上次状态差异 |

### 6.2 异常处理

```python
# 伪代码示例
def get_device_status(acctount, page=0):
    try:
        response = http_get(f"/api/devicelist/get?acctount={acctount}&page={page}")
        if response.code != 200:
            log_error(f"API 错误: {response.msg}")
            return None
        
        # 检查故障设备
        for device in response.list:
            if device.ctrlerrcount > 0:
                alert(f"设备 {device.deviceid} 存在 {device.ctrlerrcount} 个故障")
        
        return response
    except NetworkError:
        log_error("网络连接失败")
        return None
```

### 6.3 数据缓存

- 设备注册表结构变化不频繁，可本地缓存
- 设备状态实时性要求高，建议每次查询
- 信号强度/电量变化缓慢，可 5-10 分钟更新

---

## 7. 与服务端集成

### 7.1 推荐架构

```
┌─────────────────────────────────────────────────────────────┐
│                    冈仁波齐服务端 (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 设备管理模块  │  │ 灌溉调度模块  │  │ 数据存储模块  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│              MHP HTTP Client (Python requests)                │
├─────────────────────────────────────────────────────────────┤
│  • 设备列表轮询              • 注册表缓存                      │
│  • 状态变更检测              • 故障告警                        │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│              MHP 灌溉控制器 (mhelectr.top:13600)              │
├─────────────────────────────────────────────────────────────┤
│  • 无线阀门/水泵控制                                         │
│  • 土壤墒情传感器采集                                        │
│  • 气象站数据接入                                            │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Python SDK 示例

```python
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ControlNode:
    nodeaddr: int
    subaddr: int
    name: str
    type: str
    status: str
    power: str
    signal: str
    children: List['ControlNode']

class MHPClient:
    """MHP 灌溉控制器 HTTP 客户端"""
    
    BASE_URL = "http://mhelectr.top:13600"
    
    def __init__(self, account: str, registid: str):
        self.account = account
        self.registid = registid
    
    def get_device_list(self, page: int = 0) -> Dict:
        """获取设备列表"""
        url = f"{self.BASE_URL}/api/devicelist/get"
        params = {"acctount": self.account, "page": page}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_registtab(self) -> Dict:
        """获取设备注册表"""
        url = f"{self.BASE_URL}/api/registtab/get"
        params = {"acctount": self.account, "registid": self.registid}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def parse_control_tree(self, data: Dict) -> List[ControlNode]:
        """解析控制对象树"""
        pumps = data.get("pumptab", {}).get("list", [])
        return [self._parse_node(p) for p in pumps]
    
    def _parse_node(self, data: Dict) -> ControlNode:
        """递归解析节点"""
        children = [self._parse_node(c) for c in data.get("list", [])]
        return ControlNode(
            nodeaddr=data["nodeaddr"],
            subaddr=data["subaddr"],
            name=data["name"],
            type=data["type"],
            status=data["status"],
            power=data.get("power", "N/A"),
            signal=data.get("signal", "N/A"),
            children=children
        )

# 使用示例
client = MHPClient("88888888888", "2119992778")
devices = client.get_device_list()
registtab = client.get_registtab()
control_tree = client.parse_control_tree(registtab)
```

---

## 8. 故障排查

### 8.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 设备显示离线 | 网络中断/电源故障 | 检查设备电源和网络连接 |
| 控制无响应 | 信号弱/设备故障 | 检查 signal 和 ctrlerrcount |
| 电量下降快 | 低温/频繁通讯 | 减少轮询频率，检查电池 |
| 阀门状态不一致 | 通讯延迟/丢包 | 增加重试机制，状态确认 |

### 8.2 状态码

| Code | 含义 | 处理 |
|------|------|------|
| 200 | 操作成功 | 正常 |
| 400 | 参数错误 | 检查请求参数 |
| 401 | 认证失败 | 检查 account 和 registid |
| 500 | 服务器错误 | 稍后重试或联系技术支持 |

---

## 9. 相关资源

- **项目主页**: https://hiyascott.github.io/scott-portfolio/research/kailash-irrigation/
- **能力图谱**: https://hiyascott.github.io/scott-portfolio/skills/irrigation/
- **Fertigation Skill**: `/skills/fertigation/`
- **Soil & Water Skill**: `/skills/soil-water-management/`

---

*本文档基于 MHP-HTTP1.3 协议文档整理，用于冈仁波齐天山灌溉系统项目。*
