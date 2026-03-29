# Game AI Design - 游戏AI设计

游戏AI系统设计指南，涵盖从基础状态机到高级群体AI的完整知识体系。

---

## 1. 游戏AI概述

### 1.1 游戏AI与学术AI的区别

| 维度 | 学术AI | 游戏AI |
|------|--------|--------|
| **目标** | 最优解、真实性、性能 | 可玩性、娱乐性、可控性 |
| **约束** | 计算资源充足 | 实时性、性能预算 |
| **评估** | 准确度、效率 | 玩家体验、趣味性 |
| **透明度** | 黑盒可接受 | 需要可调试、可设计 |
| **失败处理** | 避免失败 | 可控的失败增强体验 |

**核心区别**：学术AI追求"正确"，游戏AI追求"有趣"。

### 1.2 可玩性优先于真实感

**为什么真实感不是首要目标？**

1. **真实可能无趣**：真实的狙击手可能长时间等待，玩家会觉得无聊
2. **公平性需求**：AI需要给玩家"赢的机会"
3. **性能限制**：完全真实的物理模拟不可行
4. **设计意图**：AI行为应服务于游戏节奏和叙事

**可玩性设计原则：**

- **可读性**：玩家应能理解AI行为模式
- **可预测性**：建立玩家对AI行为的预期
- **可反应性**：给玩家响应AI行为的时间
- **渐进挑战**：难度应逐步提升

### 1.3 AI难度曲线设计

**难度曲线类型：**

```
难度
 ↑
 │    ╭────╮        ← 波浪式（推荐）
 │   ╱      ╲    ╭─
 │  ╱        ╲  ╱
 │ ╱          ╲╱
 │╱
 └────────────────→ 进度

难度
 ↑
 │                 ╱ 指数增长（硬核）
 │              ╱
 │           ╱
 │        ╱
 │    ╱
 └────────────────→ 进度

难度
 ↑
 │    ╭──╮
 │   ╱    ╲   ╭─╮   ← 阶梯式（关卡制）
 │  ╱      ╲─╯  ╰─
 │ ╱
 │╱
 └────────────────→ 进度
```

**难度调节参数：**

| 参数 | 低难度 | 高难度 |
|------|--------|--------|
| 反应时间 | 慢（1-2秒） | 快（0.1-0.3秒） |
| 准确度 | 低（50%） | 高（90%+） |
| 视野范围 | 窄 | 广 |
| 资源获取 | 少 | 多 |
| 失误惩罚 | 轻 | 重 |
| 提示频率 | 高 | 低 |

---

## 2. NPC行为系统

### 2.1 有限状态机（FSM）

**概念**：将AI行为建模为有限个状态及其之间的转换。

**结构：**

```
    ┌─────────┐
    │  Idle   │◄────────┐
    └────┬────┘         │
         │ see player   │
         ▼              │
    ┌─────────┐         │
    │  Chase  │─────────┤ lost
    └────┬────┘         │ player
         │ in range     │
         ▼              │
    ┌─────────┐         │
    │ Attack  │─────────┘
    └─────────┘  player dead
```

**优缺点：**

- ✅ 实现简单，易于理解
- ✅ 性能高效
- ✅ 调试方便
- ❌ 状态爆炸问题
- ❌ 难以表达复杂行为
- ❌ 代码重复（类似状态）

**适用场景**：简单敌人、道具、门等交互对象

### 2.2 行为树（Behavior Trees）

**概念**：层次化的任务分解，使用组合节点控制执行流程。

**核心节点类型：**

| 节点类型 | 符号 | 功能 | 返回值 |
|----------|------|------|--------|
| Sequence | → | 顺序执行，失败即停 | 全成功=成功 |
| Selector | ? | 选择执行，成功即停 | 任一成功=成功 |
| Parallel | ⇉ | 并行执行 | 视策略而定 |
| Decorator | ◇ | 修饰子节点 | 转换返回值 |
| Action | □ | 执行动作 | 成功/失败/运行 |
| Condition | ○ | 检查条件 | 成功/失败 |

