# NPC巡逻AI（有限状态机实现）
# 文件：npc_patrol.gd
# 适用于：Godot 4.x

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

# ========== 调试绘制 ==========

func _draw():
	if Engine.is_editor_hint() or OS.is_debug_build():
		# 绘制检测范围
		draw_circle(Vector2.ZERO, detection_range, Color(1, 0, 0, 0.1))
		# 绘制攻击范围
		draw_circle(Vector2.ZERO, attack_range, Color(1, 0.5, 0, 0.2))
		# 绘制当前状态
		draw_string(get_theme_font(""), Vector2(0, -30), State.keys()[current_state], HORIZONTAL_ALIGNMENT_CENTER)
