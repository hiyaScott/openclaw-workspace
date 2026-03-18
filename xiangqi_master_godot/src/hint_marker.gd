class_name HintMarker
extends Node2D

enum HintType {
    PRECISE,    # 精确提示：虚线绿圈
    VAGUE,      # 模糊提示：淡黄色圆点
    TEXT,       # 文字提示：无标记
    NONE        # 无提示
}

var hint_type: HintType = HintType.PRECISE
var target_positions: Array[Vector2i] = []
var board_offset: Vector2 = Vector2.ZERO
var cell_size: float = 60.0

func _ready():
    z_index = 5  # 在棋子下方

func setup(type: HintType, positions: Array[Vector2i], offset: Vector2, size: float):
    hint_type = type
    target_positions = positions
    board_offset = offset
    cell_size = size
    queue_redraw()

func clear():
    target_positions.clear()
    queue_redraw()

func _draw():
    if hint_type == HintType.TEXT or hint_type == HintType.NONE:
        return
    
    for pos in target_positions:
        var world_pos = board_offset + Vector2(pos.x * cell_size, pos.y * cell_size)
        
        match hint_type:
            HintType.PRECISE:
                _draw_dashed_circle(world_pos, 25)
            HintType.VAGUE:
                _draw_faint_dot(world_pos, 15)

func _draw_dashed_circle(center: Vector2, radius: float):
    var color = Color(0.2, 0.8, 0.2, 0.8)  # 绿色
    var dash_length = 8.0
    var gap_length = 4.0
    var circumference = 2 * PI * radius
    var num_dashes = int(circumference / (dash_length + gap_length))
    
    for i in range(num_dashes):
        var start_angle = i * (dash_length + gap_length) / radius
        var end_angle = start_angle + dash_length / radius
        
        var points = PackedVector2Array()
        var segments = 8
        for j in range(segments + 1):
            var angle = start_angle + (end_angle - start_angle) * j / segments
            points.append(center + Vector2(cos(angle), sin(angle)) * radius)
        
        for j in range(points.size() - 1):
            draw_line(points[j], points[j + 1], color, 3.0)

func _draw_faint_dot(center: Vector2, radius: float):
    var color = Color(1.0, 0.9, 0.4, 0.4)  # 淡黄色
    draw_circle(center, radius, color)
    draw_circle(center, radius, Color(1.0, 0.8, 0.2, 0.6), false, 2.0)
