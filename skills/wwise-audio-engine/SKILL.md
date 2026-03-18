---
name: wwise-audio-engine
description: Wwise 音频引擎专业知识，用于游戏音频设计与交互音乐系统实现。当用户需要游戏音频中间件技术、Wwise 集成、交互音乐系统设计、音频事件与参数控制、混音与性能优化时使用此 skill。
---

# Wwise 音频引擎

## 概述

Wwise 是 Audiokinetic 开发的专业音频中间件，广泛应用于游戏行业。与 FMOD 的 timeline-first 结构不同，Wwise 使用 tree-driven 结构来组织声音行为。

## 核心概念

### 工程 (Project)

Wwise 基于工程管理，一个游戏的所有平台和语言的音频信息集中在一个工程中：
- 管理声音、语音、音乐和振动素材
- 定义对象属性和播放行为
- 创建触发音频的 Event（事件）
- 生成所有平台的 SoundBank

### 制作管线工作流程

1. **创作**：创建声音、振动和音乐结构，定义属性和行为
2. **模拟**：验证艺术方向和模拟游戏体验
3. **集成**：早期集成，无需额外编程
4. **混音**：在游戏中实时混合属性
5. **性能分析**：实时监控资源占用

### 关键组件

| 组件 | 功能 |
|------|------|
| **Event（事件）** | 触发音频行为的基本单位，可包含播放、停止、音量调整等 |
| **SoundBank** | 包含音频数据和设计参数的数据包 |
| **Switch（切换开关）** | 对象级别的状态切换（如不同地面类型的脚步声） |
| **State（状态）** | 全局状态切换（如场景音乐变化） |
| **RTPC** | 实时参数控制，用于连续数值影响音频（如引擎转速） |
| **Game Syncs** | 游戏同步器总称，包括 Switch、State、RTPC |

## 交互音乐系统

### 垂直混音 (Vertical Remixing)

Wwise 中通过控制不同音乐层的音量来实现：
- 使用 RTPC 控制各层音量
- 设置淡入淡出时间（通常 0.5-3 秒）
- 层可以非同步进入

### 水平重新排序 (Horizontal Resequencing)

- 使用 Playlist 组织音乐片段
- 通过 Switch 或 State 切换不同片段
- 设置过渡规则避免突兀切换

### Stingers 和 Transitions

- **Stingers**：短促音乐标记，用于事件提示
- **Transitions**：音乐段落间的过渡片段
- 可在 Wwise 中设置同步点（Quantization）

## 程序员集成指南

### 声音引擎初始化

```cpp
// 初始化内存管理器
AK::MemoryMgr::Init();

// 创建流管理器
AK::StreamMgr::Create();

// 初始化 I/O 设备
m_pLowLevelIO->Init();

// 初始化声音引擎
AK::SoundEngine::Init();

// 初始化音乐引擎（可选）
AK::MusicEngine::Init();

// 初始化通信模块（开发版本）
#if !defined AK_OPTIMIZED
AK::Comm::Init();
#endif
```

### 核心 API 调用

```cpp
// 注册/注销游戏对象
AK::SoundEngine::RegisterGameObj(gameObjectID);
AK::SoundEngine::UnregisterGameObj(gameObjectID);

// 触发事件
AK::SoundEngine::PostEvent("EventName", gameObjectID);

// 设置游戏同步器
AK::SoundEngine::SetSwitch("SwitchGroup", "SwitchState", gameObjectID);
AK::SoundEngine::SetState("StateGroup", "State");
AK::SoundEngine::SetRTPCValue("RTPCName", value, gameObjectID);

// 渲染音频（每帧调用）
AK::SoundEngine::RenderAudio();
```

### SoundBank 管理

```cpp
// 加载 SoundBank
AK::SoundEngine::LoadBank("BankName", bankID);

// 卸载 SoundBank
AK::SoundEngine::UnloadBank("BankName", nullptr);
```

### 关闭流程

```cpp
// 关闭通信模块
#if !defined AK_OPTIMIZED
AK::Comm::Term();
#endif

// 关闭音乐引擎
AK::MusicEngine::Term();

// 关闭声音引擎
AK::SoundEngine::Term();

// 关闭 I/O 设备
m_pLowLevelIO->Term();

// 销毁流管理器
AK::IAkStreamMgr::Get()->Destroy();

// 关闭内存管理器
AK::MemoryMgr::Term();
```

## 混音技术

Wwise 提供 6 种混音技术：

1. **Set-volume mixing** - 基础音量混音
2. **State-based (snapshot) mixing** - 基于状态的快照混音
3. **Auto ducking** - 自动闪避
4. **RTPC (parameter controlled)** - 参数控制混音
5. **Sidechaining** - 侧链压缩
6. **HDR (High Dynamic Range) mixing** - 高动态范围混音

## 性能优化

### 内存管理
- 使用内存池管理
- 根据平台调整内存大小
- 合理规划 SoundBank 加载策略

### 流播放
- 长音频使用流式播放而非全加载
- 短音效加载到 RAM
- 根据平台调整流数量

### 调试工具
- Wwise Profiler：实时监控性能
- Game Sync Monitor：观察 RTPC 变化
- Capture Log：捕获日志

## 游戏引擎集成

### Unity 集成
- 使用 Wwise Unity Integration
- 通过 AkGameObj、AkBank、AkEvent 组件
- 支持 C# 脚本控制

### Unreal 集成
- 使用 Wwise Unreal Integration
- 通过 Blueprint 或 C++
- 内置音频组件支持

## 参考资源

- Wwise Fundamentals 官方指南
- Wwise 快速上手指南：程序员篇
- Wwise Project Adventure 教程
- Audiokinetic 官方学习资源：https://www.audiokinetic.com/education/learn-wwise/