**示例行为树结构：**

```
                    [Root]
                      │
              [Selector: Combat?]
                 ╱           ╲
           [Sequence]      [Patrol]
          ╱    │     ╲
    [See]  [InRange] [Attack]
              │
           [Chase]
```

**优缺点：**

- ✅ 可视化编辑友好
- ✅ 模块化、可复用
- ✅ 支持中断和恢复
- ✅ 层次结构清晰
- ❌ 学习曲线陡峭
- ❌ 过度设计风险
- ❌ 调试复杂行为困难

**适用场景**：复杂Boss、队友AI、任务系统

### 2.3 GOAP（目标导向行动规划）

**概念**：反向链式推理，从目标状态推导行动计划。

**核心组件：**

1. **世界状态**：键值对表示的环境状态
2. **目标**：期望达到的世界状态条件
3. **动作**：改变世界状态的操作（前置条件+效果）
4. **规划器**：A*算法寻找最优动作序列

**GOAP工作流程：**

```
当前状态 ──► 规划器 ──► 动作序列 ──► 执行
              ▲              │
              └──────────────┘
            (效果反馈更新状态)
```

**动作示例：**

```yaml
动作: 攻击玩家
前置条件:
  - 持有武器: true
  - 距离玩家: < 2m
效果:
  - 玩家生命值: -10
  - 弹药: -1
成本: 5
```

**优缺点：**

- ✅ 高度灵活，无需预设行为
- ✅ 适应动态环境
- ✅ 模块化动作设计
- ❌ 计算开销大
- ❌ 调试困难
- ❌ 设计复杂，需要精细调参

**适用场景**：策略游戏、模拟游戏、复杂决策场景

### 2.4 Utility AI（效用AI）

**概念**：为每个可选动作计算"效用值"，选择最高效用的动作。

**核心公式：**

```
效用 = Σ(因素权重 × 因素评分)

或

效用 = 响应曲线(输入值) × 权重
```

**响应曲线类型：**

```
线性      指数      对数      S型      反S型
 │╲        │╲       │        │╭─╮     ╭─╮│
 │ ╲       │ ╲      │╲       ││ │    │ │ │
 │  ╲      │  ╲     │ ╲      ╰│ │    │ │╯
 │   ╲     │   ╲    │  ╲      │ │    │ │
 └────     └────    └───      ╰─╯    ╰─╯
```

**考虑因素示例（饥饿的NPC）：**

| 动作 | 饥饿度 | 食物距离 | 危险程度 | 总效用 |
|------|--------|----------|----------|--------|
| 吃食物 | 0.9×10 | 0.5×3 | 0.1×-5 | 9.5 |
| 逃跑 | 0.1×2 | - | 0.9×8 | 7.4 |
| 探索 | 0.5×5 | - | 0.5×0 | 2.5 |

**优缺点：**

- ✅ 平滑过渡，行为自然
- ✅ 易于平衡（调权重）
- ✅ 可处理模糊决策
- ❌ 权重调优困难
- ❌ 可能出现意外行为
- ❌ 调试困难

**适用场景**：模拟游戏、RPG决策、生态系统模拟

---

## 3. 决策系统对比

| 系统 | 适用场景 | 复杂度 | 灵活性 | 性能 | 可调试性 |
|------|----------|--------|--------|------|----------|
| **FSM** | 简单敌人、道具 | 低 | 低 | 极高 | 极高 |
| **行为树** | 复杂Boss、队友AI | 中 | 中 | 高 | 高 |
| **GOAP** | 策略游戏、沙盒 | 高 | 高 | 中 | 低 |
| **Utility AI** | 模拟游戏、RPG | 高 | 高 | 中 | 低 |
| **分层FSM** | 中等复杂度NPC | 中 | 中-高 | 高 | 高 |
| **HTN** | RTS、复杂任务 | 高 | 极高 | 中-低 | 中 |

### 选择决策

**选择FSM当：**
- 行为简单且固定
- 性能极度敏感
- 快速原型开发

