# 实验短片 004 v3 - 音频优化版

## v3 音频系统重构

### 主要改进

#### 1. 防破音压缩器
```javascript
masterCompressor.threshold.value = -12;  // 阈值 -12dB
masterCompressor.ratio.value = 4;          // 压缩比 4:1
masterCompressor.attack.value = 0.01;      // 快速攻击
masterCompressor.release.value = 0.1;      // 快速释放
```
- 所有音频信号经过压缩器处理
- 有效防止削波和破音
- 特别适合手机扬声器

#### 2. BGM与音效分离
```
音频信号流:
BGM(背景音乐) ─┐
               ├─→ Compressor ─→ MasterGain ─→ Output
SFX(音效) ─────┘
```

- **BGM通道**: 持续铺垫音、旋律
- **SFX通道**: 场景切换音效、交互音
- 独立音量控制: BGM 60%, SFX 40%

#### 3. 声音数量限制
```javascript
const MAX_CONCURRENT_SOUNDS = 6;
```
- 限制同时播放的声音数量
- 自动清理旧节点
- 避免音频堆叠过载

#### 4. 频率优化
- 移除过低频率(C2以下)
- 最低频率从 C3 (130Hz) 开始
- 避免手机扬声器低频失真

#### 5. 波形选择
| 用途 | 波形 | 原因 |
|------|------|------|
| BGM铺垫 | sine | 最柔和,无谐波 |
| 旋律 | triangle | 柔和但有色彩 |
| 音效 | sine/triangle | 短促清晰 |

#### 6. 音量控制
- 主音量: 50%
- BGM音量: 60%
- SFX音量: 40%
- 单个音符: 最大25%

---

*实验短片 004 v3 | 音频优化版 | 2026-03-25*
