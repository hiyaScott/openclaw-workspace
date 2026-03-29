# 音频设计参考资源

## Web Audio API 资源

### 官方文档
- **Web Audio API MDN**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
- **Web Audio API 规范**: https://webaudio.github.io/web-audio-api/

### 教程与学习
- **Web Audio API 入门教程**: MDN 上的完整指南
- **HTML5 Rocks 音频文章**: 基础概念和最佳实践

### 开源库
- **Howler.js**: 现代 Web 音频库，简化 Web Audio API 使用
- **Tone.js**: 用于交互式音乐的 Web Audio 框架
- **Pizzicato.js**: 音频效果处理库

---

## Wwise 资源

### Audiokinetic 官方
- **Wwise 官网**: https://www.audiokinetic.com/
- **Wwise 学习资源**: https://www.audiokinetic.com/education/learn-wwise/
- **Wwise 文档中心**: https://www.audiokinetic.com/library/edge/
- **Wwise Fundamentals Guide**: 官方入门教程

### Wwise 2024.1 for Godot 专项资源

#### GitHub 仓库
- **wwise-godot-integration**: https://github.com/alessandrofama/wwise-godot-integration
  - 官方 GDExtension 集成
  - 包含源代码、构建脚本和文档
  - 支持 Windows、macOS、Linux、Android、iOS
- **Releases 下载**: https://github.com/alessandrofama/wwise-godot-integration/releases
  - 当前推荐版本: Wwise 2024.1.9 for Godot (支持 Godot 4.3/4.4/4.5)

#### 官方博客与文档
- **What's New in Wwise 2024.1 for Godot**: https://www.audiokinetic.com/en/blog/whats-new-in-wwise-2024.1-for-godot/
  - 详细介绍 WwiseProjectDatabase、Wwise Types、Auto-Defined SoundBanks 等新特性
- **Audiokinetic Wwise now fully compatible with Godot 4.3**: https://blog.blips.fm/articles/audiokinetic-wwise-now-fully-compatible-with-godot-43
  - 第三方对 Wwise 2024.1 for Godot 的介绍

#### 技术文档
- **Auto-Defined SoundBanks**: https://www.audiokinetic.com/en/public-library/2025.1.5_9095/?source=Help&id=auto_defining_soundbank
- **SoundBanks Settings**: https://www.audiokinetic.com/library/edge/?source=Help&id=soundbank_settings_soundbanks_tab
- **Wwise 2024.1 What's New**: https://www.audiokinetic.com/en/blog/wwise2024.1-whats-new/

#### 视频教程
- **Wwise Up On Air - Auto Defined SoundBanks**: https://www.audiokinetic.com/en/learning/videos/zq0amgosoje/
  - 官方视频教程，讲解 Auto-Defined SoundBanks 的使用

### 版本兼容性

| Wwise 版本 | Godot 版本 | 集成版本 |
|-----------|-----------|---------|
| 2025.1.3 | 4.3, 4.4, 4.5 | 最新 |
| 2024.1.9 | 4.3, 4.4, 4.5 | 推荐 |
| 2024.1.8 | 4.3, 4.4, 4.5 | 稳定 |
| 2024.1.3 | 4.3, 4.4 | 稳定 |
| 2024.1.1 | 4.3 | 稳定 |

### 新特性支持矩阵

| 特性 | 2023.1 | 2024.1+ |
|------|--------|---------|
| WAAPI | ✅ | ✅ (向后兼容) |
| WwiseProjectDatabase | ❌ | ✅ |
| Wwise Types | ❌ | ✅ |
| Auto-Defined SoundBanks | ❌ | ✅ |
| 简化插件支持 | ❌ | ✅ |
| 引擎内文档 | ❌ | ✅ |
| Wwise 对象作为资源 | ❌ | ✅ |

### 社区资源

- **Audiokinetic 官方 Discord**: 包含 Wwise Godot 频道
- **GitHub Issues**: https://github.com/alessandrofama/wwise-godot-integration/issues

### 许可信息

- **Wwise**: Audiokinetic 提供免费的独立开发者许可
- **集成**: 查看 GitHub 仓库中的 LICENSE 文件了解集成代码许可

---

## 通用音频资源

### 专业书籍
- **Game Audio Implementation - Guy Somberg**: https://www.routledge.com/Game-Audio-Implementation/Somberg/p/book/9781138013203
- **The Game Audio Tutorial - Richard Stevens**: https://www.routledge.com/The-Game-Audio-Tutorial/Stevens-Raybould/p/book/9781138093946

### 会议与演讲
- **GDC Audio Talks**: https://www.gdcvault.com/free/audio

### 音频资源网站
- **Freesound.org**: 免费音效社区
- **Epidemic Sound**: 高质量音乐授权
- **Artlist**: 音乐和视频素材
- **AudioJungle**: 音频素材市场

---

## 技术对比

### Wwise vs FMOD

| 特性 | Wwise | FMOD |
|------|-------|------|
| 界面结构 | Tree-driven | Timeline-first |
| 学习曲线 | 较陡 | 较平缓 |
| 授权模式 | 按项目收费 | 免费/按收入收费 |
| 中间件地位 | 行业标准 | 广泛使用 |
| 脚本语言 | LUA | 类似 DAW |

### Web Audio vs 音频中间件

| 特性 | Web Audio API | Wwise/FMOD |
|------|---------------|------------|
| 运行环境 | 浏览器 | 原生应用 |
| 功能复杂度 | 基础-中等 | 专业级 |
| 学习成本 | 低 | 高 |
| 适用项目 | Web游戏、H5 | 中大型游戏 |
| 授权费用 | 免费 | 商业授权 |

---

## 性能指标参考

### 移动端内存预算
- 短音效：加载到 RAM
- 音乐：流式播放
- 总内存：根据平台 10-50MB

### 主机平台
- 更多内存预算
- 支持更复杂的混音
- 可同时处理更多声道

---

## 命名规范参考

### Wwise 事件命名
```
Play_[Object]_[Action]
Stop_[Object]_[Action]
SetState_[Group]_[State]
SetSwitch_[Group]_[Switch]
```

示例：
- `Play_Footstep_Concrete`
- `Play_Weapon_Gun_Fire`
- `SetState_Music_Combat`
- `SetSwitch_Footstep_Material_Grass`

---

## 快速链接

**Web Audio API:**
- MDN 文档: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

**Wwise for Godot:**
- 下载集成: https://github.com/alessandrofama/wwise-godot-integration/releases
- 官方博客 (2024.1 新特性): https://www.audiokinetic.com/en/blog/whats-new-in-wwise-2024.1-for-godot/
- Wwise 学习中心: https://www.audiokinetic.com/education/learn-wwise/
