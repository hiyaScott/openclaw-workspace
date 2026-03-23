extends Node2D

# 粒子效果系统 - Godot 4.6.1
# 各种视觉特效

class_name ParticleEffects

# 占领效果
static func create_claim_effect(position: Vector2, color: Color):
	for i in range(8):
		var particle = ColorRect.new()
		particle.color = color
		particle.size = Vector2(4, 4)
		particle.position = position
		
		get_tree().root.add_child(particle)
		
		var angle = (i / 8.0) * PI * 2
		var direction = Vector2(cos(angle), sin(angle))
		var target_pos = position + direction * 30
		
		var tween = particle.create_tween()
		tween.parallel().tween_property(particle, "position", target_pos, 0.5)
		tween.parallel().tween_property(particle, "modulate", Color(color.r, color.g, color.b, 0.0), 0.5)
		tween.tween_callback(particle.queue_free)

# 敌人死亡效果
static func create_death_effect(position: Vector2):
	for i in range(12):
		var particle = ColorRect.new()
		particle.color = Color(0.9, 0.3, 0.2, 1.0)
		particle.size = Vector2(6, 6)
		particle.position = position
		
		get_tree().root.add_child(particle)
		
		var angle = (i / 12.0) * PI * 2
		var direction = Vector2(cos(angle), sin(angle))
		var target_pos = position + direction * 50
		
		var tween = particle.create_tween()
		tween.parallel().tween_property(particle, "position", target_pos, 0.6)
		tween.parallel().tween_property(particle, "rotation", randf() * PI * 2, 0.6)
		tween.parallel().tween_property(particle, "modulate", Color(0.9, 0.3, 0.2, 0.0), 0.6)
		tween.tween_callback(particle.queue_free)

# 冲刺效果
static func create_dash_effect(start_pos: Vector2, end_pos: Vector2):
	var trail = Line2D.new()
	trail.points = [start_pos, end_pos]
	trail.width = 8
	trail.default_color = Color(0.5, 1.0, 1.0, 0.6)
	
	get_tree().root.add_child(trail)
	
	var tween = trail.create_tween()
	tween.tween_property(trail, "modulate", Color(0.5, 1.0, 1.0, 0.0), 0.3)
	tween.tween_callback(trail.queue_free)

# 升级效果
static func create_level_up_effect(position: Vector2):
	# 光环效果
	var ring = ColorRect.new()
	ring.color = Color(1.0, 0.8, 0.0, 0.5)
	ring.size = Vector2(10, 10)
	ring.position = position - Vector2(5, 5)
	
	get_tree().root.add_child(ring)
	
	var tween = ring.create_tween()
	tween.parallel().tween_property(ring, "size", Vector2(200, 200), 1.0)
	tween.parallel().tween_property(ring, "position", position - Vector2(100, 100), 1.0)
	tween.parallel().tween_property(ring, "modulate", Color(1.0, 0.8, 0.0, 0.0), 1.0)
	tween.tween_callback(ring.queue_free)
	
	# 粒子
	for i in range(16):
		var particle = ColorRect.new()
		particle.color = Color(1.0, 0.9, 0.3, 1.0)
		particle.size = Vector2(5, 5)
		particle.position = position
		
		get_tree().root.add_child(particle)
		
		var angle = (i / 16.0) * PI * 2
		var direction = Vector2(cos(angle), sin(angle))
		var target_pos = position + direction * 60
		
		var ptween = particle.create_tween()
		ptween.parallel().tween_property(particle, "position", target_pos, 1.0)
		ptween.parallel().tween_property(particle, "modulate", Color(1.0, 0.9, 0.3, 0.0), 1.0)
		ptween.tween_callback(particle.queue_free)