**选择行为树当：**
- 需要层次化组织
- 行为可模块化复用
- 使用可视化编辑器

**选择GOAP当：**
- 需要自动规划
- 环境动态变化大
- 有大量可能的动作组合

**选择Utility AI当：**
- 需要平滑行为过渡
- 决策基于多个因素权衡
- 需要涌现性行为

---

## 4. Godot实现示例

### 4.1 简单巡逻AI（FSM）

```gdscript
# npc_patrol.gd
class_name PatrolNPC
extends CharacterBody2D

enum State { IDLE, PATROL, CHASE, ATTACK }

@export var patrol_points: Array[Marker2D] = []
@export var move_speed: float = 100.0
@export var chase_speed: float = 200.0
@export var detection_range: float = 200.0
@export var attack_range: float = 50.0

var current_state: State = State.IDLE
var current_point_index: int = 0
var player: Node2D = null
var idle_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D

func _ready():
    # 查找玩家
    player = get_tree().get_first_node_in_group("player")
    _enter_state(State.PATROL)

func _physics_process(delta):
    match current_state:
        State.IDLE:
            _process_idle(delta)
        State.PATROL:
            _process_patrol(delta)
        State.CHASE:
            _process_chase(delta)
        State.ATTACK:
            _process_attack(delta)

func _enter_state(new_state: State):
    current_state = new_state
    match new_state:
        State.IDLE:
            idle_timer = 2.0  # 等待2秒
            velocity = Vector2.ZERO
        State.PATROL:
            pass
        State.CHASE:
            pass
        State.ATTACK:
            _perform_attack()

# ========== 状态处理 ==========

func _process_idle(delta):
    idle_timer -= delta
    
    # 检测玩家
    if _can_see_player():
        _enter_state(State.CHASE)
        return
    
    # 等待结束，继续巡逻
    if idle_timer <= 0:
        _enter_state(State.PATROL)

func _process_patrol(delta):
    # 检测玩家
    if _can_see_player():
        _enter_state(State.CHASE)
        return
    
    if patrol_points.is_empty():
        _enter_state(State.IDLE)
        return
    
    var target = patrol_points[current_point_index]
    var direction = (target.global_position - global_position).normalized()
    velocity = direction * move_speed
    
    # 到达目标点
    if global_position.distance_to(target.global_position) < 10:
        current_point_index = (current_point_index + 1) % patrol_points.size()
        _enter_state(State.IDLE)
    
    move_and_slide()

func _process_chase(delta):
    if player == null:
        _enter_state(State.PATROL)
        return
    
    var distance = global_position.distance_to(player.global_position)
    
    # 进入攻击范围
    if distance < attack_range:
        _enter_state(State.ATTACK)
        return
    
    # 丢失玩家（距离过远）
    if distance > detection_range * 1.5:
        _enter_state(State.PATROL)
        return
    
    var direction = (player.global_position - global_position).normalized()
    velocity = direction * chase_speed
    move_and_slide()

func _process_attack(delta):
    var distance = global_position.distance_to(player.global_position)
    
    # 玩家离开攻击范围
    if distance > attack_range:
        _enter_state(State.CHASE)
        return
    
    # 攻击冷却处理...

# ========== 辅助函数 ==========

func _can_see_player() -> bool:
    if player == null:
        return false
    
    var distance = global_position.distance_to(player.global_position)
    if distance > detection_range:
        return false
    
    # 视线检测
    var space_state = get_world_2d().direct_space_state
    var query = PhysicsRayQueryParameters2D.create(
        global_position, 
        player.global_position,
        1  # 碰撞层
    )
    var result = space_state.intersect_ray(query)
    
    if result.is_empty():
        return true
    
    return result.collider == player

func _perform_attack():
    print("Attack!")
    # 播放攻击动画
    # 造成伤害
    await get_tree().create_timer(0.5).timeout
    _enter_state(State.CHASE)
```

### 4.2 行为树基础结构

