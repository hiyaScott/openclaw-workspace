extends CharacterBody2D

# 玩家配置
const MOVE_SPEED = 4.0  # 格/秒
const CELL_SIZE = 50

# 玩家状态
var grid_pos: Vector2i = Vector2i(6, 6)  # 起始位置（中心）
var max_health: int = 3
var current_health: int = 3
var is_alive: bool = true

# 移动相关
var target_world_pos: Vector2
var is_moving: bool = false
var move_cooldown: float = 0.0

# 引用
@onready var grid_system = get_node("../GridSystem")
@onready var game_manager = get_node("../GameManager")

signal health_changed(new_health: int, max_health: int)
signal player_died

func _ready():
	# 设置初始位置
	update_position_from_grid()
	target_world_pos = position
	
	# 占领起始位置
	grid_system.occupy_cell(grid_pos.x, grid_pos.y)
	
	# 发送初始生命值
	health_changed.emit(current_health, max_health)

func _process(delta):
	if not is_alive:
		return
	
	# 处理移动
	if is_moving:
		var direction = (target_world_pos - position).normalized()
		var distance = position.distance_to(target_world_pos)
		var move_distance = MOVE_SPEED * CELL_SIZE * delta
		
		if distance <= move_distance:
			position = target_world_pos
			is_moving = false
			# 移动完成后占领格子
			var occupied = grid_system.occupy_cell(grid_pos.x, grid_pos.y)
			if occupied:
				game_manager.on_cell_occupied()
		else:
			position += direction * move_distance
	else:
		# 处理输入
		handle_input()

func handle_input():
	var input_dir = Vector2i.ZERO
	
	if Input.is_action_just_pressed("move_left"):
		input_dir.x = -1
	elif Input.is_action_just_pressed("move_right"):
		input_dir.x = 1
	elif Input.is_action_just_pressed("move_up"):
		input_dir.y = -1
	elif Input.is_action_just_pressed("move_down"):
		input_dir.y = 1
	
	if input_dir != Vector2i.ZERO:
		try_move(input_dir)

func try_move(direction: Vector2i):
	var new_pos = grid_pos + direction
	
	# 检查边界
	if not grid_system.is_in_bounds(new_pos.x, new_pos.y):
		return
	
	# 检查障碍物
	if grid_system.get_cell(new_pos.x, new_pos.y) == grid_system.CellState.BLOCKED:
		return
	
	# 执行移动
	grid_pos = new_pos
	target_world_pos = grid_system.grid_to_world(grid_pos)
	is_moving = true

func update_position_from_grid():
	position = grid_system.grid_to_world(grid_pos)

func take_damage(amount: int):
	if not is_alive:
		return
	
	current_health -= amount
	current_health = max(0, current_health)
	
	# 受伤闪烁效果
	modulate = Color(1, 0.3, 0.3, 1)
	await get_tree().create_timer(0.1).timeout
	modulate = Color(1, 1, 1, 1)
	
	health_changed.emit(current_health, max_health)
	
	if current_health <= 0:
		die()

func die():
	is_alive = false
	player_died.emit()

func reset():
	current_health = max_health
	is_alive = true
	grid_pos = Vector2i(6, 6)
	update_position_from_grid()
	target_world_pos = position
	is_moving = false
	health_changed.emit(current_health, max_health)

func _draw():
	# 绘制玩家（菱形）
	var size = 15
	var points = PackedVector2Array([
		Vector2(0, -size),
		Vector2(size, 0),
		Vector2(0, size),
		Vector2(-size, 0)
	])
	draw_colored_polygon(points, Color(0.0, 1.0, 0.8, 1.0))
	
	# 内部发光效果
	var inner_size = 8
	var inner_points = PackedVector2Array([
		Vector2(0, -inner_size),
		Vector2(inner_size, 0),
		Vector2(0, inner_size),
		Vector2(-inner_size, 0)
	])
	draw_colored_polygon(inner_points, Color(0.5, 1.0, 0.9, 1.0))
