# MMORPG 架构设计

## 概述

MMORPG (Massively Multiplayer Online Role-Playing Game) 需要支持大量玩家同时在线，对服务器架构有特殊要求。

## 四层服务器架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│                    (玩家客户端)                              │
├─────────────────────────────────────────────────────────────┤
│                        Proxy Layer                          │
│           (网关服务器 / Gateway / Load Balancer)            │
├─────────────────────────────────────────────────────────────┤
│                      Game Logic Layer                       │
│         (游戏逻辑服务器 / Zone Server / Instance)          │
├─────────────────────────────────────────────────────────────┤
│                       Database Layer                        │
│        (数据库 / Cache / Message Queue / Log)              │
└─────────────────────────────────────────────────────────────┘
```

## 各层职责

### 1. Client Layer (客户端层)

**特性**: 瘦客户端 (Thin Client)

**职责**:
- 图形渲染
- 用户输入处理
- 本地预测与插值
- 状态展示

**关键设计**:
- 客户端不处理核心逻辑
- 所有关键计算在服务端验证
- 客户端预测减少延迟感知

### 2. Proxy Layer (代理层)

**组件**:
- Login Server (登录服务器)
- Gateway Server (网关服务器)
- Load Balancer (负载均衡器)

**职责**:
- 连接管理
- 消息路由
- 安全验证
- 流量控制

### 3. Game Logic Layer (游戏逻辑层)

**组件**:
- Zone Server (区域服务器)
- World Server (世界服务器)
- Instance Server (副本服务器)
- Matchmaking Server (匹配服务器)

**职责**:
- 游戏状态管理
- 物理/战斗计算
- NPC AI
- 事件处理

### 4. Database Layer (数据库层)

**组件**:
- Account DB (账号数据库)
- Game DB (游戏数据库)
- Log DB (日志数据库)
- Cache (Redis等缓存)
- Message Queue (消息队列)

## 世界分割策略

### 1. Zoning (分区)

将大世界划分为多个区域，每个区域由独立服务器处理。

```
World Map:
┌───┬───┬───┐
│ A │ B │ C │
├───┼───┼───┤
│ D │ E │ F │
├───┼───┼───┤
│ G │ H │ I │
└───┴───┴───┘

Each zone → Separate server
```

**优点**:
- 水平扩展
- 负载均衡
- 故障隔离

**挑战**:
- 跨区交互复杂
- 边界同步问题
- 玩家跨区延迟

### 2. Sharding (分服)

将玩家分散到多个独立的世界副本。

```
Shard 1: 玩家1-1000
Shard 2: 玩家1001-2000
Shard 3: 玩家2001-3000
```

**优点**:
- 完全隔离
- 简单实现
- 独立运营

**缺点**:
- 玩家无法跨服交互
- 资源利用率低
- 服务器选择问题

### 3. Instancing (实例化)

对特定区域创建多个副本。

```
Dungeon A:
├── Instance 1 (Players 1-5)
├── Instance 2 (Players 6-10)
└── Instance 3 (Players 11-15)
```

**适用场景**:
- 副本/地下城
- 任务场景
- 竞技场

## 关键技术

### AOI (Area of Interest)

只同步玩家视野范围内的状态更新。

```
Player AOI Radius = R
Only entities within R are synchronized
```

**算法**:
- 九宫格
- 十字链表
- 空间哈希

### 状态同步方案

#### 1. 状态同步 (State Synchronization)
- 服务器权威
- 定期广播状态
- 客户端插值

#### 2. 帧同步 (Lockstep)
- 确定性模拟
- 只同步输入
- 严格时序

### 跨区交互处理

```
Player moves from Zone A to Zone B:
1. Lock movement in Zone A
2. Transfer player data to Zone B
3. Notify Zone B to accept player
4. Update player connection to new server
5. Unlock movement in Zone B
```

## 可扩展性设计

### 动态负载均衡

```
Load Balancer Algorithm:
- Monitor server load (CPU/Memory/Network)
- Dynamically assign zones to servers
- Migrate overloaded zones to new servers
- Balance player distribution
```

### 无状态设计

- 玩家数据持久化到数据库
- 服务器可随时重启/替换
- 支持快速扩容

## 性能优化

### 1. 网络优化
- 协议优化 (Protobuf/MessagePack)
- 压缩
- 差值同步
- 批量更新

### 2. 计算优化
- 空间分割
- LOD (Level of Detail)
- 事件优先级
- 异步处理

### 3. 存储优化
- 读写分离
- 分表分库
- 缓存策略
- 冷热数据分离

## 参考架构

### 经典MMORPG架构

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Gateway   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ Zone A  │◄─────►│ Zone B  │◄─────►│ Zone C  │
   │ Server  │       │ Server  │       │ Server  │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │     DB      │
                    └─────────────┘
```

## 参考文献

- Massive Multiplayer Online Game Architectures - Martijn Moraal
- A Distributed Architecture for MMORPG - NUS
- MMOG Server Architecture Best Practices