```gdscript
# behavior_tree.gd - 行为树基类
class_name BehaviorTree
extends Node

enum Status { SUCCESS, FAILURE, RUNNING }

func tick(actor: Node, blackboard: Dictionary) -> Status:
    push_error("tick() must be implemented")
    return Status.FAILURE

# ========== 组合节点 ==========

class_name BTSequence
extends BehaviorTree

@export var children: Array[BehaviorTree] = []

func tick(actor: Node, blackboard: Dictionary) -> Status:
    for child in children:
        var status = child.tick(actor, blackboard)
        if status == Status.FAILURE:
            return Status.FAILURE
        if status == Status.RUNNING:
            return Status.RUNNING
    return Status.SUCCESS

class_name BTSelector
extends BehaviorTree

@export var children: Array[BehaviorTree] = []

func tick(actor: Node, blackboard: Dictionary) -> Status:
    for child in children:
        var status = child.tick(actor, blackboard)
        if status == Status.SUCCESS:
            return Status.SUCCESS
        if status == Status.RUNNING:
            return Status.RUNNING
    return Status.FAILURE

# ========== 装饰器 ==========

class_name BTInverter
extends BehaviorTree

@export var child: BehaviorTree

func tick(actor: Node, blackboard: Dictionary) -> Status:
    var status = child.tick(actor, blackboard)
    match status:
        Status.SUCCESS: return Status.FAILURE
        Status.FAILURE: return Status.SUCCESS
        _: return status

# ========== 叶子节点 ==========

class_name BTAction
extends BehaviorTree

var action_callable: Callable

func _init(callable: Callable):
    action_callable = callable

func tick(actor: Node, blackboard: Dictionary) -> Status:
    return action_callable.call(actor, blackboard)

class_name BTCondition
extends BehaviorTree

var condition_callable: Callable

func _init(callable: Callable):
    condition_callable = callable

func tick(actor: Node, blackboard: Dictionary) -> Status:
    if condition_callable.call(actor, blackboard):
        return Status.SUCCESS
    return Status.FAILURE
```

### 4.3 行为树使用示例

```gdscript
# enemy_ai.gd
extends CharacterBody2D

var blackboard: Dictionary = {}
var behavior_tree: BehaviorTree

func _ready():
    _build_behavior_tree()

func _physics_process(delta):
    blackboard["delta"] = delta
    behavior_tree.tick(self, blackboard)

func _build_behavior_tree():
    # 创建条件检查
    var can_see_player = BTCondition.new(_check_can_see_player)
    var in_attack_range = BTCondition.new(_check_in_attack_range)
    
    # 创建动作
    var chase_player = BTAction.new(_action_chase)
    var attack_player = BTAction.new(_action_attack)
    var patrol = BTAction.new(_action_patrol)
    
    # 构建行为树：Selector[Sequence[see?, in_range?, attack], chase, patrol]
    var attack_sequence = BTSequence.new()
    attack_sequence.children = [can_see_player, in_attack_range, attack_player]
    
    var chase_sequence = BTSequence.new()
    chase_sequence.children = [can_see_player, chase_player]
    
    var root = BTSelector.new()
    root.children = [attack_sequence, chase_sequence, patrol]
    
    behavior_tree = root

# ========== 条件函数 ==========

func _check_can_see_player(_actor: Node, _blackboard: Dictionary) -> bool:
    var player = get_tree().get_first_node_in_group("player")
    if player == null:
        return false
    
    var distance = global_position.distance_to(player.global_position)
    return distance < 200.0

func _check_in_attack_range(_actor: Node, _blackboard: Dictionary) -> bool:
    var player = get_tree().get_first_node_in_group("player")
    if player == null:
        return false
    
    var distance = global_position.distance_to(player.global_position)
    return distance < 50.0

# ========== 动作函数 ==========

func _action_chase(actor: Node, blackboard: Dictionary) -> int:
    var player = get_tree().get_first_node_in_group("player")
    if player == null:
        return BehaviorTree.Status.FAILURE
    
    var direction = (player.global_position - global_position).normalized()
    velocity = direction * 150.0
    move_and_slide()
    
    return BehaviorTree.Status.RUNNING

func _action_attack(_actor: Node, _blackboard: Dictionary) -> int:
    print("Attacking!")
    # 执行攻击
    return BehaviorTree.Status.SUCCESS

func _action_patrol(actor: Node, blackboard: Dictionary) -> int:
    # 巡逻逻辑
    velocity = Vector2.RIGHT.rotated(Time.get_time_dict_from_system()["second"]) * 50.0
    move_and_slide()
    return BehaviorTree.Status.RUNNING
```

