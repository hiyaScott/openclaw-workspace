extends Node2D

# 游戏配置
const WIN_OCCUPANCY_RATE = 0.80  # 80%占领率通关
const ENEMY_SPAWN_INTERVAL = 10.0  # 敌人生成间隔（秒）
const MAX_ENEMIES = 5  # 最大敌人数

# 游戏状态
enum GameState {
	PLAYING,
	WON,
	LOST
}
var current_state = GameState.PLAYING

# 计时器
var enemy_spawn_timer: float = 0.0
var game_time: float = 0.0

# 引用
@onready var grid_system = $GridSystem
@onready var player = $Player
@onready var ui = $UI
@onready var enemy_container = $EnemyContainer

func _ready():
	# 连接信号
	player.health_changed.connect(_on_player_health_changed)
	player.player_died.connect(_on_player_died)
	
	# 初始化UI
	update_occupancy_display()
	
	# 生成初始敌人
	spawn_enemy()
	spawn_enemy()

func _process(delta):
	if current_state != GameState.PLAYING:
		return
	
	game_time += delta
	
	# 敌人生成计时
	enemy_spawn_timer -= delta
	if enemy_spawn_timer <= 0:
		enemy_spawn_timer = ENEMY_SPAWN_INTERVAL
		if enemy_container.get_child_count() < MAX_ENEMIES:
			spawn_enemy()

func spawn_enemy():
	var enemy_scene = load("res://scenes/enemy.tscn")
	if enemy_scene:
		var enemy = enemy_scene.instantiate()
		enemy_container.add_child(enemy)
		enemy.enemy_died.connect(_on_enemy_died)

func on_cell_occupied():
	update_occupancy_display()
	check_win_condition()

func update_occupancy_display():
	var occupancy_rate = grid_system.get_occupancy_rate()
	ui.update_occupancy(occupancy_rate, WIN_OCCUPANCY_RATE)

func check_win_condition():
	var occupancy_rate = grid_system.get_occupancy_rate()
	if occupancy_rate >= WIN_OCCUPANCY_RATE:
		win_game()

func win_game():
	current_state = GameState.WON
	ui.show_game_won(game_time)

func lose_game():
	current_state = GameState.LOST
	ui.show_game_over()

func reset_game():
	current_state = GameState.PLAYING
	game_time = 0.0
	enemy_spawn_timer = 0.0
	
	# 重置网格
	grid_system.initialize_grid()
	
	# 重置玩家
	player.reset()
	grid_system.occupy_cell(player.grid_pos.x, player.grid_pos.y)
	
	# 清除所有敌人
	for enemy in enemy_container.get_children():
		enemy.queue_free()
	
	# 生成初始敌人
	spawn_enemy()
	spawn_enemy()
	
	# 更新UI
	update_occupancy_display()
	ui.hide_game_over()

func _on_player_health_changed(new_health: int, max_health: int):
	ui.update_health(new_health, max_health)

func _on_player_died():
	lose_game()

func _on_enemy_died(enemy: Node2D):
	# 敌人死亡处理（可以在这里添加得分等）
	pass

func _input(event):
	if event.is_action_pressed("restart"):
		if current_state == GameState.WON or current_state == GameState.LOST:
			reset_game()
