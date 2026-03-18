extends Node

# 技能系统 - Godot 4.6.1
# 管理玩家技能

class_name SkillSystem

signal skill_used(skill_name)
signal skill_cooldown_updated(skill_name, cooldown_percent)

# 技能数据
enum SkillType { NONE, BLAST, SHIELD, SPEED }

var skills: Dictionary = {
	"Q": {
		"type": SkillType.BLAST,
		"name": "区域爆破",
		"description": "对周围3x3区域造成伤害",
		"cooldown": 8.0,
		"current_cooldown": 0.0,
		"damage": 50,
		"range": 1
	},
	"E": {
		"type": SkillType.SHIELD,
		"name": "护盾",
		"description": "获得5秒无敌护盾",
		"cooldown": 15.0,
		"current_cooldown": 0.0,
		"duration": 5.0
	},
	"R": {
		"type": SkillType.SPEED,
		"name": "加速",
		"description": "移动速度翻倍，持续5秒",
		"cooldown": 12.0,
		"current_cooldown": 0.0,
		"duration": 5.0,
		"speed_multiplier": 2.0
	}
}

# 组件引用
@onready var player = get_parent()
@onready var grid_system = get_node_or_null("/root/Main/GridSystem")
@onready var enemy_manager = get_node_or_null("/root/Main/EnemyManager")

func _ready():
	pass

func _process(delta):
	# 更新技能冷却
	for key in skills.keys():
		if skills[key]["current_cooldown"] > 0:
			skills[key]["current_cooldown"] -= delta
			if skills[key]["current_cooldown"] < 0:
				skills[key]["current_cooldown"] = 0
		
		# 发送冷却更新信号
		var cooldown_percent = 1.0 - (skills[key]["current_cooldown"] / skills[key]["cooldown"])
		skill_cooldown_updated.emit(key, cooldown_percent)

func use_skill(skill_key: String) -> bool:
	if not skills.has(skill_key):
		return false
	
	var skill = skills[skill_key]
	
	if skill["current_cooldown"] > 0:
		return false
	
	# 执行技能
	match skill["type"]:
		SkillType.BLAST:
			use_blast_skill(skill)
		SkillType.SHIELD:
			use_shield_skill(skill)
		SkillType.SPEED:
			use_speed_skill(skill)
	
	# 设置冷却
	skill["current_cooldown"] = skill["cooldown"]
	skill_used.emit(skill["name"])
	
	return true

func use_blast_skill(skill: Dictionary):
	if not grid_system or not enemy_manager:
		return
	
	var player_pos = grid_system.world_to_grid(player.position)
	var range = skill["range"]
	
	# 对范围内的敌人造成伤害
	for enemy in enemy_manager.enemies:
		var enemy_pos = grid_system.world_to_grid(enemy.position)
		var dist = abs(enemy_pos.x - player_pos.x) + abs(enemy_pos.y - player_pos.y)
		
		if dist <= range:
			enemy.take_damage(skill["damage"])
	
	# 视觉效果
	create_blast_effect(player.position)

func use_shield_skill(skill: Dictionary):
	player.is_shielded = true
	
	# 视觉反馈
	if player.sprite:
		player.sprite.modulate = Color(0.3, 0.8, 1.0, 0.8)
	
	# 定时器移除护盾
	await get_tree().create_timer(skill["duration"]).timeout
	
	player.is_shielded = false
	if player.sprite:
		player.sprite.modulate = Color.WHITE

func use_speed_skill(skill: Dictionary):
	var original_speed = player.move_speed
	player.move_speed *= skill["speed_multiplier"]
	
	# 视觉反馈
	if player.sprite:
		var tween = create_tween()
		tween.tween_property(player.sprite, "modulate", Color(1.0, 1.0, 0.5, 1.0), 0.2)
	
	# 定时器恢复速度
	await get_tree().create_timer(skill["duration"]).timeout
	
	player.move_speed = original_speed
	if player.sprite:
		player.sprite.modulate = Color.WHITE

func create_blast_effect(pos: Vector2):
	# 创建爆炸视觉效果
	var blast = ColorRect.new()
	blast.color = Color(1.0, 0.5, 0.0, 0.5)
	blast.size = Vector2(100, 100)
	blast.position = pos - Vector2(50, 50)
	get_tree().root.add_child(blast)
	
	# 动画
	var tween = create_tween()
	tween.tween_property(blast, "modulate", Color(1.0, 0.5, 0.0, 0.0), 0.5)
	tween.tween_callback(blast.queue_free)

func get_skill_info(skill_key: String) -> Dictionary:
	if skills.has(skill_key):
		return skills[skill_key]
	return {}

func is_skill_ready(skill_key: String) -> bool:
	if skills.has(skill_key):
		return skills[skill_key]["current_cooldown"] <= 0
	return false