### 4.4 视线检测与追击逻辑

```gdscript
# line_of_sight.gd
class_name LineOfSight
extends Node2D

@export var view_distance: float = 300.0
@export var view_angle: float = 90.0  # 度
@export var view_cone_color: Color = Color(1, 0, 0, 0.3)

var target: Node2D = null
var can_see_target: bool = false

func _ready():
    # 可选：设置目标
    target = get_tree().get_first_node_in_group("player")

func _physics_process(delta):
    if target:
        can_see_target = check_line_of_sight(target)

func check_line_of_sight(target_node: Node2D) -> bool:
    if target_node == null:
        return false
    
    var to_target = target_node.global_position - global_position
    var distance = to_target.length()
    
    # 距离检查
    if distance > view_distance:
        return false
    
    # 角度检查
    var forward = Vector2.RIGHT.rotated(global_rotation)
    var angle_to_target = rad_to_deg(forward.angle_to(to_target))
    
    if abs(angle_to_target) > view_angle / 2.0:
        return false
    
    # 射线检测（障碍物）
    var space_state = get_world_2d().direct_space_state
    var query = PhysicsRayQueryParameters2D.create(
        global_position,
        target_node.global_position,
        1  # 碰撞层掩码
    )
    query.exclude = [get_parent()]  # 排除自身
    
    var result = space_state.intersect_ray(query)
    
    if result.is_empty():
        return true
    
    return result.collider == target_node

func get_predicted_position(target_node: Node2D, time_ahead: float) -> Vector2:
    """预测目标未来位置（用于射击或拦截）"""
    if not target_node is CharacterBody2D:
        return target_node.global_position
    
    var target_body: CharacterBody2D = target_node
    return target_node.global_position + target_body.velocity * time_ahead

func _draw():
    # 绘制视野锥（调试用）
    if Engine.is_editor_hint():
        var points = PackedVector2Array()
        points.append(Vector2.ZERO)
        
        var steps = 20
        var start_angle = -view_angle / 2.0
        var angle_step = view_angle / steps
        
        for i in range(steps + 1):
            var angle = deg_to_rad(start_angle + angle_step * i)
            var point = Vector2.RIGHT.rotated(angle) * view_distance
            points.append(point)
        
        draw_polygon(points, [view_cone_color])
```

---

## 5. 高级话题

### 5.1 群体AI（群集行为）

**Boids算法三大原则：**

1. **分离（Separation）**：避免拥挤
2. **对齐（Alignment）**：与邻居朝向一致
3. **凝聚（Cohesion）**：向群体中心移动

