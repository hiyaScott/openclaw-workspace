extends Node2D

# 格子状态枚举
enum CellState {
	EMPTY,      # 未占领
	OWNED,      # 玩家占领
	BLOCKED     # 障碍物
}

# 网格配置
const GRID_WIDTH = 12
const GRID_HEIGHT = 12
const CELL_SIZE = 50

# 颜色配置
const COLOR_EMPTY = Color(0.1, 0.1, 0.15, 1.0)
const COLOR_OWNED = Color(0.0, 0.8, 0.6, 0.6)
const COLOR_GRID_LINE = Color(0.2, 0.25, 0.3, 1.0)
const COLOR_BLOCKED = Color(0.3, 0.3, 0.35, 1.0)

# 网格数据
var cells: Array[CellState] = []
var grid_offset: Vector2

func _ready():
	# 计算网格居中偏移
	var grid_width_px = GRID_WIDTH * CELL_SIZE
	var grid_height_px = GRID_HEIGHT * CELL_SIZE
	grid_offset = Vector2(
		(get_viewport_rect().size.x - grid_width_px) / 2,
		(get_viewport_rect().size.y - grid_height_px) / 2
	)
	
	# 初始化网格
	initialize_grid()

func initialize_grid():
	cells.clear()
	for i in range(GRID_WIDTH * GRID_HEIGHT):
		cells.append(CellState.EMPTY)

func get_cell_index(x: int, y: int) -> int:
	if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
		return -1
	return y * GRID_WIDTH + x

func get_cell(x: int, y: int) -> CellState:
	var index = get_cell_index(x, y)
	if index < 0:
		return CellState.BLOCKED
	return cells[index]

func set_cell(x: int, y: int, state: CellState):
	var index = get_cell_index(x, y)
	if index >= 0:
		cells[index] = state
		queue_redraw()

func occupy_cell(x: int, y: int) -> bool:
	var index = get_cell_index(x, y)
	if index < 0 or cells[index] == CellState.BLOCKED:
		return false
	if cells[index] == CellState.EMPTY:
		cells[index] = CellState.OWNED
		queue_redraw()
		return true
	return false

func get_occupancy_rate() -> float:
	var owned_count = 0
	var total_cells = GRID_WIDTH * GRID_HEIGHT
	for cell in cells:
		if cell == CellState.OWNED:
			owned_count += 1
	return float(owned_count) / float(total_cells)

func get_owned_cells() -> Array[Vector2i]:
	var result: Array[Vector2i] = []
	for y in range(GRID_HEIGHT):
		for x in range(GRID_WIDTH):
			if get_cell(x, y) == CellState.OWNED:
				result.append(Vector2i(x, y))
	return result

func is_in_bounds(x: int, y: int) -> bool:
	return x >= 0 and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT

func world_to_grid(world_pos: Vector2) -> Vector2i:
	var local_pos = world_pos - grid_offset
	return Vector2i(
		int(local_pos.x / CELL_SIZE),
		int(local_pos.y / CELL_SIZE)
	)

func grid_to_world(grid_pos: Vector2i) -> Vector2:
	return grid_offset + Vector2(
		grid_pos.x * CELL_SIZE + CELL_SIZE / 2,
		grid_pos.y * CELL_SIZE + CELL_SIZE / 2
	)

func _draw():
	# 绘制格子背景
	for y in range(GRID_HEIGHT):
		for x in range(GRID_WIDTH):
			var rect = Rect2(
				grid_offset.x + x * CELL_SIZE,
				grid_offset.y + y * CELL_SIZE,
				CELL_SIZE,
				CELL_SIZE
			)
			
			var cell_state = get_cell(x, y)
			match cell_state:
				CellState.EMPTY:
					draw_rect(rect, COLOR_EMPTY)
				CellState.OWNED:
					draw_rect(rect, COLOR_OWNED)
				CellState.BLOCKED:
					draw_rect(rect, COLOR_BLOCKED)
	
	# 绘制网格线
	for x in range(GRID_WIDTH + 1):
		var line_start = Vector2(grid_offset.x + x * CELL_SIZE, grid_offset.y)
		var line_end = Vector2(grid_offset.x + x * CELL_SIZE, grid_offset.y + GRID_HEIGHT * CELL_SIZE)
		draw_line(line_start, line_end, COLOR_GRID_LINE, 1.0)
	
	for y in range(GRID_HEIGHT + 1):
		var line_start = Vector2(grid_offset.x, grid_offset.y + y * CELL_SIZE)
		var line_end = Vector2(grid_offset.x + GRID_WIDTH * CELL_SIZE, grid_offset.y + y * CELL_SIZE)
		draw_line(line_start, line_end, COLOR_GRID_LINE, 1.0)
