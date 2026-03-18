extends Node2D

@onready var board = $Board
@onready var game_manager = $GameManager
@onready var sound_manager = $SoundManager
@onready var pieces_container = $Board/Pieces
@onready var hint_marker = $Board/HintMarker
@onready var max_character = $UI/MaxCharacter
@onready var ju_success_panel = $UI/JuSuccessPanel

# UI 引用
@onready var level_label = $UI/TopBar/LevelLabel
@onready var progress_label = $UI/TopBar/ProgressLabel
@onready var progress_bar = $UI/TopBar/ProgressBar
@onready var tag_label = $UI/JuInfoPanel/TagLabel
@onready var name_label = $UI/JuInfoPanel/NameLabel
@onready var desc_label = $UI/JuInfoPanel/DescLabel
@onready var reset_button = $UI/ActionButtons/ResetButton
@onready var hint_button = $UI/ActionButtons/HintButton
@onready var sound_button = $UI/ActionButtons/SoundButton

var piece_scene = preload("res://scenes/piece.tscn")
var current_level_data: Dictionary = {}
var current_ju_index: int = 0
var selected_piece: Piece = null
var total_jus: int = 10

func _ready():
    # 连接信号
    board.piece_moved.connect(_on_piece_moved)
    game_manager.step_completed.connect(_on_step_completed)
    game_manager.ju_completed.connect(_on_ju_completed)
    game_manager.show_hint.connect(_on_show_hint)
    
    # UI 按钮连接
    reset_button.pressed.connect(_on_reset)
    hint_button.pressed.connect(_on_show_hint_button)
    sound_button.pressed.connect(_on_toggle_sound)
    
    # 结算面板信号
    ju_success_panel.continue_pressed.connect(_on_next_ju)
    ju_success_panel.replay_pressed.connect(_on_reset)
    ju_success_panel.share_pressed.connect(_on_share)
    
    # 开始第一关
    start_level(1)

func start_level(level_id: int):
    game_manager.start_level(level_id)
    current_ju_index = 0
    load_level_data(level_id)
    setup_ju()

func load_level_data(level_id: int):
    var file_path = "res://data/levels/level_%d.json" % level_id
    if FileAccess.file_exists(file_path):
        var file = FileAccess.open(file_path, FileAccess.READ)
        var json = JSON.new()
        json.parse(file.get_as_text())
        current_level_data = json.get_data()
        file.close()

func setup_ju():
    if current_level_data.is_empty():
        return
    
    # 清除现有棋子
    for child in pieces_container.get_children():
        child.queue_free()
    
    # 更新UI
    update_ui()
    
    # 创建棋子
    if current_level_data.has("pieces"):
        for piece_data in current_level_data.pieces:
            create_piece(piece_data)
    
    # 显示提示标记
    update_hint_markers()
    
    # 显示Max消息
    if current_level_data.has("steps") and current_level_data.steps.size() > 0:
        var step = current_level_data.steps[0]
        if step.has("hintText"):
            max_character.set_message(step.hintText)

func create_piece(data: Dictionary):
    var piece = piece_scene.instantiate()
    piece.piece_type = data.get("type", Piece.PieceType.HORSE)
    piece.piece_side = data.get("side", Piece.PieceSide.RED)
    piece.piece_name = data.get("name", "马")
    
    var pos = Vector2i(data.x, data.y)
    board.place_piece(piece, pos)
    pieces_container.add_child(piece)
    
    # 连接点击信号
    piece.piece_clicked.connect(_on_piece_clicked)

func update_ui():
    if current_level_data.is_empty():
        return
    
    # 更新顶部信息
    level_label.text = "第一章 · 棋子移动 · %s" % current_level_data.get("name", "")
    progress_label.text = "%d / %d 局" % [current_ju_index + 1, total_jus]
    progress_bar.max_value = total_jus
    progress_bar.value = current_ju_index + 1
    
    # 更新局信息
    tag_label.text = "📚 %s" % ("教学" if current_ju_index < 3 else ("练习" if current_ju_index < 6 else "巩固"))
    name_label.text = current_level_data.get("name", "")
    desc_label.text = current_level_data.get("description", "")

func update_hint_markers():
    if current_level_data.is_empty() or not current_level_data.has("steps"):
        hint_marker.clear()
        return
    
    var step_index = game_manager.current_step
    if step_index >= current_level_data.steps.size():
        hint_marker.clear()
        return
    
    var step = current_level_data.steps[step_index]
    var hint_type_str = step.get("hintType", "precise")
    var hint_type = HintMarker.HintType.PRECISE
    
    match hint_type_str:
        "precise":
            hint_type = HintMarker.HintType.PRECISE
        "vague":
            hint_type = HintMarker.HintType.VAGUE
        "text", "none":
            hint_type = HintMarker.HintType.NONE
    
    var targets = step.get("target", [])
    var target_positions: Array[Vector2i] = []
    
    if targets is Dictionary:
        target_positions.append(Vector2i(targets.x, targets.y))
    elif targets is Array:
        for t in targets:
            if t is Dictionary:
                target_positions.append(Vector2i(t.x, t.y))
    
    hint_marker.setup(hint_type, target_positions, board.board_offset, board.CELL_SIZE)

