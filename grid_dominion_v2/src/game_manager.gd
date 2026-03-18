extends Node

# 游戏管理器 - 核心游戏逻辑
# 管理游戏状态、分数、关卡进度

signal game_over
signal level_complete
signal score_changed(new_score)
signal dominion_changed(percentage)

# 游戏状态
enum GameState { PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE }
var current_state: GameState = GameState.PLAYING

# 游戏数据
var score: int = 0
var current_level: int = 1
var dominion_percentage: float = 0.0
var target_dominion: float = 80.0  # 通关需要80%占领

# 时间控制
var game_time: float = 0.0
var enemy_spawn_timer: float = 0.0
var enemy_spawn_interval: float = 30.0  # 每30秒生成一波敌人

# 难度缩放
var difficulty_multiplier: float = 1.0

func _ready():
	pass

func _process(delta):
	if current_state != GameState.PLAYING:
		return
	
	game_time += delta
	enemy_spawn_timer += delta
	
	# 每30秒生成一波敌人
	if enemy_spawn_timer >= enemy_spawn_interval:
		enemy_spawn_timer = 0
		spawn_enemy_wave()

func initialize_game():
	print("游戏初始化 - 关卡 ", current_level)
	score = 0
	game_time = 0.0
	dominion_percentage = 0.0
	current_state = GameState.PLAYING
	
	# 通知UI更新
	score_changed.emit(score)
	dominion_changed.emit(dominion_percentage)

func update_dominion_percentage(percentage: float):
	dominion_percentage = percentage
	dominion_changed.emit(dominion_percentage)
	
	# 检查通关条件
	if dominion_percentage >= target_dominion:
		level_cleared()

func add_score(points: int):
	score += points
	score_changed.emit(score)

func level_cleared():
	if current_state == GameState.PLAYING:
		current_state = GameState.LEVEL_COMPLETE
		level_complete.emit()
		print("关卡完成！占领率: ", dominion_percentage, "%")

func trigger_game_over():
	if current_state == GameState.PLAYING:
		current_state = GameState.GAME_OVER
		game_over.emit()
		print("游戏结束！存活时间: ", game_time, "秒")

func spawn_enemy_wave():
	# 通知敌人生成器生成一波敌人
	var enemy_manager = get_node_or_null("/root/Main/EnemyManager")
	if enemy_manager:
		enemy_manager.spawn_wave(difficulty_multiplier)
		print("生成敌人波次 - 难度: ", difficulty_multiplier)

func next_level():
	current_level += 1
	difficulty_multiplier += 0.2  # 每关难度增加20%
	get_tree().reload_current_scene()

func get_game_time_formatted() -> String:
	var minutes = int(game_time) / 60
	var seconds = int(game_time) % 60
	return "%02d:%02d" % [minutes, seconds]
