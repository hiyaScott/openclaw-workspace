class_name SoundManager
extends Node

# 音效类型
enum SoundType {
    SELECT,     # 选择棋子
    MOVE,       # 移动棋子
    CAPTURE,    # 吃子
    SUCCESS,    # 成功
    ERROR,      # 错误
    CLICK       # 点击按钮
}

# 音频播放器
var audio_players: Dictionary = {}
var sound_enabled: bool = true

# 音频流缓存
var sound_cache: Dictionary = {}

func _ready():
    # 为每种音效类型创建 AudioStreamPlayer
    for sound_type in SoundType.values():
        var player = AudioStreamPlayer.new()
        player.name = "SoundPlayer_%d" % sound_type
        add_child(player)
        audio_players[sound_type] = player
    
    # 预生成所有音效
    _generate_all_sounds()

func _generate_all_sounds():
    # 生成并缓存所有音效
    sound_cache[SoundType.SELECT] = _generate_select_sound()
    sound_cache[SoundType.MOVE] = _generate_move_sound()
    sound_cache[SoundType.CAPTURE] = _generate_capture_sound()
    sound_cache[SoundType.SUCCESS] = _generate_success_sound()
    sound_cache[SoundType.ERROR] = _generate_error_sound()
    sound_cache[SoundType.CLICK] = _generate_click_sound()

func _generate_select_sound() -> AudioStreamWAV:
    # 选择音效：短促的高音
    return _create_tone(800, 0.1, 0.3, true)

func _generate_move_sound() -> AudioStreamWAV:
    # 移动音效：中等音调
    return _create_tone(600, 0.15, 0.2, true)

func _generate_capture_sound() -> AudioStreamWAV:
    # 吃子音效：低音，稍长
    return _create_tone(400, 0.2, 0.4, true)

func _generate_success_sound() -> AudioStreamWAV:
    # 成功音效：上升音阶 C5-E5-G5-C6
    var sample_rate = 44100
    var duration = 0.4
    var samples = int(sample_rate * duration)
    var data = PackedByteArray()
    data.resize(samples * 2)  # 16-bit stereo
    
    var notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    var note_duration = int(samples / notes.size())
    
    for i in range(samples):
        var note_index = i / note_duration
        var note_idx = int(note_index)
        if note_idx >= notes.size():
            note_idx = notes.size() - 1
        
        var freq = notes[note_idx]
        var t = float(i % note_duration) / sample_rate
        var envelope = 1.0 - (float(i % note_duration) / note_duration)
        envelope = pow(envelope, 2)
        
        var value = int(sin(t * freq * 2 * PI) * 3000 * envelope)
        value = clamp(value, -32768, 32767)
        
        data.encode_s16(i * 2, value)
        data.encode_s16(i * 2 + 1, value)
    
    var stream = AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.stereo = true
    stream.mix_rate = sample_rate
    stream.data = data
    return stream

func _generate_error_sound() -> AudioStreamWAV:
    # 错误音效：下降音调
    return _create_tone(200, 0.2, 0.3, false)

func _generate_click_sound() -> AudioStreamWAV:
    # 点击音效：短促
    return _create_tone(1000, 0.05, 0.2, true)

func _create_tone(start_freq: float, duration: float, volume: float, rising: bool) -> AudioStreamWAV:
    var sample_rate = 44100
    var samples = int(sample_rate * duration)
    var data = PackedByteArray()
    data.resize(samples * 2)  # 16-bit stereo
    
    for i in range(samples):
        var t = float(i) / sample_rate
        var progress = float(i) / samples
        
        var freq = start_freq
        if rising:
            freq = start_freq * (1.0 - progress * 0.5)  # 下降
        else:
            freq = start_freq * (1.0 - progress * 0.25)  # 缓慢下降
        
        var envelope = 1.0 - progress
        envelope = pow(envelope, 2)
        
        var value = int(sin(t * freq * 2 * PI) * 3000 * volume * envelope)
        value = clamp(value, -32768, 32767)
        
        data.encode_s16(i * 2, value)
        data.encode_s16(i * 2 + 1, value)
    
    var stream = AudioStreamWAV.new()
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    stream.stereo = true
    stream.mix_rate = sample_rate
    stream.data = data
    return stream

func play_sound(sound_type: SoundType):
    if not sound_enabled:
        return
    
    if audio_players.has(sound_type) and sound_cache.has(sound_type):
        var player = audio_players[sound_type]
        player.stream = sound_cache[sound_type]
        player.play()

func toggle_sound():
    sound_enabled = not sound_enabled
    return sound_enabled

func set_sound_enabled(enabled: bool):
    sound_enabled = enabled
