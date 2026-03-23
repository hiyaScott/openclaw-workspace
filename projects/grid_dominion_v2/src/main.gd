extends Node2D

# GRID.DOMINION - 游戏主场景
# Godot 4.6.1 版本

@onready var grid_system = $GridSystem
@onready var player = $Player
@onready var enemy_manager = $EnemyManager
@onready var ui = $UI
@onready var game_manager = $GameManager

func _ready():
	print("GRID.DOMINION v2.0 - 游戏启动")
	
	# 初始化游戏
	game_manager.initialize_game()
	
	# 连接信号
	game_manager.game_over.connect(_on_game_over)
	game_manager.level_complete.connect(_on_level_complete)

func _on_game_over():
	ui.show_game_over()

func _on_level_complete():
	ui.show_level_complete()

func _input(event):
	if event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
