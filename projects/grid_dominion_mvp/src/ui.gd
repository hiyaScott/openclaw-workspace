extends CanvasLayer

# UI配置
const BAR_WIDTH = 300
const BAR_HEIGHT = 20

# 引用
@onready var occupancy_label = $MarginContainer/VBoxContainer/OccupancyLabel
@onready var occupancy_bar = $MarginContainer/VBoxContainer/OccupancyBar
@onready var health_label = $MarginContainer/VBoxContainer/HealthLabel
@onready var game_over_panel = $GameOverPanel
@onready var game_won_panel = $GameWonPanel
@onready var final_time_label = $GameWonPanel/VBoxContainer/FinalTimeLabel

func _ready():
	# 初始化
	occupancy_bar.min_value = 0
	occupancy_bar.max_value = 100
	occupancy_bar.value = 0
	
	# 隐藏结束画面
	game_over_panel.hide()
	game_won_panel.hide()

func update_occupancy(current_rate: float, target_rate: float):
	var percentage = current_rate * 100
	var target_percentage = target_rate * 100
	
	occupancy_label.text = "占领率: %.1f%% / %.0f%%" % [percentage, target_percentage]
	occupancy_bar.value = percentage
	
	# 根据进度改变颜色
	if current_rate >= target_rate:
		occupancy_bar.modulate = Color(0.0, 1.0, 0.5, 1.0)  # 绿色
	elif current_rate >= target_rate * 0.7:
		occupancy_bar.modulate = Color(1.0, 0.8, 0.0, 1.0)  # 黄色
	else:
		occupancy_bar.modulate = Color(0.0, 0.8, 1.0, 1.0)  # 蓝色

func update_health(current: int, max_health: int):
	health_label.text = "生命值: %d / %d" % [current, max_health]
	
	# 根据生命值改变颜色
	if current <= 1:
		health_label.modulate = Color(1.0, 0.2, 0.2, 1.0)  # 红色
	elif current <= max_health / 2:
		health_label.modulate = Color(1.0, 0.8, 0.0, 1.0)  # 黄色
	else:
		health_label.modulate = Color(0.0, 1.0, 0.5, 1.0)  # 绿色

func show_game_over():
	game_over_panel.show()

func show_game_won(time_seconds: float):
	var minutes = int(time_seconds) / 60
	var seconds = int(time_seconds) % 60
	final_time_label.text = "通关时间: %02d:%02d" % [minutes, seconds]
	game_won_panel.show()

func hide_game_over():
	game_over_panel.hide()
	game_won_panel.hide()
