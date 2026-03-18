extends Node2D

# 网格系统 - 管理游戏网格和占领机制
# Godot 4.6.1 版本

class_name GridSystem

signal grid_updated
signal dominion_calculated(percentage)

# 网格配置
@export var grid_width: int = 16
@export var grid_height: int = 12
@export var cell_size: float = 48.0

# 网格状态
enum CellState { EMPTY, DOMINION, WALL }
var grid: Array = []  # 二维数组存储网格状态

# 视觉效果
@export var grid_color: Color = Color(0.1, 0.1, 0.15, 1.0)
@export var dominion_color: Color = Color(0.0, 0.8, 0.6, 0.6)
@export var wall_color: Color = Color(0.3, 0.3, 0.35, 1.0)
@export var grid_line_color: Color = Color(0.2, 0.2, 0.25, 1.0)

func _ready():
	initialize_grid()
	generate_walls()

func initialize_grid():
	grid.clear()
	for x in range(grid_width):
		var column = []
		for y in range(grid_height):
			column.append(CellState.EMPTY)
		grid.append(column)

func generate_walls():
	# 在边缘生成墙壁
	for x in range(grid_width):
		set_cell(x, 0, CellState.WALL)
		set_cell(x, grid_height - 1, CellState.WALL)
	for y in range(grid_height):
		set_cell(0, y, CellState.WALL)
		set_cell(grid_width - 1, y, CellState.WALL)
	
	# 随机生成一些内部墙壁
	var wall_count = int(grid_width * grid_height * 0.1)  # 10%的墙壁
	for i in range(wall_count):
		var wx = randi() % (grid_width - 2) + 1
		var wy = randi() % (grid_height - 2) + 1
		set_cell(wx, wy, CellState.WALL)

func set_cell(x: int, y: int, state: CellState):
	if is_valid_cell(x, y):
		grid[x][y] = state
		queue_redraw()

func get_cell(x: int, y: int) -> CellState:
	if is_valid_cell(x, y):
		return grid[x][y]
	return CellState.WALL

func is_valid_cell(x: int, y: int) -> bool:
	return x >= 0 and x < grid_width and y >= 0 and y < grid_height

func is_walkable(x: int, y: int) -> bool:
	return is_valid_cell(x, y) and grid[x][y] != CellState.WALL

func world_to_grid(world_pos: Vector2) -> Vector2i:
	var offset = Vector2(grid_width * cell_size / 2, grid_height * cell_size / 2)
	var local_pos = world_pos + offset
	return Vector2i(int(local_pos.x / cell_size), int(local_pos.y / cell_size))

func grid_to_world(grid_pos: Vector2i) -> Vector2:
	var offset = Vector2(grid_width * cell_size / 2, grid_height * cell_size / 2)
	return Vector2(grid_pos.x * cell_size, grid_pos.y * cell_size) - offset + Vector2(cell_size / 2, cell_size / 2)

func claim_cell(x: int, y: int) -> bool:
	if is_valid_cell(x, y) and grid[x][y] == CellState.EMPTY:
		grid[x][y] = CellState.DOMINION
		queue_redraw()
		calculate_dominion()
		return true
	return false

func calculate_dominion() -> float:
	var total_cells = (grid_width - 2) * (grid_height - 2)  # 排除墙壁
	var dominion_cells = 0
	
	for x in range(1, grid_width - 1):
		for y in range(1, grid_height - 1):
			if grid[x][y] == CellState.DOMINION:
				dominion_cells += 1
	
	var percentage = float(dominion_cells) / total_cells * 100.0
	dominion_calculated.emit(percentage)
	return percentage

func _draw():
	var offset = Vector2(grid_width * cell_size / 2, grid_height * cell_size / 2)
	
	# 绘制网格单元
	for x in range(grid_width):
		for y in range(grid_height):
			var pos = Vector2(x * cell_size, y * cell_size) - offset
			var rect = Rect2(pos, Vector2(cell_size, cell_size))
			
			match grid[x][y]:
				CellState.EMPTY:
					draw_rect(rect, grid_color)
				CellState.DOMINION:
					draw_rect(rect, dominion_color)
				CellState.WALL:
					draw_rect(rect, wall_color)
	
	# 绘制网格线
	for x in range(grid_width + 1):
		var start = Vector2(x * cell_size, 0) - offset
		var end = Vector2(x * cell_size, grid_height * cell_size) - offset
		draw_line(start, end, grid_line_color, 1.0)
	
	for y in range(grid_height + 1):
		var start = Vector2(0, y * cell_size) - offset
		var end = Vector2(grid_width * cell_size, y * cell_size) - offset
		draw_line(start, end, grid_line_color, 1.0)
