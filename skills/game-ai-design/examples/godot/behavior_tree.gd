# 行为树基础结构
# 文件：behavior_tree.gd
# 适用于：Godot 4.x

class_name BehaviorTree
extends Node

enum Status { SUCCESS, FAILURE, RUNNING }

func tick(actor: Node, blackboard: Dictionary) -> Status:
	push_error("tick() must be implemented")
	return Status.FAILURE

# ========== 组合节点 ==========

class_name BTSequence
extends BehaviorTree

@export var children: Array[BehaviorTree] = []

func tick(actor: Node, blackboard: Dictionary) -> Status:
	for child in children:
		var status = child.tick(actor, blackboard)
		if status == Status.FAILURE:
			return Status.FAILURE
		if status == Status.RUNNING:
			return Status.RUNNING
	return Status.SUCCESS

class_name BTSelector
extends BehaviorTree

@export var children: Array[BehaviorTree] = []

func tick(actor: Node, blackboard: Dictionary) -> Status:
	for child in children:
		var status = child.tick(actor, blackboard)
		if status == Status.SUCCESS:
			return Status.SUCCESS
		if status == Status.RUNNING:
			return Status.RUNNING
	return Status.FAILURE

class_name BTParallel
extends BehaviorTree

enum Policy { RequireAll, RequireOne }

@export var children: Array[BehaviorTree] = []
@export var success_policy: Policy = Policy.RequireAll
@export var failure_policy: Policy = Policy.RequireOne

func tick(actor: Node, blackboard: Dictionary) -> Status:
	var success_count = 0
	var failure_count = 0
	var running = false
	
	for child in children:
		var status = child.tick(actor, blackboard)
		match status:
			Status.SUCCESS:
				success_count += 1
			Status.FAILURE:
				failure_count += 1
			Status.RUNNING:
				running = true
	
	# 检查失败策略
	if failure_policy == Policy.RequireOne and failure_count > 0:
		return Status.FAILURE
	if failure_policy == Policy.RequireAll and failure_count == children.size():
		return Status.FAILURE
	
	# 检查成功策略
	if success_policy == Policy.RequireOne and success_count > 0:
		return Status.SUCCESS
	if success_policy == Policy.RequireAll and success_count == children.size():
		return Status.SUCCESS
	
	return Status.RUNNING if running else Status.SUCCESS

# ========== 装饰器 ==========

class_name BTInverter
extends BehaviorTree

@export var child: BehaviorTree

func tick(actor: Node, blackboard: Dictionary) -> Status:
	var status = child.tick(actor, blackboard)
	match status:
		Status.SUCCESS: return Status.FAILURE
		Status.FAILURE: return Status.SUCCESS
		_: return status

class_name BTRepeater
extends BehaviorTree

@export var child: BehaviorTree
@export var repeat_count: int = -1  # -1 = 无限
@export var repeat_forever: bool = false

var current_count: int = 0

func tick(actor: Node, blackboard: Dictionary) -> Status:
	if repeat_count > 0 and current_count >= repeat_count:
		return Status.SUCCESS
	
	var status = child.tick(actor, blackboard)
	
	if status != Status.RUNNING:
		current_count += 1
	
	if repeat_forever or (repeat_count > 0 and current_count < repeat_count):
		return Status.RUNNING
	
	return status

class_name BTAlwaysSucceed
extends BehaviorTree

@export var child: BehaviorTree

func tick(actor: Node, blackboard: Dictionary) -> Status:
	child.tick(actor, blackboard)
	return Status.SUCCESS

class_name BTAlwaysFail
extends BehaviorTree

@export var child: BehaviorTree

func tick(actor: Node, blackboard: Dictionary) -> Status:
	child.tick(actor, blackboard)
	return Status.FAILURE

# ========== 叶子节点 ==========

class_name BTAction
extends BehaviorTree

var action_callable: Callable

func _init(callable: Callable = Callable()):
	action_callable = callable

func tick(actor: Node, blackboard: Dictionary) -> Status:
	if action_callable.is_valid():
		return action_callable.call(actor, blackboard)
	return Status.FAILURE

class_name BTCondition
extends BehaviorTree

var condition_callable: Callable

func _init(callable: Callable = Callable()):
	condition_callable = callable

func tick(actor: Node, blackboard: Dictionary) -> Status:
	if condition_callable.is_valid():
		if condition_callable.call(actor, blackboard):
			return Status.SUCCESS
	return Status.FAILURE

class_name BTWait
extends BehaviorTree

@export var wait_time: float = 1.0

var timer: float = 0.0

func tick(actor: Node, blackboard: Dictionary) -> Status:
	timer += blackboard.get("delta", 0.0)
	if timer >= wait_time:
		timer = 0.0
		return Status.SUCCESS
	return Status.RUNNING
