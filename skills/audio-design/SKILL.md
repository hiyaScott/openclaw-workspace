---
name: audio-design
description: 游戏音频设计与实现能力，涵盖Web Audio API、Wwise 2024.1音频中间件、交互式音乐系统、音效设计和空间音频技术。
---

# 音频设计

## 概述

游戏音频设计是游戏体验的核心组成部分，包括音效、音乐、语音和空间音频的设计与实现。本技能涵盖浏览器端Web Audio API技术和专业音频中间件（Wwise）两大方向。

---

## 第一部分：Web Audio API

浏览器端的原生音频处理能力，适用于Web游戏和交互式网页应用。

### 基础用法

```javascript
// 创建音频上下文
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// 加载音频
const response = await fetch('sound.mp3');
const arrayBuffer = await response.arrayBuffer();
const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

// 播放
const source = audioContext.createBufferSource();
source.buffer = audioBuffer;
source.connect(audioContext.destination);
source.start();
```

### 3D音频定位

```javascript
// Web Audio 3D定位
const panner = audioContext.createPanner();
panner.positionX.value = x;
panner.positionY.value = y;
panner.positionZ.value = z;
panner.connect(audioContext.destination);
```

### 音频路由与效果

```javascript
// 创建压缩器（防破音）
const compressor = audioContext.createDynamicsCompressor();
compressor.threshold.value = -12;
compressor.ratio.value = 4;

// 增益控制
const gainNode = audioContext.createGain();
gainNode.gain.value = 0.5;

// 连接链：源 → 效果 → 输出
source.connect(compressor);
compressor.connect(gainNode);
gainNode.connect(audioContext.destination);
```

### Web Audio 最佳实践

| 技术点 | 建议 |
|--------|------|
| 自动播放策略 | 等待用户交互后初始化音频上下文 |
| 内存管理 | 复用AudioBuffer，及时断开节点连接 |
| 移动端优化 | 使用压缩器防止破音，控制同时播放数量 |
| 频率选择 | 避免手机不友好的超低频(<100Hz) |

---

## 第二部分：Wwise 2024.1 for Godot 集成

专业音频中间件解决方案，适用于需要高质量音频的中大型游戏项目。

### 概述

Wwise 是 Audiokinetic 开发的专业音频中间件，广泛应用于游戏行业。Wwise 2024.1 for Godot 是与 Godot 4.3+ 深度集成的版本，提供了与 Unity、Unreal 类似的现代化工作流程。

**版本支持**
- **Wwise**: 2024.1.x (推荐 2024.1.9+)
- **Godot**: 4.3, 4.4, 4.5
- **集成方式**: GDExtension（无需重新编译引擎）

---

### Wwise 2024.1 新特性

#### 1. WwiseProjectDatabase 替代 WAAPI

Wwise 2024.1 引入了 **WwiseProjectDatabase** 作为新的数据源，完全替代了旧版基于 WAAPI 的工作流程。

**旧版 WAAPI 的局限性**
- 需要同时打开 Wwise Authoring 和 Godot Editor
- 多项目打开时可能产生冲突
- 缺乏层级化的工程概览（WorkUnits、文件夹不显示）
- SoundBank 更新后需要手动重新生成 IDs

**新版 ProjectDatabase 优势**
- **自动监控**: 监听指定的 SoundBank 目录，自动更新数据
- **层级结构**: 完整显示 Wwise 工程结构（WorkUnits、文件夹）
- **WwiseProjectData 资产**: 自动生成，包含所有核心对象数据
  - Acoustic Textures（声学纹理）
  - Aux Buses（辅助总线）
  - SoundBanks（音频包）
  - Events（事件）
  - Game Parameters（游戏参数）
  - States（状态）
  - Switches（切换开关）
  - Triggers（触发器）

**配置方法**
```
Project Settings → Wwise → General → SoundBank Directory
设置为 Wwise 工程生成的 SoundBank 输出目录
```

#### 2. Wwise Types 在 Godot Inspector 中使用

Wwise Types 是一组代表 Wwise 核心对象的类，可以直接在 Godot Inspector 中序列化和编辑。

**支持的 Wwise Types**

| Type | 用途 | 内置方法 |
|------|------|----------|
| `WwiseEvent` | 音频事件 | `post()`, `post_callback()`, `prepare()`, `unprepare()` |
| `WwiseRTPC` | 实时参数控制 | `set_value()`, `get_value()` |
| `WwiseBank` | SoundBank | `load()`, `unload()` |
| `WwiseState` | 全局状态 | `set_value()` |
| `WwiseSwitch` | 对象开关 | `set_value()` |
| `WwiseTrigger` | 触发器 | `post()` |
| `WwiseAuxBus` | 辅助总线 | - |
| `WwiseAcousticTexture` | 声学纹理 | - |

