extends CharacterBody2D

# 玩家控制器 - Godot 4.6.1 版本
# 区域控制Roguelike动作游戏

class_name Player

signal health_changed(new_health, max_health)
signal player_died

# 移动参数
@export var move_speed: float = 200.0
@export var dash_speed: float = 600.0
@export var dash_duration: float = 0.2
@export var dash_cooldown: float = 3.0

# 生命值
@export var max_health: int = 100
var health: int = max_health

# 状态
var is_dashing: bool = false
var can_dash: bool = true
var dash_timer: float = 0.0
var dash_cooldown_timer: float = 0.0
var is_shielded: bool = false

# 网格位置
var current_grid_pos: Vector2i = Vector2i.ZERO

# 组件引用
@onready var grid_system = get_node("/root/Main/GridSystem")
@onready var game_manager = get_node("/root/Main/GameManager")
@onready var skill_system = $SkillSystem
@onready var sprite = $Sprite2D
@onready var collision = $CollisionShape2D

func _ready():
	# 设置初始位置
	position = grid_system.grid_to_world(Vector2i(2, 2))
	update_grid_position()
	health_changed.emit(health, max_health)

func _physics_process(delta):
	if is_dashing:
		handle_dash(delta)
	else:
		handle_movement(delta)
		handle_dash_input(delta)
		handle_skill_input()
	
	# 更新网格位置
	update_grid_position()

func handle_movement(delta):
	var input_dir = Vector2.ZERO
	
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1
	if Input.is_action_pressed("move_up"):
		input_dir.y -= 1
	if Input.is_action_pressed("move_down"):
		input_dir.y += 1
	
	input_dir = input_dir.normalized()
	velocity = input_dir * move_speed
	
	# 尝试移动
	var collision_info = move_and_collide(velocity * delta)
	
	# 占领当前格子
	claim_current_cell()

func handle_dash_input(delta):
	if dash_cooldown_timer > 0:
		dash_cooldown_timer -= delta
		if dash_cooldown_timer <= 0:
			can_dash = true
	
	if Input.is_action_just_pressed("dash") and can_dash:
		start_dash()

func handle_skill_input():
	if Input.is_action_just_pressed("skill_q"):
		skill_system.use_skill("Q")
	if Input.is_action_just_pressed("skill_e"):
		skill_system.use_skill("E")
	if Input.is_action_just_pressed("skill_r"):
		skill_system.use_skill("R")

func start_dash():
	is_dashing = true
	can_dash = false
	dash_timer = dash_duration
	dash_cooldown_timer = dash_cooldown
	
	# 根据当前移动方向冲刺
	var input_dir = Vector2.ZERO
	if Input.is_action_pressed("move_left"):
		input_dir.x -= 1
	if Input.is_action_pressed("move_right"):
		input_dir.x += 1
	if Input.is_action_pressed("move_up"):
		input_dir.y -= 1
	if Input.is_action_pressed("move_down"):
		input_dir.y += 1
	
	if input_dir == Vector2.ZERO:
		input_dir = Vector2.RIGHT  # 默认向右冲刺
	
	input_dir = input_dir.normalized()
	velocity = input_dir * dash_speed
	
	# 视觉反馈
	if sprite:
		sprite.modulate = Color(0.5, 1.0, 1.0, 0.7)

func handle_dash(delta):
	dash_timer -= delta
	move_and_slide()
	
	if dash_timer <= 0:
		end_dash()

func end_dash():
	is_dashing = false
	velocity = Vector2.ZERO
	
	# 恢复视觉
	if sprite:
		sprite.modulate = Color.WHITE

func update_grid_position():
	if grid_system:
		var new_grid_pos = grid_system.world_to_grid(position)
		if new_grid_pos != current_grid_pos:
			current_grid_pos = new_grid_pos

func claim_current_cell():
	if grid_system:
		if grid_system.claim_cell(current_grid_pos.x, current_grid_pos.y):
			# 成功占领，增加分数
			if game_manager:
				game_manager.add_score(10)

func take_damage(damage: int):
	if is_dashing or is_shielded:
		return  # 冲刺或护盾时无敌
	
	health -= damage
	health_changed.emit(health, max_health)
	
	# 视觉反馈
	if sprite:
		sprite.modulate = Color(1.0, 0.3, 0.3, 1.0)
		await get_tree().create_timer(0.1).timeout
		sprite.modulate = Color.WHITE
	
	if health <= 0:
		die()

func die():
	player_died.emit()
	if game_manager:
		game_manager.trigger_game_over()
	queue_free()

func heal(amount: int):
	health = min(health + amount, max_health)
	health_changed.emit(health, max_health)
