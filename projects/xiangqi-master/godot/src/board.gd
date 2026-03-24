class_name XiangqiBoard
extends Node2D

# 中国象棋棋盘常量
const BOARD_WIDTH = 9   # 9列
const BOARD_HEIGHT = 10 # 10行
const CELL_SIZE = 60    # 格子大小

# 棋盘位置偏移
var board_offset: Vector2 = Vector2(100, 50)

# 当前棋盘状态: null 或棋子对象
var grid: Array = []

# 信号
signal piece_moved(from_pos, to_pos, piece)
signal piece_captured(attacker, target)

func _ready():
	_init_board()

func _init_board():
	# 初始化空棋盘
	grid = []
	for x in range(BOARD_WIDTH):
		grid.append([])
		for y in range(BOARD_HEIGHT):
			grid[x].append(null)

# 世界坐标转棋盘坐标
func world_to_grid(world_pos: Vector2) -> Vector2i:
	var relative = world_pos - board_offset
	var x = round(relative.x / CELL_SIZE)
	var y = round(relative.y / CELL_SIZE)
	return Vector2i(x, y)

# 棋盘坐标转世界坐标
func grid_to_world(grid_pos: Vector2i) -> Vector2:
	return board_offset + Vector2(grid_pos.x * CELL_SIZE, grid_pos.y * CELL_SIZE)

# 检查坐标是否在棋盘内
func is_valid_position(pos: Vector2i) -> bool:
	return pos.x >= 0 and pos.x < BOARD_WIDTH and pos.y >= 0 and pos.y < BOARD_HEIGHT

# 获取格子上的棋子
func get_piece_at(pos: Vector2i) -> Piece:
	if not is_valid_position(pos):
		return null
	return grid[pos.x][pos.y]

# 放置棋子
func place_piece(piece: Piece, pos: Vector2i):
	if is_valid_position(pos):
		grid[pos.x][pos.y] = piece
		if piece:
			piece.board_pos = pos
			piece.position = grid_to_world(pos)

# 移动棋子
func move_piece(from_pos: Vector2i, to_pos: Vector2i) -> bool:
	var piece = get_piece_at(from_pos)
	if not piece:
		return false
	
	var target = get_piece_at(to_pos)
	
	# 更新网格
	grid[from_pos.x][from_pos.y] = null
	grid[to_pos.x][to_pos.y] = piece
	
	# 更新棋子位置
	piece.board_pos = to_pos
	
	# 动画移动
	var tween = create_tween()
	tween.tween_property(piece, "position", grid_to_world(to_pos), 0.2)
	
	if target:
		target.queue_free()
		piece_captured.emit(piece, target)
	
	piece_moved.emit(from_pos, to_pos, piece)
	return true

# 验证马的走法（日字）
func is_valid_horse_move(from_pos: Vector2i, to_pos: Vector2i) -> bool:
	var dx = abs(to_pos.x - from_pos.x)
	var dy = abs(to_pos.y - from_pos.y)
	
	# 马走日：必须是 2+1 或 1+2
	if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
		return false
	
	# 检查绊马脚
	var blocking_pos: Vector2i
	if dx == 2:
		# 横向移动2格，检查横向中间的格子
		blocking_pos = Vector2i((from_pos.x + to_pos.x) / 2, from_pos.y)
	else:
		# 纵向移动2格，检查纵向中间的格子
		blocking_pos = Vector2i(from_pos.x, (from_pos.y + to_pos.y) / 2)
	
	if get_piece_at(blocking_pos) != null:
		return false  # 有棋子绊马脚
	
	return true

# 获取马的所有合法走法
func get_horse_valid_moves(pos: Vector2i) -> Array[Vector2i]:
	var moves: Array[Vector2i] = []
	var horse_moves = [
		Vector2i(2, 1), Vector2i(2, -1),
		Vector2i(-2, 1), Vector2i(-2, -1),
		Vector2i(1, 2), Vector2i(1, -2),
		Vector2i(-1, 2), Vector2i(-1, -2)
	]
	
	for move in horse_moves:
		var target = pos + move
		if is_valid_position(target) and is_valid_horse_move(pos, target):
			moves.append(target)
	
	return moves

func _draw():
	# 绘制棋盘背景
	draw_rect(Rect2(board_offset - Vector2(5, 5), 
		Vector2(BOARD_WIDTH * CELL_SIZE + 10, BOARD_HEIGHT * CELL_SIZE + 10)), 
		Color(0.9, 0.7, 0.4), true)
	
	# 绘制格子线
	for x in range(BOARD_WIDTH):
		for y in range(BOARD_HEIGHT):
			var pos = grid_to_world(Vector2i(x, y))
			draw_rect(Rect2(pos - Vector2(CELL_SIZE/2, CELL_SIZE/2), 
				Vector2(CELL_SIZE, CELL_SIZE)), 
				Color(0.85, 0.65, 0.35), false, 1)
