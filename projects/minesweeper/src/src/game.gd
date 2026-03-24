extends Node2D

# 扫雷游戏 - 主场景
# Godot 4.6.1

const GRID_SIZE = 10
const CELL_SIZE = 40
const MINE_COUNT = 15

var grid = []
var revealed = []
var flagged = []
var game_over = false
var first_click = true

@onready var camera = $Camera2D

func _ready():
	print("扫雷游戏启动")
	initialize_grid()
	center_camera()

func initialize_grid():
	grid.clear()
	revealed.clear()
	flagged.clear()
	
	for x in range(GRID_SIZE):
		grid.append([])
		revealed.append([])
		flagged.append([])
		for y in range(GRID_SIZE):
			grid[x].append(0)
			revealed[x].append(false)
			flagged[x].append(false)

func place_mines(exclude_x, exclude_y):
	var mines_placed = 0
	while mines_placed < MINE_COUNT:
		var x = randi() % GRID_SIZE
		var y = randi() % GRID_SIZE
		
		if grid[x][y] != -1 and not (x == exclude_x and y == exclude_y):
			grid[x][y] = -1
			mines_placed += 1
	
	# 计算数字
	for x in range(GRID_SIZE):
		for y in range(GRID_SIZE):
			if grid[x][y] != -1:
				grid[x][y] = count_adjacent_mines(x, y)

func count_adjacent_mines(x, y) -> int:
	var count = 0
	for dx in range(-1, 2):
		for dy in range(-1, 2):
			var nx = x + dx
			var ny = y + dy
			if nx >= 0 and nx < GRID_SIZE and ny >= 0 and ny < GRID_SIZE:
				if grid[nx][ny] == -1:
					count += 1
	return count

func _draw():
	for x in range(GRID_SIZE):
		for y in range(GRID_SIZE):
			var pos = Vector2(x * CELL_SIZE, y * CELL_SIZE)
			
			# 绘制格子背景
			if revealed[x][y]:
				draw_rect(Rect2(pos, Vector2(CELL_SIZE - 1, CELL_SIZE - 1)), Color(0.8, 0.8, 0.8))
				
				# 绘制数字或地雷
				if grid[x][y] == -1:
					draw_circle(pos + Vector2(CELL_SIZE/2, CELL_SIZE/2), 12, Color.BLACK)
				elif grid[x][y] > 0:
					draw_string(default_font, pos + Vector2(12, 28), str(grid[x][y]), get_number_color(grid[x][y]))
			else:
				# 未揭开的格子
				if flagged[x][y]:
					draw_rect(Rect2(pos, Vector2(CELL_SIZE - 1, CELL_SIZE - 1)), Color(1, 0.5, 0.5))
					draw_string(default_font, pos + Vector2(10, 28), "🚩", Color.RED)
				else:
					draw_rect(Rect2(pos, Vector2(CELL_SIZE - 1, CELL_SIZE - 1)), Color(0.6, 0.6, 0.6))

func get_number_color(num: int) -> Color:
	match num:
		1: return Color.BLUE
		2: return Color.GREEN
		3: return Color.RED
		4: return Color.NAVY_BLUE
		5: return Color.MAROON
		6: return Color.CYAN
		7: return Color.BLACK
		8: return.Color.GRAY
		_: return Color.BLACK

func _input(event):
	if game_over:
		if event.is_action_pressed("restart"):
			restart_game()
		return
	
	if event is InputEventMouseButton and event.pressed:
		var mouse_pos = get_local_mouse_position()
		var grid_x = int(mouse_pos.x / CELL_SIZE)
		var grid_y = int(mouse_pos.y / CELL_SIZE)
		
		if grid_x >= 0 and grid_x < GRID_SIZE and grid_y >= 0 and grid_y < GRID_SIZE:
			if event.button_index == MOUSE_BUTTON_LEFT:
				reveal_cell(grid_x, grid_y)
			elif event.button_index == MOUSE_BUTTON_RIGHT:
				toggle_flag(grid_x, grid_y)

func reveal_cell(x, y):
	if revealed[x][y] or flagged[x][y]:
		return
	
	if first_click:
		first_click = false
		place_mines(x, y)
	
	revealed[x][y] = true
	
	if grid[x][y] == -1:
		game_over = true
		reveal_all_mines()
		print("游戏结束！踩到地雷了！")
	elif grid[x][y] == 0:
		# 自动揭开周围空格
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				var nx = x + dx
				var ny = y + dy
				if nx >= 0 and nx < GRID_SIZE and ny >= 0 and ny < GRID_SIZE:
					if not revealed[nx][ny]:
						reveal_cell(nx, ny)
	
	queue_redraw()
	check_win()

func toggle_flag(x, y):
	if not revealed[x][y]:
		flagged[x][y] = not flagged[x][y]
		queue_redraw()

func reveal_all_mines():
	for x in range(GRID_SIZE):
		for y in range(GRID_SIZE):
			if grid[x][y] == -1:
				revealed[x][y] = true
	queue_redraw()

func check_win():
	var revealed_count = 0
	for x in range(GRID_SIZE):
		for y in range(GRID_SIZE):
			if revealed[x][y]:
				revealed_count += 1
	
	if revealed_count == GRID_SIZE * GRID_SIZE - MINE_COUNT:
		game_over = true
		print("恭喜！你赢了！")

func restart_game():
	game_over = false
	first_click = true
	initialize_grid()
	queue_redraw()
	print("游戏重新开始")

func center_camera():
	var grid_width = GRID_SIZE * CELL_SIZE
	var grid_height = GRID_SIZE * CELL_SIZE
	camera.position = Vector2(grid_width / 2, grid_height / 2)
