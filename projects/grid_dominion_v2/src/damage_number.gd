extends Node2D

# 伤害数字显示 - Godot 4.6.1
# 浮动伤害数字效果

class_name DamageNumber

static func show_damage(position: Vector2, damage: int, color: Color = Color.WHITE):
	var label = Label.new()
	label.text = str(damage)
	label.modulate = color
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	
	# 设置字体大小
	var font_size = 16
	if damage >= 50:
		font_size = 24
	elif damage >= 20:
		font_size = 20
	
	# 创建字体设置
	var label_settings = LabelSettings.new()
	label_settings.font_size = font_size
	label_settings.font_color = color
	label_settings.outline_size = 2
	label_settings.outline_color = Color.BLACK
	label.label_settings = label_settings
	
	# 添加到场景
	get_tree().root.add_child(label)
	label.position = position - Vector2(20, 30)
	
	# 动画
	var tween = label.create_tween()
	tween.parallel().tween_property(label, "position", label.position + Vector2(0, -50), 1.0)
	tween.parallel().tween_property(label, "modulate", Color(color.r, color.g, color.b, 0.0), 1.0)
	tween.tween_callback(label.queue_free)

static func show_text(position: Vector2, text: String, color: Color = Color.YELLOW):
	var label = Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	
	var label_settings = LabelSettings.new()
	label_settings.font_size = 14
	label_settings.font_color = color
	label_settings.outline_size = 2
	label_settings.outline_color = Color.BLACK
	label.label_settings = label_settings
	
	get_tree().root.add_child(label)
	label.position = position - Vector2(40, 40)
	
	var tween = label.create_tween()
	tween.parallel().tween_property(label, "position", label.position + Vector2(0, -40), 1.5)
	tween.parallel().tween_property(label, "modulate", Color(color.r, color.g, color.b, 0.0), 1.5)
	tween.tween_callback(label.queue_free)
