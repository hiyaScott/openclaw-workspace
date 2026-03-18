extends CharacterBody2D

# 敌人 - Godot 4.6.1 版本
# 基础敌人类，包含AI行为

class_name Enemy

signal enemy_died(enemy)

# 敌人属性
@export var move_speed: float = 80.0
@export var health: int = 30
@export var damage: int = 10
@export var score_value: int = 50

# 状态
var is_alive: bool = true
var is_in_dominion: bool = false

# 组件引用
@onready var grid_system = get_node("/root/Main/GridSystem")
@onready var player = get_node("/root/Main/Player")
@onready var sprite = $Sprite2D
@onready var collision = $CollisionShape2D

func _ready():
	# 随机化外观
	if sprite:
		sprite.modulate = Color(0.9, 0.3, 0.2, 1.0)

func _physics_process(delta):
	if not is_alive:
		return
	
	if not player:
		return
	
	# AI行为
	var direction = calculate_move_direction()
	velocity = direction * move_speed
	
	# 检查是否在玩家领地内
	check_dominion_status()
	
	move_and_slide()

func calculate_move_direction() -> Vector2:
	if not player:
		return Vector2.ZERO
	
	# 基础AI：向玩家移动
	var direction = (player.position - position).normalized()
	
	# 如果在领地内，尝试逃离
	if is_in_dominion:
		var grid_pos = grid_system.world_to_grid(position)
		var player_grid_pos = grid_system.world_to_grid(player.position)
		
		# 寻找最近的非领地格子
		var escape_dir = Vector2.ZERO
		var best_dist = INF
		
		for dx in range(-2, 3):
			for dy in range(-2, 3):
				var check_x = grid_pos.x + dx
				var check_y = grid_pos.y + dy
				
				if grid_system.is_valid_cell(check_x, check_y):
					if grid_system.get_cell(check_x, check_y) != grid_system.CellState.DOMINION:
						var world_pos = grid_system.grid_to_world(Vector2i(check_x, check_y))
						var dist = position.distance_to(world_pos)
						if dist < best_dist:
							best_dist = dist
							escape_dir = (world_pos - position).normalized()
		
		if escape_dir != Vector2.ZERO:
			direction = escape_dir
	
	return direction

func check_dominion_status():
	if not grid_system:
		return
	
	var grid_pos = grid_system.world_to_grid(position)
	var cell_state = grid_system.get_cell(grid_pos.x, grid_pos.y)
	
	var was_in_dominion = is_in_dominion
	is_in_dominion = (cell_state == grid_system.CellState.DOMINION)
	
	if is_in_dominion:
		# 在领地内受到伤害
		var dominion_damage = 5 * get_process_delta_time()
		take_damage(dominion_damage)
		
		# 视觉反馈
		if sprite:
			sprite.modulate = Color(0.9, 0.5, 0.5, 0.7)
	else:
		# 恢复正常
		if sprite:
			sprite.modulate = Color(0.9, 0.3, 0.2, 1.0)

func take_damage(amount: float):
	health -= int(amount)
	
	if health <= 0:
		die()

func die():
	if not is_alive:
		return
	
	is_alive = false
	enemy_died.emit(self)
	
	# 死亡动画效果
	if sprite:
		var tween = create_tween()
		tween.tween_property(sprite, "scale", Vector2.ZERO, 0.3)
		tween.tween_callback(queue_free)
	else:
		queue_free()

func _on_body_entered(body):
	if body is Player:
		body.take_damage(damage)