```gdscript
# flock_agent.gd
class_name FlockAgent
extends CharacterBody2D

@export var separation_weight: float = 1.5
@export var alignment_weight: float = 1.0
@export var cohesion_weight: float = 1.0
@export var perception_radius: float = 100.0
@export var max_speed: float = 200.0
@export var max_force: float = 10.0

var flock_mates: Array[FlockAgent] = []

func _physics_process(delta):
    var separation = _calculate_separation()
    var alignment = _calculate_alignment()
    var cohesion = _calculate_cohesion()
    
    var acceleration = separation * separation_weight + \
                       alignment * alignment_weight + \
                       cohesion * cohesion_weight
    
    velocity += acceleration * delta
    velocity = velocity.limit_length(max_speed)
    
    move_and_slide()
    
    # 朝向移动方向
    if velocity.length() > 0.1:
        rotation = velocity.angle()

func _calculate_separation() -> Vector2:
    var steer = Vector2.ZERO
    var count = 0
    
    for mate in flock_mates:
        var distance = global_position.distance_to(mate.global_position)
        if distance > 0 and distance < perception_radius / 2:
            var diff = global_position - mate.global_position
            diff = diff.normalized() / distance  # 距离越近，排斥越强
            steer += diff
            count += 1
    
    if count > 0:
        steer /= count
        steer = steer.normalized() * max_speed - velocity
        steer = steer.limit_length(max_force)
    
    return steer

func _calculate_alignment() -> Vector2:
    var average_velocity = Vector2.ZERO
    var count = 0
    
    for mate in flock_mates:
        if global_position.distance_to(mate.global_position) < perception_radius:
            average_velocity += mate.velocity
            count += 1
    
    if count > 0:
        average_velocity /= count
        average_velocity = average_velocity.normalized() * max_speed
        var steer = average_velocity - velocity
        return steer.limit_length(max_force)
    
    return Vector2.ZERO

func _calculate_cohesion() -> Vector2:
    var center = Vector2.ZERO
    var count = 0
    
    for mate in flock_mates:
        if global_position.distance_to(mate.global_position) < perception_radius:
            center += mate.global_position
            count += 1
    
    if count > 0:
        center /= count
        return _seek(center)
    
    return Vector2.ZERO

func _seek(target: Vector2) -> Vector2:
    var desired = (target - global_position).normalized() * max_speed
    var steer = desired - velocity
    return steer.limit_length(max_force)
```

### 5.2 学习AI（强化学习入门）

**核心概念：**

- **状态（State）**：AI观察到的环境
- **动作（Action）**：AI可以采取的行为
- **奖励（Reward）**：动作的反馈信号
- **策略（Policy）**：状态到动作的映射

**简化Q-Learning示例：**

```gdscript
# q_learning_agent.gd
class_name QLearningAgent
extends Node

var q_table: Dictionary = {}  # 状态 -> {动作: Q值}
@export var learning_rate: float = 0.1
@export var discount_factor: float = 0.9
@export var epsilon: float = 0.1  # 探索率

var last_state = null
var last_action = null

func get_action(state: String, possible_actions: Array[String]) -> String:
    # 初始化Q表
    if not q_table.has(state):
        q_table[state] = {}
        for action in possible_actions:
            q_table[state][action] = 0.0
    
    # ε-贪婪策略
    if randf() < epsilon:
        return possible_actions.pick_random()
    
    # 选择最大Q值的动作
    var max_q = -INF
    var best_action = possible_actions[0]
    
    for action in possible_actions:
        var q = q_table[state].get(action, 0.0)
        if q > max_q:
            max_q = q
            best_action = action
    
    last_state = state
    last_action = best_action
    
    return best_action

func update_reward(reward: float, new_state: String):
    if last_state == null or last_action == null:
        return
    
    var old_q = q_table[last_state][last_action]
    var max_future_q = 0.0
    
    if q_table.has(new_state):
        max_future_q = q_table[new_state].values().max()
    
    # Q值更新公式
    var new_q = old_q + learning_rate * (reward + discount_factor * max_future_q - old_q)
    q_table[last_state][last_action] = new_q
```

**游戏AI中的强化学习应用：**

- **动态难度调整**：根据玩家表现调整AI行为
- **对手建模**：学习玩家习惯并针对性应对
- **程序化内容生成**：生成适应玩家风格的关卡

### 5.3 AI难度自适应

**动态难度调整（DDA）策略：**

