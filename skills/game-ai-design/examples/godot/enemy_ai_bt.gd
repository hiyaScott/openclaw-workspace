# 行为树使用示例 - 敌人AI
# 文件：enemy_ai.gd
# 适用于：Godot 4.x

extends CharacterBody2D

var blackboard: Dictionary = {}
var behavior_tree: BehaviorTree

@export var move_speed: float = 100.0
@export var chase_speed: float = 200.0
@export var attack_range: float = 50.0
@export var detection_range: float = 200.0

func _ready():
	_build_behavior_tree()

func _physics_process(delta):
	blackboard["delta"] = delta
	blackboard["self"] = self
	if behavior_tree:
		behavior_tree.tick(self, blackboard)

func _build_behavior_tree():
	# 创建条件检查
	var can_see_player = BTCondition.new(_check_can_see_player)
	var in_attack_range = BTCondition.new(_check_in_attack_range)
	var health_low = BTCondition.new(_check_health_low)
	
	# 创建动作
	var chase_player = BTAction.new(_action_chase)
	var attack_player = BTAction.new(_action_attack)
	var patrol = BTAction.new(_action_patrol)
	var flee = BTAction.new(_action_flee)
	var wait = BTWait.new()
	wait.wait_time = 1.0
	
	# 构建行为树结构：
	# Selector[
	#   Sequence[health_low?, flee],      # 优先逃跑
	#   Sequence[see?, in_range?, attack], # 攻击
	#   Sequence[see?, chase],             # 追击
	#   Selector[patrol, wait]             # 巡逻或等待
	# ]
	
	var flee_sequence = BTSequence.new()
	flee_sequence.children = [health_low, flee]
	
	var attack_sequence = BTSequence.new()
	attack_sequence.children = [can_see_player, in_attack_range, attack_player]
	
	var chase_sequence = BTSequence.new()
	chase_sequence.children = [can_see_player, chase_player]
	
	var patrol_fallback = BTSelector.new()
	patrol_fallback.children = [patrol, wait]
	
	var root = BTSelector.new()
	root.children = [flee_sequence, attack_sequence, chase_sequence, patrol_fallback]
	
	behavior_tree = root

# ========== 条件函数 ==========

func _check_can_see_player(_actor: Node, _blackboard: Dictionary) -> bool:
	var player = get_tree().get_first_node_in_group("player")
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
		1
	)
	query.exclude = [self]
	var result = space_state.intersect_ray(query)
	
	if result.is_empty():
		return true
	return result.collider == player

func _check_in_attack_range(_actor: Node, _blackboard: Dictionary) -> bool:
	var player = get_tree().get_first_node_in_group("player")
	if player == null:
		return false
	
	var distance = global_position.distance_to(player.global_position)
	return distance < attack_range

func _check_health_low(_actor: Node, _blackboard: Dictionary) -> bool:
	# 假设有health属性
	# return health < max_health * 0.2
	return false  # 占位

# ========== 动作函数 ==========

func _action_chase(actor: Node, _blackboard: Dictionary) -> int:
	var player = get_tree().get_first_node_in_group("player")
	if player == null:
		return BehaviorTree.Status.FAILURE
	
	var direction = (player.global_position - global_position).normalized()
	velocity = direction * chase_speed
	actor.move_and_slide()
	
	# 朝向目标
	actor.rotation = direction.angle()
	
	return BehaviorTree.Status.RUNNING

func _action_attack(_actor: Node, _blackboard: Dictionary) -> int:
	print("Enemy attacks!")
	# 播放攻击动画
	# 造成伤害
	# await动画完成
	return BehaviorTree.Status.SUCCESS

func _action_flee(actor: Node, _blackboard: Dictionary) -> int:
	var player = get_tree().get_first_node_in_group("player")
	if player == null:
		return BehaviorTree.Status.FAILURE
	
	# 逃离玩家
	var direction = (global_position - player.global_position).normalized()
	velocity = direction * chase_speed * 1.2  # 逃跑更快
	actor.move_and_slide()
	actor.rotation = direction.angle()
	
	return BehaviorTree.Status.RUNNING

# 巡逻状态
var patrol_points: Array[Vector2] = []
var current_patrol_index: int = 0
var patrol_wait_time: float = 0.0

func _action_patrol(actor: Node, blackboard: Dictionary) -> int:
	# 初始化巡逻点（只在第一次）
	if patrol_points.is_empty():
		# 在周围生成巡逻点
		for i in range(4):
			var angle = i * PI / 2
			patrol_points.append(global_position + Vector2.RIGHT.rotated(angle) * 100)
	
	if patrol_points.is_empty():
		return BehaviorTree.Status.FAILURE
	
	var target = patrol_points[current_patrol_index]
	var distance = global_position.distance_to(target)
	
	if distance < 10:
		# 到达巡逻点，等待一下
		patrol_wait_time += blackboard.get("delta", 0.0)
		if patrol_wait_time > 1.0:
			patrol_wait_time = 0.0
			current_patrol_index = (current_patrol_index + 1) % patrol_points.size()
		velocity = Vector2.ZERO
	else:
		var direction = (target - global_position).normalized()
		velocity = direction * move_speed
		actor.rotation = direction.angle()
	
	actor.move_and_slide()
	return BehaviorTree.Status.RUNNING

# ========== 调试 ==========

func _draw():
	if OS.is_debug_build():
		# 绘制检测范围
		draw_arc(Vector2.ZERO, detection_range, 0, TAU, 32, Color.red)
		draw_arc(Vector2.ZERO, attack_range, 0, TAU, 32, Color.orange)
