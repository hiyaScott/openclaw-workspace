extends Node

# 游戏管理器
class_name GameManager

enum GameState { MENU, PLAYING, PAUSED, LEVEL_COMPLETE, GAME_OVER }

var current_state: GameState = GameState.MENU
var current_level: int = 0
var current_ju: int = 0  # 当前局

# 关卡数据
var level_data: Dictionary = {}
var current_step: int = 0
var steps_data: Array = []

# 信号
signal state_changed(new_state)
signal level_started(level_id)
signal ju_completed(ju_id, stars)
signal step_completed(step_index)
signal show_hint(hint_text, hint_type)

func _ready():
    pass

func start_level(level_id: int):
    current_level = level_id
    current_step = 0
    current_state = GameState.PLAYING
    load_level_data(level_id)
    level_started.emit(level_id)
    state_changed.emit(current_state)

func load_level_data(level_id: int):
    # 从文件加载关卡数据
    var file_path = "res://data/levels/level_%d.json" % level_id
    if FileAccess.file_exists(file_path):
        var file = FileAccess.open(file_path, FileAccess.READ)
        var json = JSON.new()
        json.parse(file.get_as_text())
        level_data = json.get_data()
        steps_data = level_data.get("steps", [])
        file.close()

func check_move(piece, from_pos: Vector2i, to_pos: Vector2i) -> bool:
    if current_step >= steps_data.size():
        return false
    
    var current_step_data = steps_data[current_step]
    var targets = current_step_data.get("target", [])
    
    # 支持单目标或多目标
    if targets is Dictionary:
        targets = [targets]
    
    for target in targets:
        if target is Dictionary:
            if to_pos.x == target.get("x", -1) and to_pos.y == target.get("y", -1):
                return true
    
    return false

func on_piece_moved(piece, from_pos: Vector2i, to_pos: Vector2i):
    if check_move(piece, from_pos, to_pos):
        # 正确的移动
        current_step += 1
        step_completed.emit(current_step - 1)
        
        if current_step >= steps_data.size():
            # 完成本局
            complete_ju()
    else:
        # 错误的移动，显示提示
        show_error_hint()

func complete_ju():
    current_state = GameState.LEVEL_COMPLETE
    state_changed.emit(current_state)
    ju_completed.emit(current_ju, 3)  # 3星完成

func show_error_hint():
    var hints = [
        "不对哦，再想想看？",
        "这个方向走不通，试试别的？",
        "再仔细看看目标位置？",
        "不对，但没关系，再试一次！",
        "想想马走日的规则？"
    ]
    show_hint.emit(hints[randi() % hints.size()], "error")

func get_current_hint() -> Dictionary:
    if current_step < steps_data.size():
        return steps_data[current_step]
    return {}
