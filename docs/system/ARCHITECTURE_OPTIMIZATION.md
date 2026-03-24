# 认知监控架构优化提案

## 当前问题

### 数据流
```
监控脚本(1分钟) → 写入本地history.jsonl → 推送整个文件 → GitHub → CDN → 前端下载整个文件
```

### 问题
1. **推送量大**: 每次推送几百KB的history.jsonl
2. **下载量大**: 前端每次下载几百KB历史数据
3. **延迟高**: CDN缓存5-10分钟，不是实时趋势
4. **API限制**: GitHub API有频率限制

---

## 优化方案 - 增量实时模式

### 核心思路
只推送"当前状态"，前端自己累积历史到 LocalStorage

### 新数据流
```
监控脚本(1分钟) → 生成单条记录
                    ↓
              同时写入两个文件:
                    ├── cognitive-data.json (完整状态，包含当前history数组)
                    └── 可选: trend-data.json (仅最近60条趋势数据)
                    ↓
              推送到GitHub
                    ↓
              前端读取
                    ├── 首次: 读取带history的data.json (或单独trend.json)
                    └── 之后: 只读data.json，本地累积到LocalStorage
```

### 方案A: 前端本地累积 (推荐)

**后端变更 (cognitive_monitor.py):**
- `cognitive-data.json` 保持现状（包含当前状态）
- 新增 `trend-latest.json` - 只包含最近20条趋势点

**前端变更:**
```javascript
// 首次加载: 读取 trend-latest.json (小文件)
// 之后: 每30秒读取 cognitive-data.json (单条)，本地累积到 LocalStorage

const trendData = JSON.parse(localStorage.getItem('cognitive_trend') || '[]');
// 添加新点
trendData.push({timestamp: newData.timestamp, score: newData.cognitive_score});
// 只保留最近60条
trendData = trendData.slice(-60);
localStorage.setItem('cognitive_trend', JSON.stringify(trendData));
```

**优点:**
- 推送量小: 只传最新状态 (1KB vs 几百KB)
- 下载量小: 前端只下载单条 (1KB vs 几百KB)
- 实时性: 无CDN缓存问题
- 安全: 不依赖历史文件同步

### 方案B: 独立趋势接口

**新增 API 端点 (GitHub Pages 无法真正做API，但可以用小文件模拟):**
- `current.json` - 当前状态 (1KB)
- `trend-5m.json` - 最近5分钟趋势 (5条, 几百字节)
- `trend-1h.json` - 最近1小时趋势 (60条, 几KB)

**前端按需加载:**
- 默认显示: 读取 trend-5m.json (实时)
- 切1小时: 读取 trend-1h.json

---

## 推荐实现: 方案A + 优化

### 步骤

1. **修改 cognitive_monitor.py**
   - 保持 `cognitive-data.json` 不变
   - 新增 `trend-data.json` - 只保留最近60条，用于首次加载

2. **修改前端**
   - 首次加载: 读取 `trend-data.json` 初始化 LocalStorage
   - 轮询: 只读取 `cognitive-data.json`，提取当前点加入 LocalStorage
   - 趋势图: 从 LocalStorage 读取渲染

3. **修改推送脚本**
   - 同时推送 `cognitive-data.json` 和 `trend-data.json`
   - 两者都很小，推送快

### 代码示例

**trend-data.json 格式:**
```json
{
  "updated_at": "2026-03-19T12:00:00Z",
  "points": [
    {"t": "12:55", "s": 2},
    {"t": "12:56", "s": 3},
    ...
  ]
}
```

**前端 LocalStorage 累积:**
```javascript
// 每30秒执行
async function updateTrend() {
    const data = await fetch(DATA_URL).then(r => r.json());
    
    // 从 LocalStorage 读取现有趋势
    let trend = JSON.parse(localStorage.getItem('cognitive_trend') || '[]');
    
    // 添加新点 (避免重复)
    const newPoint = {
        timestamp: data.timestamp,
        score: data.cognitive_score
    };
    
    // 检查是否已存在相同时间戳
    const exists = trend.some(p => p.timestamp === newPoint.timestamp);
    if (!exists) {
        trend.push(newPoint);
        // 只保留最近60条
        trend = trend.slice(-60);
        localStorage.setItem('cognitive_trend', JSON.stringify(trend));
    }
    
    // 渲染
    renderTrendChart(trend);
}
```

---

## 实施计划

### 阶段1: 最小改动 (30分钟)
- 修改前端: 使用 LocalStorage 累积，首次从当前 data.json 初始化
- 不需要改后端，不需要改推送
- 效果: 趋势图实时更新，不依赖history.jsonl

### 阶段2: 完整优化 (1小时)
- 后端新增 trend-data.json 生成
- 推送脚本同时推送 trend-data.json
- 前端首次加载 trend-data.json 初始化
- 删除 history.jsonl 推送 (可选，保留作备份)

### 阶段3: 清理 (可选)
- 停止生成 history.jsonl
- 前端完全依赖 LocalStorage

---

需要我先实施**阶段1**（前端LocalStorage累积，最小改动）来验证效果吗？
