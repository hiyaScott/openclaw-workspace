extends Button

# 扫雷格子脚本

signal cell_revealed(x, y)
signal cell_flagged

var grid_x: int = 0
var grid_y: int = 0
var is_mine: bool = false
var is_revealed: bool = false
var is_flagged: bool = false
var neighbor_mines: int = 0

@onready var label = $Label

func _ready():
	custom_minimum_size = Vector2(40, 40)
	update_appearance()

func _gui_input(event):
	if is_revealed:
		return
	
	if event is InputEventMouseButton:
		if event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				if not is_flagged:
					reveal()
			elif event.button_index == MOUSE_BUTTON_RIGHT:
				toggle_flag()

func toggle_flag():
	if is_revealed:
		return
	
	is_flagged = !is_flagged
	update_appearance()
	cell_flagged.emit()

func reveal():
	if is_revealed or is_flagged:
		return
	
	is_revealed = true
	update_appearance()
	cell_revealed.emit(grid_x, grid_y)

func update_appearance():
	if is_flagged:
		text = "🚩"
		modulate = Color.ORANGE
	elif is_revealed:
		if is_mine:
			text = "💣"
			modulate = Color.RED
		else:
			if neighbor_mines > 0:
				text = str(neighbor_mines)
				# 根据数字设置不同颜色
				match neighbor_mines:
					1: modulate = Color.BLUE
					2: modulate = Color.GREEN
					3: modulate = Color.RED
					4: modulate = Color.PURPLE
					5: modulate = Color.MAROON
					6: modulate = Color.TURQUOISE
					7: modulate = Color.BLACK
					8: modulate = Color.GRAY
				_:
					modulate = Color.WHITE
			else:
				text = ""
				modulate = Color.LIGHT_GRAY
	else:
		text = ""
		modulate = Color.DARK_GRAY
