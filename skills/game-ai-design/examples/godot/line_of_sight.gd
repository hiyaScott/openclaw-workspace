# 视线检测与追击逻辑
# 文件：line_of_sight.gd
# 适用于：Godot 4.x

class_name LineOfSight
extends Node2D

@export var view_distance: float = 300.0
@export var view_angle: float = 90.0  # 度
@export var view_cone_color: Color = Color(1, 0, 0, 0.3)
@export var debug_draw: bool = true

var target: Node2D = null
var can_see_target: bool = false
var last_known_position: Vector2 = Vector2.ZERO

# 记忆系统
var memory_timer: float = 0.0
@export var memory_duration: float = 3.0  # 丢失目标后记忆时间

func _ready():
	# 可选：自动查找目标
	call_deferred("_find_target")

func _find_target():
	target = get_tree().get_first_node_in_group("player")

func _physics_process(delta):
	if target:
		var could_see = can_see_target
		can_see_target = check_line_of_sight(target)
		
		if can_see_target:
			last_known_position = target.global_position
			memory_timer = memory_duration
		elif could_see and not can_see_target:
			# 刚刚丢失目标
			print("Target lost! Last known position: ", last_known_position)
		
		# 记忆系统
		if not can_see_target and memory_timer > 0:
			memory_timer -= delta

func check_line_of_sight(target_node: Node2D) -> bool:
	if target_node == null:
		return false
	
	var to_target = target_node.global_position - global_position
	var distance = to_target.length()
	
	# 距离检查
	if distance > view_distance:
		return false
	
	# 角度检查
	var forward = Vector2.RIGHT.rotated(global_rotation)
	var angle_to_target = rad_to_deg(forward.angle_to(to_target))
	
	if abs(angle_to_target) > view_angle / 2.0:
		return false
	
	# 射线检测（障碍物）
	var space_state = get_world_2d().direct_space_state
	var query = PhysicsRayQueryParameters2D.create(
		global_position,
		target_node.global_position,
		1  # 碰撞层掩码
	)
	query.exclude = [get_parent()]  # 排除自身
	
	var result = space_state.intersect_ray(query)
	
	if result.is_empty():
		return true
	
	return result.collider == target_node

func check_line_of_sight_with_offset(target_node: Node2D, offset: Vector2) -> bool:
	"""检查特定偏移位置的视线（用于检查玩家身体的不同部位）"""
	if target_node == null:
		return false
	
	var target_pos = target_node.global_position + offset
	var to_target = target_pos - global_position
	var distance = to_target.length()
	
	if distance > view_distance:
		return false
	
	var forward = Vector2.RIGHT.rotated(global_rotation)
	var angle_to_target = rad_to_deg(forward.angle_to(to_target))
	
	if abs(angle_to_target) > view_angle / 2.0:
		return false
	
	var space_state = get_world_2d().direct_space_state
	var query = PhysicsRayQueryParameters2D.create(
		global_position,
		target_pos,
		1
	)
	query.exclude = [get_parent()]
	
	var result = space_state.intersect_ray(query)
	
	if result.is_empty():
		return true
	
	return result.collider == target_node

func get_predicted_position(target_node: Node2D, time_ahead: float) -> Vector2:
	"""预测目标未来位置（用于射击或拦截）"""
	if not target_node is CharacterBody2D:
		return target_node.global_position
	
	var target_body: CharacterBody2D = target_node
	return target_node.global_position + target_body.velocity * time_ahead

func get_intercept_point(target_node: Node2D, projectile_speed: float) -> Vector2:
	"""计算拦截点（考虑子弹速度和目标速度）"""
	if not target_node is CharacterBody2D:
		return target_node.global_position
	
	var target_body: CharacterBody2D = target_node
	var to_target = target_node.global_position - global_position
	var target_velocity = target_body.velocity
	
	# 二次方程求解
	var a = target_velocity.dot(target_velocity) - projectile_speed * projectile_speed
	var b = 2 * to_target.dot(target_velocity)
	var c = to_target.dot(to_target)
	
	var discriminant = b * b - 4 * a * c
	
	if discriminant < 0:
		# 无法拦截，返回当前位置
		return target_node.global_position
	
	var t = (-b - sqrt(discriminant)) / (2 * a)
	
	if t < 0:
		t = (-b + sqrt(discriminant)) / (2 * a)
	
	if t < 0:
		return target_node.global_position
	
	return target_node.global_position + target_velocity * t

func has_memory_of_target() -> bool:
	"""是否还记得目标位置"""
	return memory_timer > 0

func get_last_known_position() -> Vector2:
	return last_known_position

func clear_memory():
	memory_timer = 0.0
	last_known_position = Vector2.ZERO

# ========== 调试绘制 ==========

func _draw():
	if not debug_draw:
		return
	
	if Engine.is_editor_hint() or OS.is_debug_build():
		# 绘制视野锥
		var points = PackedVector2Array()
		points.append(Vector2.ZERO)
		
		var steps = 20
		var start_angle = -view_angle / 2.0
		var angle_step = view_angle / steps
		
		for i in range(steps + 1):
			var angle = deg_to_rad(start_angle + angle_step * i)
			var point = Vector2.RIGHT.rotated(angle) * view_distance
			points.append(point)
		
		var colors = PackedColorArray([view_cone_color])
		draw_polygon(points, colors)
		
		# 绘制视线
		if target and can_see_target:
			draw_line(Vector2.ZERO, to_local(target.global_position), Color.green, 2.0)
		elif has_memory_of_target():
			# 绘制记忆中的位置
			draw_line(Vector2.ZERO, to_local(last_known_position), Color.yellow, 1.0)
			draw_circle(to_local(last_known_position), 5, Color.yellow)

# ========== 信号 ==========

signal target_detected(target_node: Node2D)
signal target_lost(target_node: Node2D)
signal memory_expired

# 使用示例的扩展版本
func _on_detection_changed():
	var could_see = can_see_target
	if target:
		can_see_target = check_line_of_sight(target)
		
		if not could_see and can_see_target:
			target_detected.emit(target)
		elif could_see and not can_see_target:
			target_lost.emit(target)
