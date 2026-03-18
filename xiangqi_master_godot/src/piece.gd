class_name Piece
extends Node2D

enum PieceType { HORSE, CHARIOT, CANNON, ELEPHANT, ADVISOR, GENERAL, SOLDIER }
enum PieceSide { RED, BLACK }

@export var piece_type: PieceType = PieceType.HORSE
@export var piece_side: PieceSide = PieceSide.RED
@export var piece_name: String = "马"

var board_pos: Vector2i = Vector2i.ZERO
var is_selected: bool = false

signal piece_clicked(piece: Piece)

func _ready():
    pass

func select():
    is_selected = true
    scale = Vector2(1.1, 1.1)
    z_index = 10
    queue_redraw()

func deselect():
    is_selected = false
    scale = Vector2(1.0, 1.0)
    z_index = 0
    queue_redraw()

func _input_event(viewport, event, shape_idx):
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        piece_clicked.emit(self)

func _draw():
    # 绘制棋子背景圆
    var bg_color = Color(0.8, 0.2, 0.2) if piece_side == PieceSide.RED else Color(0.2, 0.2, 0.2)
    var border_color = Color(0.9, 0.5, 0.5) if piece_side == PieceSide.RED else Color(0.5, 0.5, 0.5)
    
    # 选中时添加蓝色边框
    if is_selected:
        border_color = Color(0.2, 0.5, 0.9, 0.8)
        draw_circle(Vector2.ZERO, 28, border_color)
    
    # 绘制棋子圆形背景
    draw_circle(Vector2.ZERO, 25, bg_color)
    draw_circle(Vector2.ZERO, 25, border_color, false, 3)
    
    # 绘制文字 - 使用系统字体
    var text_color = Color.WHITE
    var font = ThemeDB.fallback_font
    if font:
        draw_string(
            font,
            Vector2(-12, 8),
            piece_name,
            HORIZONTAL_ALIGNMENT_CENTER,
            -1,
            24,
            text_color
        )
