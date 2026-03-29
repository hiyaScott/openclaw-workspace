# 群体管理器
# 文件：flock_manager.gd
# 配合 flock_agent.gd 使用

class_name FlockManager
extends Node2D

@export var agent_scene: PackedScene
@export var agent_count: int = 50
@export var spawn_radius: float = 200.0

var agents: Array[FlockAgent] = []

func _ready():
	spawn_agents()

func spawn_agents():
	if agent_scene == null:
		push_error("Agent scene not set!")
		return
	
	for i in range(agent_count):
		var agent = agent_scene.instantiate() as FlockAgent
		if agent:
			# 随机位置生成
			var angle = randf() * TAU
			var distance = randf() * spawn_radius
			agent.global_position = global_position + Vector2.RIGHT.rotated(angle) * distance
			
			add_child(agent)
			agents.append(agent)
	
	# 更新每个agent的邻居列表
	_update_flock_mates()

func _update_flock_mates():
	"""更新每个agent的邻居列表（优化：使用空间分区会更好）"""
	for agent in agents:
		agent.flock_mates.clear()
		for other in agents:
			if other != agent:
				agent.flock_mates.append(other)

func _process(delta):
	# 可以在这里添加动态调整参数的逻辑
	pass

# ========== 交互 ==========

func scatter_at(position: Vector2, radius: float, force: float = 500.0):
	"""在指定位置吓散群体"""
	for agent in agents:
		if agent.global_position.distance_to(position) < radius:
			var flee_direction = (agent.global_position - position).normalized()
			agent.velocity += flee_direction * force

func attract_to(position: Vector2, radius: float):
	"""吸引群体到指定位置"""
	for agent in agents:
		if agent.global_position.distance_to(position) < radius:
			agent.wander_target = position

# ========== 调试 ==========

func _draw():
	if OS.is_debug_build():
		# 绘制生成区域
		draw_arc(Vector2.ZERO, spawn_radius, 0, TAU, 64, Color(1, 1, 1, 0.2))
