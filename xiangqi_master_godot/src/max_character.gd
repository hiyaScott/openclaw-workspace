class_name MaxCharacter
extends Control

@onready var texture_rect = $TextureRect
@onready var bubble = $Bubble
@onready var message_label = $Bubble/MessageLabel

var max_texture: Texture2D

func _ready():
    # 加载Max角色图片
    max_texture = load("res://assets/max_character.jpg")
    if texture_rect and max_texture:
        texture_rect.texture = max_texture
    
    # 初始隐藏对话框
    if bubble:
        bubble.visible = false

func show_message(text: String, duration: float = 3.0):
    if message_label:
        message_label.text = text
    if bubble:
        bubble.visible = true
    
    # 自动隐藏
    await get_tree().create_timer(duration).timeout
    hide_message()

func hide_message():
    if bubble:
        bubble.visible = false

func set_message(text: String):
    if message_label:
        message_label.text = text
    if bubble:
        bubble.visible = true

func show_happy():
    # 可以添加动画效果
    var tween = create_tween()
    tween.tween_property(self, "scale", Vector2(1.1, 1.1), 0.2)
    tween.tween_property(self, "scale", Vector2(1.0, 1.0), 0.2)