**Inspector 用法**

1. 在 GDScript 中导出 Wwise Type:
```gdscript
@export var footstep_event: WwiseEvent
@export var engine_rtpc: WwiseRTPC
@export var surface_switch: WwiseSwitch
```

2. 在 Inspector 中点击按钮，使用 **Wwise Picker** 选择对象
3. 自动生成对应的 Resource 到 `res://Wwise/resources/`

#### 3. Auto-Defined SoundBanks 自动管理

Wwise 2024.1 支持 **Auto-Defined SoundBanks**，无需手动管理 SoundBank 加载。

**工作原理**
- 当 `WwiseEvent` 引用的事件不在用户定义的 SoundBank 中时
- 集成自动调用 `AK::SoundEngine::PrepareEvent()` 准备事件
- `WwiseEvent` 销毁且不再被引用时，自动 Unprepare 并卸载
- ProjectDatabase 自动判断事件是否属于 User-Defined SoundBank

**配置步骤**
1. 在 Wwise 中: `Project Settings → SoundBanks → Enable Auto-Defined SoundBanks`
2. 在 Godot 中: 使用 `@export var event: WwiseEvent` 导出事件
3. 运行时自动处理加载/卸载

**注意事项**
- `AkBank` 节点和 `WwiseBank` type 的 Picker 中只显示 **User-Defined SoundBanks**
- Auto-Defined SoundBank 不需要也不应该在代码中手动加载

#### 4. 插件支持简化

Wwise 2024.1 大幅简化了插件使用流程。

**旧版流程（复杂）**
- 需要重新编译集成
- 手动指定插件（如 AK Convolution Reverb）

**新版流程（简化）**
- **自动检测**: ProjectDatabase 识别工程中使用的插件
- **自动导出**: 导出时自动复制所需插件到目标目录
- **编辑器预览**: 使用 `AkInitSettings::szPluginDLLPath` 自动加载
- **iOS 支持**: 使用 `EditorExportPlugin` API 自动添加静态库和初始化代码

**自定义插件使用**
1. 将 Sound Engine Plugins 复制到集成的平台 DSP 文件夹
2. ProjectDatabase 自动检测使用
3. 无需重新编译集成

---

### 集成流程（Godot 4.3+）

#### 安装步骤

