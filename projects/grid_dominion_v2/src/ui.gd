extends CanvasLayer

# UI管理器 - Godot 4.6.1 版本
# 处理游戏界面显示

class_name GameUI

# UI元素引用
@onready var health_bar = $MarginContainer/VBoxContainer/HealthBar
@onready var health_label = $MarginContainer/VBoxContainer/HealthBar/HealthLabel
@onready var score_label = $MarginContainer/VBoxContainer/ScoreLabel
@onready var dominion_label = $MarginContainer/VBoxContainer/DominionLabel
@onready var time_label = $MarginContainer/VBoxContainer/TimeLabel
@onready var game_over_panel = $GameOverPanel
@onready var level_complete_panel = $LevelCompletePanel

# 技能UI
@onready var skill_q_bar = $SkillContainer/SkillQ/ProgressBar
@onready var skill_e_bar = $SkillContainer/SkillE/ProgressBar
@onready var skill_r_bar = $SkillContainer/SkillR/ProgressBar

# 组件引用
@onready var player = get_node("/root/Main/Player")
@onready var game_manager = get_node("/root/Main/GameManager")

func _ready():
	# 连接信号
	if player:
		player.health_changed.connect(_on_health_changed)
		if player.skill_system:
			player.skill_system.skill_cooldown_updated.connect(_on_skill_cooldown_updated)
	
	if game_manager:
		game_manager.score_changed.connect(_on_score_changed)
		game_manager.dominion_changed.connect(_on_dominion_changed)
	
	# 隐藏面板
	game_over_panel.hide()
	level_complete_panel.hide()

func _process(delta):
	if game_manager:
		time_label.text = "时间: " + game_manager.get_game_time_formatted()

func _on_health_changed(new_health, max_health):
	health_bar.max_value = max_health
	health_bar.value = new_health
	health_label.text = "%d/%d" % [new_health, max_health]

func _on_score_changed(new_score):
	score_label.text = "分数: %d" % new_score

func _on_dominion_changed(percentage):
	dominion_label.text = "占领: %.1f%% / 80%%" % percentage

func _on_skill_cooldown_updated(skill_key, cooldown_percent):
	match skill_key:
		"Q":
			skill_q_bar.value = cooldown_percent * 100
		"E":
			skill_e_bar.value = cooldown_percent * 100
		"R":
			skill_r_bar.value = cooldown_percent * 100

func show_game_over():
	game_over_panel.show()

func show_level_complete():
	level_complete_panel.show()

func _on_restart_button_pressed():
	get_tree().reload_current_scene()

func _on_next_level_button_pressed():
	if game_manager:
		game_manager.next_level()