func _on_piece_clicked(piece: Piece):
    if selected_piece == piece:
        piece.deselect()
        selected_piece = null
        sound_manager.play_sound(SoundManager.SoundType.CLICK)
        return
    
    if selected_piece:
        selected_piece.deselect()
    
    # 只能选择红方棋子
    if piece.piece_side == Piece.PieceSide.RED:
        piece.select()
        selected_piece = piece
        sound_manager.play_sound(SoundManager.SoundType.SELECT)
        
        # 显示可移动指示器
        show_move_indicators(piece)

func show_move_indicators(piece: Piece):
    # 清除之前的指示器
    for child in board.get_children():
        if child.name.begins_with("MoveIndicator"):
            child.queue_free()
    
    if piece.piece_type == Piece.PieceType.HORSE:
        var moves = board.get_horse_valid_moves(piece.board_pos)
        for move in moves:
            var indicator = Node2D.new()
            indicator.name = "MoveIndicator"
            indicator.position = board.grid_to_world(move)
            indicator.z_index = 3
            indicator.set_script(load("res://src/move_indicator.gd"))
            board.add_child(indicator)

func _input(event):
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if selected_piece:
            var click_pos = get_global_mouse_position()
            var grid_pos = board.world_to_grid(click_pos)
            
            if board.is_valid_position(grid_pos):
                var target_piece = board.get_piece_at(grid_pos)
                
                # 检查是否是有效移动
                if board.is_valid_horse_move(selected_piece.board_pos, grid_pos):
                    var from_pos = selected_piece.board_pos
                    var is_capture = target_piece != null and target_piece.piece_side == Piece.PieceSide.BLACK
                    
                    # 执行移动
                    board.move_piece(from_pos, grid_pos)
                    
                    # 播放音效
                    if is_capture:
                        sound_manager.play_sound(SoundManager.SoundType.CAPTURE)
                    else:
                        sound_manager.play_sound(SoundManager.SoundType.MOVE)
                    
                    # 清除移动指示器
                    for child in board.get_children():
                        if child.name.begins_with("MoveIndicator"):
                            child.queue_free()
                    
                    selected_piece.deselect()
                    selected_piece = null
                else:
                    # 无效移动
                    sound_manager.play_sound(SoundManager.SoundType.ERROR)
                    max_character.set_message("不对哦，再想想看？马走日字，注意不要被绊马脚！")

func _on_piece_moved(from_pos, to_pos, piece):
    # 检查是否完成当前步骤
    if game_manager.check_move(piece, from_pos, to_pos):
        game_manager.on_piece_moved(piece, from_pos, to_pos)
    else:
        # 虽然移动合法，但不是目标位置
        sound_manager.play_sound(SoundManager.SoundType.ERROR)
        max_character.set_message("这个方向走不通，试试别的目标？")

func _on_step_completed(step_index):
    update_hint_markers()
    
    # 显示步骤完成消息
    if current_level_data.has("steps") and step_index < current_level_data.steps.size():
        var step = current_level_data.steps[step_index]
        if step.has("msg") and step.msg != "":
            max_character.set_message(step.msg)

func _on_ju_completed(ju_id, stars):
    sound_manager.play_sound(SoundManager.SoundType.SUCCESS)
    ju_success_panel.show_success()

func _on_show_hint(hint_text, hint_type):
    max_character.set_message(hint_text)

func _on_show_hint_button():
    sound_manager.play_sound(SoundManager.SoundType.CLICK)
    if current_level_data.has("steps") and game_manager.current_step < current_level_data.steps.size():
        var step = current_level_data.steps[game_manager.current_step]
        var hint = step.get("hintText", "再仔细看看目标位置？")
        max_character.set_message(hint)

func _on_reset():
    sound_manager.play_sound(SoundManager.SoundType.CLICK)
    game_manager.current_step = 0
    setup_ju()

func _on_next_ju():
    sound_manager.play_sound(SoundManager.SoundType.CLICK)
    current_ju_index += 1
    
    if current_ju_index < total_jus:
        start_level(current_ju_index + 1)
    else:
        # 所有局完成
        max_character.set_message("恭喜！你已完成所有关卡！")

func _on_share():
    sound_manager.play_sound(SoundManager.SoundType.CLICK)
    max_character.set_message("分享功能开发中...")

func _on_toggle_sound():
    var enabled = sound_manager.toggle_sound()
    sound_button.text = "🔊" if enabled else "🔇"
    if enabled:
        sound_manager.play_sound(SoundManager.SoundType.CLICK)
