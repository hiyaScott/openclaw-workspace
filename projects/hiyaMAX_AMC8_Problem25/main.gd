extends Node2D

# hiyaMAX AMC8 Problem 25 - Video Player Controller
# Resolution: 1080x1920 (9:16 Vertical)

@onready var video_player = $VideoPlayer
@onready var audio_player = $AudioStreamPlayer
@onready var subtitle_label = $SubtitleLabel

var current_scene = 0
var scenes = [
	{"name": "opening", "duration": 3.0, "subtitle": ""},
	{"name": "question", "duration": 5.0, "subtitle": "关键词是\"保证\""},
	{"name": "thinking", "duration": 12.0, "subtitle": "最坏情况：每种颜色拿2个"},
	{"name": "sixballs", "duration": 15.0, "subtitle": "第7个球一定会让某一种变成3个！"},
	{"name": "sevenballs", "duration": 10.0, "subtitle": ""},
	{"name": "answer", "duration": 10.0, "subtitle": "答案是7"},
	{"name": "ending", "duration": 5.0, "subtitle": "记住：最坏情况+1"}
]

func _ready():
	print("hiyaMAX AMC8 Problem 25 - Started")
	play_scene(0)

func play_scene(index):
	if index >= scenes.size():
		print("Video complete!")
		return
	
	current_scene = index
	var scene = scenes[index]
	subtitle_label.text = scene.subtitle
	
	# Load scene image
	var image_path = "res://assets/%02d_%s.png" % [index + 1, scene.name]
	print("Loading: " + image_path)
	
	# Wait for duration
	await get_tree().create_timer(scene.duration).timeout
	play_scene(index + 1)