1. **下载集成**
   - 访问 [GitHub Releases](https://github.com/alessandrofama/wwise-godot-integration/releases)
   - 下载对应 Wwise 2024.1 和 Godot 4.3+ 的版本

2. **安装插件**
   - 解压到 Godot 项目的 `addons/` 目录
   - 确保目录结构为 `addons/Wwise/`

3. **配置 Wwise 工程**
   - 打开 Wwise 2024.1
   - `Project Settings → SoundBanks → Enable Auto-Defined SoundBanks`
   - 生成 SoundBank

4. **配置 Godot 项目设置**
   ```
   Project Settings → Wwise → General:
   - Wwise Project Path: 指向 .wproj 文件
   - SoundBank Directory: 指向 SoundBank 输出目录
   ```

5. **初始化场景**
   - 创建 `WwiseRuntimeManager` 自动节点（加载时自动创建）
   - 或手动添加 `AkInitializer` 节点到主场景

#### ProjectDatabase 工作流

```
Wwise Authoring
      ↓
生成 SoundBank
      ↓
ProjectDatabase 自动监控目录变化
      ↓
更新 WwiseProjectData 资产
      ↓
Wwise Picker / Browser 显示最新数据
      ↓
开发者选择对象 → 生成 Resource
```

#### Wwise Picker 用法

**打开方式:**
- `Project → Tools → Wwise Picker`
- 或点击 Inspector 中 Wwise Type 属性的选择按钮

**功能:**
- 层级显示 Wwise 工程结构
- 搜索过滤对象
- 选择后自动生成 Resource
- 显示对象类型图标

#### Wwise Browser 用法

**打开方式:**
```
Project → Tools → Wwise Browser
```

**功能:**
- 查询 Wwise 工程数据
- 直接在编辑器中生成 SoundBank
- 生成 Wwise IDs
- 查看工程统计信息

---

### 实战代码示例

#### 基础设置

**场景结构示例**
```
MainScene
├── Player (CharacterBody3D)
│   ├── AkListener3D          # 3D 监听器
│   └── FootstepEmitter       # 脚步声音发射器
├── Environment
│   ├── AkRoom (Forest)       # 房间环境
│   ├── AkRoom (Cave)
│   └── AkPortal (Forest_Cave) # 房间连接
└── WwiseRuntimeManager       # 自动创建的运行时管理器
```

#### WwiseEvent.post() 方法

**方法 1: 使用 Wwise Singleton（传统方式）**
```gdscript
extends Node3D

@export var event_name: String = "Play_Footstep"

func play_sound():
    # 在当前节点关联的游戏对象上播放
    Wwise.post_event(event_name, self)
    
    # 在特定游戏对象上播放
    var game_object_id = AkUtils.get_game_object_id(player_node)
    Wwise.post_event(event_name, game_object_id)
```

**方法 2: 使用 WwiseEvent Type（推荐方式）**
```gdscript
extends Node3D

@export var footstep_event: WwiseEvent
@export var jump_event: WwiseEvent

func _ready():
    # 确保在初始化后播放
    pass

func play_footstep():
    # 直接调用 WwiseEvent 的 post 方法
    if footstep_event and footstep_event.is_valid():
        footstep_event.post(self)

func play_jump():
    if jump_event:
        jump_event.post(self)

func play_with_callback():
    # 带回调的事件（用于音乐同步等）
    jump_event.post_callback(self, AkUtils.AK_EndOfEvent, _on_event_ended)

func _on_event_ended(event_data: Dictionary):
    print("Event finished: ", event_data)
```

**方法 3: 使用 AkEvent3D 节点**
```gdscript
extends Node3D

@onready var ak_event = $AkEvent3D

func _ready():
    # AkEvent3D 自动处理事件触发
    # 可以通过代码控制
    ak_event.post_event()  # 播放
    ak_event.stop_event()  # 停止
    
    # 连接信号
    ak_event.event_finished.connect(_on_event_finished)

func _on_event_finished():
    print("AkEvent3D finished playing")
```

#### WwiseRTPC.set_value() 用法

**实时参数控制示例**
```gdscript
extends CharacterBody3D

@export var engine_rtpc: WwiseRTPC
@export var speed_rtpc: WwiseRTPC

var current_speed: float = 0.0
var max_speed: float = 100.0

func _physics_process(delta):
    # 计算速度
    current_speed = velocity.length()
    
    # 方法 1: 使用 WwiseRTPC Type（推荐）
    if speed_rtpc:
        # 将速度归一化到 0-100 范围
        var normalized_speed = (current_speed / max_speed) * 100.0
        speed_rtpc.set_value(normalized_speed, self)
    
    # 方法 2: 使用 Wwise Singleton
    Wwise.set_rtpc_value("Speed", current_speed, self)

func set_engine_rpm(rpm: float):
    # 使用 WwiseRTPC 设置引擎转速
    if engine_rtpc:
        engine_rtpc.set_value(rpm, self)

func get_current_rtpc_value():
    # 获取当前 RTPC 值
    if engine_rtpc:
        var value = engine_rtpc.get_value(self)
        print("Current RTPC value: ", value)
```

**RTPC 平滑过渡**
```gdscript
extends Node3D

@export var health_rtpc: WwiseRTPC
var current_health: float = 100.0
var target_health: float = 100.0

func _process(delta):
    # 平滑过渡到目标值
    current_health = lerp(current_health, target_health, delta * 5.0)
    
    if health_rtpc:
        health_rtpc.set_value(current_health, self)

func take_damage(amount: float):
    target_health = max(0.0, target_health - amount)
```

#### AkEvent3D/AkEvent2D 节点使用

**AkEvent3D 完整示例**
```gdscript
extends CharacterBody3D

@onready var footstep_emitter = $FootstepEmitter
@onready var voice_emitter = $VoiceEmitter

@export var footstep_event: WwiseEvent
@export var jump_event: WwiseEvent
@export var land_event: WwiseEvent

var is_on_ground: bool = false

func _ready():
    # 设置发射器事件
    if footstep_event:
        footstep_emitter.event = footstep_event
    
    # 连接事件回调信号
    footstep_emitter.event_finished.connect(_on_footstep_finished)

func _physics_process(delta):
    # 检测着陆
    if is_on_ground and not is_on_floor():
        is_on_ground = false
    elif not is_on_ground and is_on_floor():
        is_on_ground = true
        play_land_sound()

func play_footstep():
    # 方法 1: 使用节点的 post_event
    footstep_emitter.post_event()
    
    # 方法 2: 直接调用 WwiseEvent
    # footstep_event.post(footstep_emitter)

func play_jump_sound():
    if jump_event:
        jump_event.post(self)

func play_land_sound():
    if land_event:
        land_event.post(self)

func _on_footstep_finished():
    print("Footstep sound completed")

func stop_all_sounds():
    # 停止此节点上的所有事件
    Wwise.stop_all(self)
```

**AkEvent2D 示例（2D 游戏）**
```gdscript
extends CharacterBody2D

@onready var ak_event_2d = $AkEvent2D

@export var shoot_event: WwiseEvent
@export var explosion_event: WwiseEvent

func _ready():
    # AkEvent2D 适用于 2D 游戏
    ak_event_2d.event = shoot_event

func shoot():
    # 每次射击触发事件
    ak_event_2d.post_event()

func explode():
    if explosion_event:
        # 在特定位置播放（即使节点不存在）
        explosion_event.post_at_position(global_position)
```

#### 空间音频（Spatial Audio）

**AkRoom 和 AkPortal 使用**
```gdscript
extends Node3D

# 房间设置通常在编辑器中完成
# 这里展示代码控制示例

@onready var room_a = $ForestRoom
@onready var room_b = $CaveRoom
@onready var portal = $ForestCavePortal

func _ready():
    # 设置房间参数
    room_a.room_tone_event = preload("res://Wwise/resources/ForestAmbience.tres")
    room_b.room_tone_event = preload("res://Wwise/resources/CaveAmbience.tres")
    
    # 配置 Portal
    portal.front_room = room_a.get_path()
    portal.back_room = room_b.get_path()

func player_entered_room(room: AkRoom):
    print("Player entered: ", room.name)
    # 可以在这里触发房间特定的音频变化
```

**AkGeometry（几何体反射）**
```gdscript
extends MeshInstance3D

@onready var ak_geometry = $AkGeometry

func _ready():
    # 从 MeshInstance3D 生成几何体
    ak_geometry.set_geometry_from_mesh(mesh)
    
    # 设置声学纹理
    var acoustic_texture = preload("res://Wwise/resources/ConcreteTexture.tres")
    ak_geometry.acoustic_texture = acoustic_texture
    
    # 设置传输损耗（0-1）
    ak_geometry.transmission_loss = 0.5
```

#### Switch 和 State 控制

**WwiseSwitch 用法**
```gdscript
extends Node3D

@export var surface_switch: WwiseSwitch

enum SurfaceType { CONCRETE, GRASS, METAL, WOOD }
var current_surface: SurfaceType = SurfaceType.CONCRETE

func set_surface(type: SurfaceType):
    current_surface = type
    
    if surface_switch:
        match type:
            SurfaceType.CONCRETE:
                surface_switch.set_value("Concrete", self)
            SurfaceType.GRASS:
                surface_switch.set_value("Grass", self)
            SurfaceType.METAL:
                surface_switch.set_value("Metal", self)
            SurfaceType.WOOD:
                surface_switch.set_value("Wood", self)
```

**WwiseState 用法**
```gdscript
extends Node

@export var game_state: WwiseState

enum GameState { EXPLORATION, COMBAT, STEALTH }

func set_game_state(state: GameState):
    if not game_state:
        return
        
    match state:
        GameState.EXPLORATION:
            game_state.set_value("Exploration")
        GameState.COMBAT:
            game_state.set_value("Combat")
        GameState.STEALTH:
            game_state.set_value("Stealth")
```

#### SoundBank 管理

**手动加载/卸载（User-Defined SoundBanks）**
```gdscript
extends Node

@export var level_bank: WwiseBank
@export var music_bank: WwiseBank

func load_level_banks():
    # 使用 WwiseBank Type
    if level_bank:
        level_bank.load()
    if music_bank:
        music_bank.load()
    
    # 或使用 Wwise Singleton
    Wwise.load_bank("Level1_Bank")
    Wwise.load_bank("Music_Bank")

func unload_level_banks():
    if level_bank:
        level_bank.unload()
    if music_bank:
        music_bank.unload()

func _exit_tree():
    unload_level_banks()
```

---

### Wwise 核心概念

#### 工程 (Project)

Wwise 基于工程管理，一个游戏的所有平台和语言的音频信息集中在一个工程中：
- 管理声音、振动和音乐素材
- 定义对象属性和播放行为
- 创建触发音频的 Event（事件）
- 生成所有平台的 SoundBank

#### 制作管线工作流程

1. **创作**：创建声音、振动和音乐结构，定义属性和行为
2. **模拟**：验证艺术方向和模拟游戏体验
3. **集成**：使用 Wwise Types 和 Auto-Defined SoundBanks 简化集成
4. **混音**：在游戏中实时混合属性
5. **性能分析**：使用 Wwise Profiler 监控资源占用

#### 关键组件

| 组件 | 功能 |
|------|------|
| **Event（事件）** | 触发音频行为的基本单位，可包含播放、停止、音量调整等 |
| **SoundBank** | 包含音频数据和设计参数的数据包 |
| **Switch（切换开关）** | 对象级别的状态切换（如不同地面类型的脚步声）|
| **State（状态）** | 全局状态切换（如场景音乐变化）|
| **RTPC** | 实时参数控制，用于连续数值影响音频（如引擎转速）|
| **Game Syncs** | 游戏同步器总称，包括 Switch、State、RTPC |

---

## 音效设计原则

### 游戏音效类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **UI音效** | 界面交互反馈 | 按钮点击、界面切换 |
| **环境音效** | 背景氛围 | 风声、雨声、城市背景 |
| **动作音效** | 角色动作 | 攻击、跳跃、脚步声 |
| **反馈音效** | 游戏状态反馈 | 得分、受伤、提示音 |

### 设计要点

- **层次感**：前景/中景/背景音效分离
- **频率分布**：避免频率冲突（使用EQ调整）
- **动态范围**：根据游戏场景调整音量
- **风格统一**：保持音频风格一致性

---

## 交互式音乐系统

### 垂直混音 (Vertical Remixing)

通过RTPC控制不同音乐层的音量：
- 使用RTPC控制各层音量
- 设置淡入淡出时间（通常 0.5-3 秒）
- 层可以非同步进入

```gdscript
# 示例：根据紧张度控制音乐层
@export var tension_rtpc: WwiseRTPC

func update_tension(tension_value: float):
    # tension_value: 0-100
    tension_rtpc.set_value(tension_value, self)
```

### 水平重新排序 (Horizontal Resequencing)

- 使用 Playlist 组织音乐片段
- 通过 Switch 或 State 切换不同片段
- 设置过渡规则避免突兀切换

### Stingers 和 Transitions

- **Stingers**：短促音乐标记，用于事件提示
- **Transitions**：音乐段落间的过渡片段
- 可在 Wwise 中设置同步点（Quantization）

---

## 混音技术

| 技术 | 说明 | 适用场景 |
|------|------|----------|
| **Set-volume** | 基础音量混音 | 简单项目 |
| **State-based** | 基于状态的快照混音 | 场景切换 |
| **Auto ducking** | 自动闪避 | 对话时降低BGM |
| **RTPC控制** | 参数控制混音 | 动态变化 |
| **Sidechaining** | 侧链压缩 | 专业音乐制作 |
| **HDR混音** | 高动态范围混音 | 3A游戏 |

---

## 空间音频

### 距离衰减模型

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| **线性衰减** | 简单直接 | 2D游戏 |
| **指数衰减** | 更自然 | 一般3D游戏 |
| **反比衰减** | 物理准确 | 模拟/写实游戏 |

### 3D音频组件（Wwise）

- **AkListener3D**: 3D音频监听器（通常绑定到玩家相机）
- **AkRoom**: 定义声学空间（房间、洞穴等）
- **AkPortal**: 连接两个房间的声音通道
- **AkGeometry**: 几何体反射模拟

---

## 性能优化

### 内存管理

- 使用内存池管理
- 合理规划SoundBank加载策略
- 短音效加载到RAM，长音频使用流式播放
- 利用 Auto-Defined SoundBanks 自动管理

### 流播放

- 根据平台调整流数量
- 设置合适的缓冲区大小
- 预加载关键音频

### 平台适配

| 平台 | 注意事项 |
|------|----------|
| **移动端** | 降低同时播放数，优化内存，注意扬声器频率响应 |
| **Web** | 注意浏览器自动播放策略，使用压缩器防破音 |
| **主机** | 利用硬件音频处理能力 |

### 调试工具（Wwise）

- **Wwise Profiler**: 实时监控性能
- **Game Sync Monitor**: 观察 RTPC 变化
- **Capture Log**: 捕获日志
- **Game Object 3D Viewer**: 查看空间音频对象

---

## 工具与资源

### 专业工具

| 工具 | 用途 |
|------|------|
| **Wwise** | 专业音频中间件 |
| **FMOD** | 另一主流音频中间件 |
| **Reaper** | DAW音频工作站 |
| **Audacity** | 开源音频编辑 |

### 音频资源网站

- Freesound.org
- Epidemic Sound
- Artlist
- AudioJungle

---

## 参考资源

详细信息请查看 `references/resources.md`
