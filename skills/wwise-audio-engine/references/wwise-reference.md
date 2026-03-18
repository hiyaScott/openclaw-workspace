# Wwise 参考资料

## 官方文档

- Wwise Fundamentals Guide
- Wwise SDK 帮助文档
- Wwise Authoring API 参考

## 学习资源

- Audiokinetic Learn：https://www.audiokinetic.com/education/learn-wwise/
- Wwise-101 认证课程
- Wwise Project Adventure 教程

## 技术对比

### Wwise vs FMOD

| 特性 | Wwise | FMOD |
|------|-------|------|
| 界面结构 | Tree-driven | Timeline-first |
| 学习曲线 | 较陡 | 较平缓 |
| 授权模式 | 按项目收费 | 免费/按收入收费 |
| 中间件地位 | 行业标准 | 广泛使用 |
| 脚本语言 | LUA | 类似 DAW |

## 性能指标参考

### 移动端内存预算
- 短音效：加载到 RAM
- 音乐：流式播放
- 总内存：根据平台 10-50MB

### 主机平台
- 更多内存预算
- 支持更复杂的混音
- 可同时处理更多声道

## 常见事件命名规范

```
Play_[Object]_[Action]
Stop_[Object]_[Action]
SetState_[Group]_[State]
SetSwitch_[Group]_[Switch]
```

示例：
- Play_Footstep_Concrete
- Play_Weapon_Gun_Fire
- SetState_Music_Combat
- SetSwitch_Footstep_Material_Grass
