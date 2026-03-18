class_name JuSuccessPanel
extends Control

signal continue_pressed
signal replay_pressed
signal share_pressed

@onready var title_label = $Panel/Content/Header/TitleLabel
@onready var check_icon = $Panel/Content/Header/CheckIcon
@onready var continue_button = $Panel/Content/ContinueButton
@onready var replay_button = $Panel/Content/Header/ActionButtons/ReplayButton
@onready var share_button = $Panel/Content/Header/ActionButtons/ShareButton

var success_texts = ["泰裤辣！", "太棒了！", "完美！", "厉害！", "牛啊！"]

func _ready():
    visible = false
    
    if continue_button:
        continue_button.pressed.connect(_on_continue)
    if replay_button:
        replay_button.pressed.connect(_on_replay)
    if share_button:
        share_button.pressed.connect(_on_share)

func show_success():
    # 随机选择成功文本
    if title_label:
        title_label.text = success_texts[randi() % success_texts.size()]
    
    visible = true
    
    # 滑入动画
    var panel = $Panel
    panel.position.y = panel.size.y
    
    var tween = create_tween()
    tween.tween_property(panel, "position:y", 0, 0.3).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)

func hide():
    var panel = $Panel
    
    var tween = create_tween()
    tween.tween_property(panel, "position:y", panel.size.y, 0.2).set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
    
    await tween.finished
    visible = false

func _on_continue():
    continue_pressed.emit()
    hide()

func _on_replay():
    replay_pressed.emit()
    hide()

func _on_share():
    share_pressed.emit()