```gdscript
# difficulty_manager.gd
class_name DifficultyManager
extends Node

enum Difficulty { EASY, NORMAL, HARD, EXPERT }

@export var adjustment_interval: float = 30.0  # 评估间隔（秒）
@export var performance_window: int = 10  # 性能记录窗口大小

var current_difficulty: Difficulty = Difficulty.NORMAL
var player_performance_history: Array[float] = []
var timer: float = 0.0

# 性能指标
var player_health_ratio: float = 1.0
var player_accuracy: float = 0.5
var player_progress_speed: float = 1.0

func _process(delta):
    timer += delta
    if timer >= adjustment_interval:
        _evaluate_and_adjust()
        timer = 0.0

func record_event(event_type: String, value: float):
    match event_type:
        "damage_taken":
            player_health_ratio = value
        "hit_ratio":
            player_accuracy = value
        "level_completion_time":
            # 根据预期时间计算进度速度
            player_progress_speed = 100.0 / value

func _evaluate_and_adjust():
    # 计算综合性能得分
    var performance_score = _calculate_performance()
    player_performance_history.append(performance_score)
    
    if player_performance_history.size() > performance_window:
        player_performance_history.pop_front()
    
    # 基于平均性能调整难度
    var avg_performance = _get_average_performance()
    
    if avg_performance > 0.8:
        _increase_difficulty()
    elif avg_performance < 0.3:
        _decrease_difficulty()
    
    print("Performance: ", avg_performance, " | Difficulty: ", Difficulty.keys()[current_difficulty])

func _calculate_performance() -> float:
    # 加权计算性能指标
    return player_health_ratio * 0.4 + player_accuracy * 0.3 + player_progress_speed * 0.3

func _get_average_performance() -> float:
    if player_performance_history.is_empty():
        return 0.5
    
    var sum = 0.0
    for score in player_performance_history:
        sum += score
    return sum / player_performance_history.size()

func _increase_difficulty():
    if current_difficulty < Difficulty.EXPERT:
        current_difficulty += 1
        _apply_difficulty_settings()

func _decrease_difficulty():
    if current_difficulty > Difficulty.EASY:
        current_difficulty -= 1
        _apply_difficulty_settings()

func _apply_difficulty_settings():
    # 应用到所有AI
    var ai_agents = get_tree().get_nodes_in_group("ai")
    for agent in ai_agents:
        if agent.has_method("set_difficulty"):
            agent.set_difficulty(current_difficulty)

# 难度参数获取
func get_ai_reaction_time() -> float:
    match current_difficulty:
        Difficulty.EASY: return 1.5
        Difficulty.NORMAL: return 0.8
        Difficulty.HARD: return 0.3
        Difficulty.EXPERT: return 0.1
    return 0.8

func get_ai_accuracy() -> float:
    match current_difficulty:
        Difficulty.EASY: return 0.4
        Difficulty.NORMAL: return 0.6
        Difficulty.HARD: return 0.8
        Difficulty.EXPERT: return 0.95
    return 0.6
```

**隐式DDA技术（玩家不易察觉）：**

- **橡皮筋效应**：落后时给予优势道具
- **微妙参数调整**：AI准确度±10%变化
- **资源投放**：根据表现调整补给品位置

---

## 6. 参考资料

### 书籍

- **《AI Game Programming Wisdom》系列** - 游戏AI编程经典
- **《Programming Game AI by Example》** - Mat Buckland
- **《Artificial Intelligence for Games》** - Ian Millington

### 在线资源

- **GDC Vault** - 游戏开发者大会演讲
- **Game AI Pro** - 免费在线书籍
- **AIGameDev.com** - 游戏AI社区

### GitHub项目

- **Godot AI框架**：各种Godot AI实现参考
- **Unity ML-Agents**：强化学习工具包
- **Recast & Detour**：导航网格生成

### 论文与文章

- "Boids: Background and Update" - Craig Reynolds
- "Planning in Games" - 游戏规划算法综述
- "The Use of Utility in AI" - Utility AI理论

---

## 工具推荐

| 工具 | 用途 | 平台 |
|------|------|------|
| **LimboAI** | Godot行为树编辑器 | Godot |
| **LogicDriver** | UE可视化行为树 | Unreal |
| **NodeCanvas** | Unity行为树/状态机 | Unity |
| **A* Pathfinding** | 寻路算法 | 通用 |

---

> 💡 **提示**：优秀的游戏AI不是追求"智能"，而是追求"有趣"。始终从玩家体验出发设计AI行为。
