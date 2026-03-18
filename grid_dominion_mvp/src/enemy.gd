extends CharacterBody2D

# 敌人配置
const MOVE_SPEED = 2.5  # 格/秒，比玩家慢
const CELL_SIZE = 50
const MAX_HEALTH = 30
const TERRITORY_DAMAGE_PER_SECOND = 5.0

# 敌人状态
var grid_pos: Vector2i
var health: float = MAX_HEALTH
var is_alive: bool = true

# 移动相关
var target_world_pos: Vector2
var is_moving: bool = false
var move_timer: float = 0.0
var path_update_timer: float = 0.0

# AI状态
enum AIState {
	IDLE,
	CHASE
}
var current_state = AIState.IDLE

# 引用
@onready var grid_system = get_node("../GridSystem")
@onready var player = get_node("../Player")
@onready var game_manager = get_node("../GameManager")

signal enemy_died(enemy: Node2D)

func _ready():
	# 设置初始位置（随机生成在远离玩家的位置）
	spawn_at_safe_location()
	
	# 更新世界位置
	update_position_from_grid()
	target_world_pos = position

func spawn_at_safe_location():
	var attempts = 0
	var max_attempts = 100
	
	while attempts < max_attempts:
		var x = randi() % grid_system.GRID_WIDTH
		var y = randi() % grid_system.GRID_HEIGHT
		
		# 确保距离玩家足够远（至少5格）
		var dist_to_player = abs(x - player.grid_pos.x) + abs(y - player.grid_pos.y)
		
		if dist_to_player >= 5 and grid_system.get_cell(x, y) != grid_system.CellState.BLOCKED:
			grid_pos = Vector2i(x, y)
			return
		
		attempts += 1
	
	# 如果找不到安全位置，使用角落
	grid_pos = Vector2i(0, 0)

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
		else:
			position += direction * move_distance
	else:
		# 更新AI
		update_ai(delta)
	
	# 检查领地伤害
	check_territory_damage(delta)
	
	# 检查与玩家碰撞
	check_player_collision()

func update_ai(delta):
	path_update_timer -= delta
	
	if path_update_timer <= 0:
		path_update_timer = 0.5  # 每0.5秒更新一次路径
		
		# 简单的追踪AI：向玩家移动
		var direction = get_direction_to_player()
		
		if direction != Vector2i.ZERO:
			try_move(direction)

func get_direction_to_player() -> Vector2i:
	var dx = player.grid_pos.x - grid_pos.x
	var dy = player.grid_pos.y - grid_pos.y
	
	# 优先移动距离更大的轴
	if abs(dx) > abs(dy):
		return Vector2i(sign(dx), 0)
	elif abs(dy) > 0:
		return Vector2i(0, sign(dy))
	
	return Vector2i.ZERO

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

func check_territory_damage(delta):
	if grid_system.get_cell(grid_pos.x, grid_pos.y) == grid_system.CellState.OWNED:
		# 在玩家领地内受到伤害
		take_damage(TERRITORY_DAMAGE_PER_SECOND * delta)

func check_player_collision():
	if grid_pos == player.grid_pos:
		# 碰到玩家，造成伤害
		if player.is_alive:
			player.take_damage(1)
			# 敌人也会受到反伤
			take_damage(10)

func take_damage(amount: float):
	if not is_alive:
		return
	
	health -= amount
	
	# 受伤闪烁效果
	modulate = Color(1, 0.5, 0.5, 1)
	await get_tree().create_timer(0.05).timeout
	modulate = Color(1, 1, 1, 1)
	
	if health <= 0:
		die()

func die():
	is_alive = false
	enemy_died.emit(self)
	queue_free()

func update_position_from_grid():
	position = grid_system.grid_to_world(grid_pos)

func _draw():
	# 绘制敌人（圆形扫描器）
	var radius = 12
	draw_circle(Vector2.ZERO, radius, Color(1.0, 0.3, 0.2, 1.0))
	
	# 扫描线效果
	var time_dict = Time.get_time_dict_from_system()
	var time = time_dict["second"] + time_dict["minute"] * 60
	var angle = fmod(time * 2.0, PI * 2)
	var line_end = Vector2(cos(angle), sin(angle)) * radius
	draw_line(Vector2.ZERO, line_end, Color(1.0, 0.8, 0.0, 0.8), 2.0)
	
	# 内部核心
	draw_circle(Vector2.ZERO, 5, Color(1.0, 0.6, 0.0, 1.0))
	
	# 生命值指示（当受伤时）
	if health < MAX_HEALTH:
		var health_percent = health / MAX_HEALTH
		var bar_width = 20
		var bar_height = 3
		var bar_pos = Vector2(-bar_width / 2, -radius - 8)
		
		draw_rect(Rect2(bar_pos, Vector2(bar_width, bar_height)), Color(0.3, 0.3, 0.3, 1.0))
		draw_rect(Rect2(bar_pos, Vector2(bar_width * health_percent, bar_height)), Color(0.0, 1.0, 0.0, 1.0))
