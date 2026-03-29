# 群体AI（群集行为/Boids）
# 文件：flock_agent.gd
# 适用于：Godot 4.x

class_name FlockAgent
extends CharacterBody2D

# Boids参数
@export var separation_weight: float = 1.5
@export var alignment_weight: float = 1.0
@export var cohesion_weight: float = 1.0
@export var wander_weight: float = 0.5
@export var avoid_obstacles_weight: float = 2.0

# 移动参数
@export var perception_radius: float = 100.0
@export var separation_radius: float = 40.0
@export var max_speed: float = 200.0
@export var max_force: float = 10.0

# 障碍物避免
@export var obstacle_avoid_distance: float = 80.0
@export var obstacle_layers: int = 1

var flock_mates: Array[FlockAgent] = []
var wander_target: Vector2 = Vector2.ZERO

@onready var flock_manager = get_parent()

func _ready():
	# 随机初始速度
	velocity = Vector2(randf() - 0.5, randf() - 0.5).normalized() * max_speed
	wander_target = global_position

func _physics_process(delta):
	# 计算各种力
	var separation = _calculate_separation()
	var alignment = _calculate_alignment()
	var cohesion = _calculate_cohesion()
	var wander = _calculate_wander()
	var avoidance = _calculate_obstacle_avoidance()
	
	# 合并力
	var acceleration = separation * separation_weight + \
				   alignment * alignment_weight + \
				   cohesion * cohesion_weight + \
				   wander * wander_weight + \
				   avoidance * avoid_obstacles_weight
	
	# 更新速度
	velocity += acceleration * delta
	velocity = velocity.limit_length(max_speed)
	
	# 移动
	move_and_slide()
	
	# 朝向移动方向
	if velocity.length() > 0.1:
		rotation = velocity.angle()
	
	# 边界处理（简单的环绕）
	_screen_wrap()

# ========== Boids行为 ==========

func _calculate_separation() -> Vector2:
	"""分离：避免与邻居过于接近"""
	var steer = Vector2.ZERO
	var count = 0
	
	for mate in flock_mates:
		var distance = global_position.distance_to(mate.global_position)
		if distance > 0 and distance < separation_radius:
			var diff = global_position - mate.global_position
			diff = diff.normalized() / distance  # 距离越近，排斥越强
			steer += diff
			count += 1
	
	if count > 0:
		steer /= count
		steer = steer.normalized() * max_speed
		steer = steer - velocity
		steer = steer.limit_length(max_force)
	
	return steer

func _calculate_alignment() -> Vector2:
	"""对齐：与邻居朝向一致"""
	var average_velocity = Vector2.ZERO
	var count = 0
	
	for mate in flock_mates:
		if global_position.distance_to(mate.global_position) < perception_radius:
			average_velocity += mate.velocity
			count += 1
	
	if count > 0:
		average_velocity /= count
		average_velocity = average_velocity.normalized() * max_speed
		var steer = average_velocity - velocity
		return steer.limit_length(max_force)
	
	return Vector2.ZERO

func _calculate_cohesion() -> Vector2:
	"""凝聚：向群体中心移动"""
	var center = Vector2.ZERO
	var count = 0
	
	for mate in flock_mates:
		if global_position.distance_to(mate.global_position) < perception_radius:
			center += mate.global_position
			count += 1
	
	if count > 0:
		center /= count
		return _seek(center)
	
	return Vector2.ZERO

func _calculate_wander() -> Vector2:
	"""漫游：随机移动"""
	# 每隔一段时间改变目标
	if randf() < 0.02:  # 约每秒1-2次（取决于帧率）
		var wander_distance = 100.0
		var wander_radius = 50.0
		var wander_angle = randf() * TAU
		
		var circle_center = velocity.normalized() * wander_distance
		var displacement = Vector2.RIGHT.rotated(wander_angle) * wander_radius
		
		wander_target = global_position + circle_center + displacement
	
	return _seek(wander_target) * 0.3  # 减弱漫游影响

func _calculate_obstacle_avoidance() -> Vector2:
	"""障碍物避免"""
	var space_state = get_world_2d().direct_space_state
	
	# 向前方发射射线
	var forward = velocity.normalized()
	var ray_end = global_position + forward * obstacle_avoid_distance
	
	var query = PhysicsRayQueryParameters2D.create(
		global_position,
		ray_end,
		obstacle_layers
	)
	query.exclude = [self]
	
	var result = space_state.intersect_ray(query)
	
	if not result.is_empty():
		# 检测到障碍物，计算避让方向
		var obstacle_pos = result.position
		var avoid_direction = (global_position - obstacle_pos).normalized()
		
		# 添加切向分量以平滑绕过
		var tangent = forward.rotated(PI / 2)
		if randf() > 0.5:
			tangent = -tangent
		
		avoid_direction = (avoid_direction + tangent).normalized()
		return avoid_direction * max_force * 2.0
	
	return Vector2.ZERO

# ========== 辅助函数 ==========

func _seek(target: Vector2) -> Vector2:
	"""向目标移动"""
	var desired = (target - global_position).normalized() * max_speed
	var steer = desired - velocity
	return steer.limit_length(max_force)

func _flee(target: Vector2) -> Vector2:
	"""逃离目标"""
	var desired = (global_position - target).normalized() * max_speed
	var steer = desired - velocity
	return steer.limit_length(max_force)

func _screen_wrap():
	"""屏幕环绕（用于演示）"""
	var viewport_size = get_viewport_rect().size
	var wrapped = false
	
	if global_position.x < 0:
		global_position.x = viewport_size.x
		wrapped = true
	elif global_position.x > viewport_size.x:
		global_position.x = 0
		wrapped = true
	
	if global_position.y < 0:
		global_position.y = viewport_size.y
		wrapped = true
	elif global_position.y > viewport_size.y:
		global_position.y = 0
		wrapped = true
	
	# 如果发生了环绕，重置漫游目标
	if wrapped:
		wander_target = global_position

# ========== 调试 ==========

func _draw():
	if OS.is_debug_build():
		# 绘制感知范围
		draw_arc(Vector2.ZERO, perception_radius, 0, TAU, 32, Color(0, 1, 0, 0.3))
		draw_arc(Vector2.ZERO, separation_radius, 0, TAU, 32, Color(1, 0, 0, 0.3))
		
		# 绘制速度向量
		draw_line(Vector2.ZERO, velocity.normalized() * 30, Color.blue, 2)
