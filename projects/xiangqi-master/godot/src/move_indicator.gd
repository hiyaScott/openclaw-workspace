extends Node2D

func _draw():
    # 绘制绿色脉冲圆点
    var color = Color(0.2, 0.7, 0.2, 0.6)
    draw_circle(Vector2.ZERO, 8, color)
    draw_circle(Vector2.ZERO, 8, Color(0.1, 0.5, 0.1, 0.8), false, 2)

func _process(delta):
    # 简单的脉冲动画
    var scale_val = 1.0 + sin(Time.get_time_dict_from_system()["second"] * 5) * 0.1
    scale = Vector2(scale_val, scale_val)
