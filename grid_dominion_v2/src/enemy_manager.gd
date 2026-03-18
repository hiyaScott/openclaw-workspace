extends Node2D

# 敌人管理器 - Godot 4.6.1 版本
# 管理敌人的生成、行为和AI

class_name EnemyManager

signal enemy_died(position, score_value)

# 敌人预制体
var enemy_scene = preload("res://scenes/enemy.tscn")

# 生成配置
@export var max_enemies: int = 20
@export var spawn_margin: float = 100.0

# 当前敌人列表
var enemies: Array = []

# 组件引用
@onready var grid_system = get_node("/root/Main/GridSystem")
@onready var player = get_node("/root/Main/Player")

func _ready():
	# 初始生成一些敌人
	spawn_initial_enemies()

func spawn_initial_enemies():
	var initial_count = 5
	for i in range(initial_count):
		spawn_enemy()

func spawn_enemy():
	if enemies.size() >= max_enemies:
		return
	
	if not enemy_scene:
		return
	
	var enemy = enemy_scene.instantiate()
	
	# 在远离玩家的位置生成
	var spawn_pos = get_random_spawn_position()
	enemy.position = spawn_pos
	
	# 连接信号
	enemy.enemy_died.connect(_on_enemy_died)
	
	add_child(enemy)
	enemies.append(enemy)

func get_random_spawn_position() -> Vector2:
	if not grid_system or not player:
		return Vector2.ZERO
	
	var attempts = 0
	var spawn_pos = Vector2.ZERO
	
	while attempts < 10:
		# 随机选择一个网格位置
		var gx = randi() % (grid_system.grid_width - 2) + 1
		var gy = randi() % (grid_system.grid_height - 2) + 1
		
		spawn_pos = grid_system.grid_to_world(Vector2i(gx, gy))
		
		# 确保距离玩家足够远
		if spawn_pos.distance_to(player.position) > 200.0:
			break
		
		attempts += 1
	
	return spawn_pos

func spawn_wave(difficulty_multiplier: float):
	var wave_size = int(3 * difficulty_multiplier)
	for i in range(wave_size):
		spawn_enemy()

func _on_enemy_died(enemy):
	enemies.erase(enemy)
	enemy_died.emit(enemy.position, enemy.score_value)
	
	# 通知游戏管理器增加分数
	var game_manager = get_node_or_null("/root/Main/GameManager")
	if game_manager:
		game_manager.add_score(enemy.score_value)

func get_nearest_enemy(pos: Vector2) -> Node2D:
	var nearest = null
	var min_dist = INF
	
	for enemy in enemies:
		var dist = enemy.position.distance_to(pos)
		if dist < min_dist:
			min_dist = dist
			nearest = enemy
	
	return nearest
