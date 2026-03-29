# Excel分析模板使用说明

## 模板概述

本目录提供游戏数据分析的Excel模板，帮助非技术团队快速进行数据分析和可视化。

## 模板文件说明

### 1. 留存分析模板 (retention_analysis.xlsx)

#### 数据输入工作表 (Data_Input)

| 字段 | 说明 | 示例 |
|------|------|------|
| user_id | 用户唯一标识 | U001, U002 |
| registration_date | 注册日期 | 2024/1/15 |
| active_date | 活跃日期 | 2024/1/16 |

#### 分析步骤

1. **数据准备**
   - 在Data_Input工作表中粘贴用户活跃数据
   - 确保日期格式统一为 YYYY/MM/DD

2. **同群计算**
   - 打开 "Cohort_Calculation" 工作表
   - 使用数据透视表功能：
     - 行：注册日期
     - 列：活跃日期与注册日期的天数差
     - 值：去重计数 user_id

3. **留存率计算**
   - 在 "Retention_Rate" 工作表
   - 公式：`当日活跃用户数 / 该群注册用户数`
   - 使用条件格式设置热力图颜色

4. **可视化**
   - "Charts" 工作表已预设留存曲线图
   - 数据更新后图表自动刷新

#### 关键公式

```excel
# 计算天数差
=active_date - registration_date

# 计算留存率（假设B2为当日活跃数，$A$2为注册数）
=B2/$A$2

# 格式化百分比
=TEXT(C2,"0.0%")
```

---

### 2. LTV预测模板 (ltv_calculator.xlsx)

#### 参数设置 (Parameters)

| 参数 | 说明 | 示例值 |
|------|------|--------|
| 首日ARPU | 第1天每用户收入 | 0.5 |
| D1留存率 | 次日留存 | 40% |
| D7留存率 | 7日留存 | 15% |
| D30留存率 | 30日留存 | 8% |
| ARPU增长率 | 每日ARPU增长 | 2% |

#### LTV计算工作表 (LTV_Calculation)

使用以下公式计算各日贡献：

```excel
# 第N日收入贡献
=首日ARPU * (1+ARPU增长率)^N * D_N留存率

# 累计LTV (前N天)
=SUM(C2:C(N+1))
```

#### 预测方法

**方法1：留存曲线法**
1. 输入实际留存率数据（前30天）
2. 对后续天数使用指数衰减公式预测
3. 公式：`=D30留存率 * POWER(0.95, N-30)`

**方法2：曲线拟合法**
1. 在"Curve_Fit"工作表使用实际留存数据
2. 添加指数趋势线
3. 显示公式：y = a * e^(-bx)
4. 使用该公式预测后续留存

---

### 3. RFM分群模板 (rfm_segmentation.xlsx)

#### 数据输入 (User_Data)

| 字段 | 说明 |
|------|------|
| user_id | 用户ID |
| last_purchase_date | 最后购买日期 |
| purchase_count | 购买次数 |
| total_spent | 总消费金额 |

#### RFM计算步骤

1. **计算Recency**
   ```excel
   =TODAY() - last_purchase_date
   ```

2. **分配分数（1-5分）**
   使用PERCENTRANK函数计算百分位，再映射到1-5分
   ```excel
   =MATCH(PERCENTRANK($B$2:$B$1000,B2),{0,0.2,0.4,0.6,0.8},1)
   ```

3. **RFM组合**
   ```excel
   =R_Score&F_Score&M_Score
   ```

#### 分群规则表

| RFM特征 | 分群名称 | 规则 |
|---------|---------|------|
| 555,554,545... | 超级VIP | R≥4, F≥4, M≥4 |
| 355,354... | 重要挽留 | R≤2, F≥4, M≥4 |
| 535,534... | 重点发展 | R≥4, F≤2, M≥4 |
| 553,543... | 潜力客户 | R≥4, F≥4, M≤2 |
| 其他 | 普通客户 | 其他组合 |

#### 透视表配置

创建分群统计透视表：
- 行：segment（分群结果）
- 值：
  - user_id (计数)
  - total_spent (求和)
  - purchase_count (平均值)

---

### 4. 关卡难度分析模板 (level_difficulty.xlsx)

#### 数据输入 (Level_Data)

| 字段 | 说明 |
|------|------|
| level_id | 关卡编号 |
| start_count | 开始次数 |
| complete_count | 完成次数 |
| total_attempts | 总尝试次数 |
| total_time | 总用时(秒) |

#### 关键指标计算

```excel
# 完成率
=complete_count/start_count

# 平均尝试次数
=total_attempts/start_count

# 平均完成时间
=total_time/complete_count

# 难度评级
=IF(完成率>0.8,"简单",IF(完成率>0.6,"适中",IF(完成率>0.4,"困难","极难")))
```

#### 可视化配置

1. **完成率曲线图**
   - X轴：level_id
   - Y轴：完成率
   - 添加目标区间（60%-80%）

2. **漏斗图**
   - 使用漏斗图展示各关卡通过率
   - 识别主要流失关卡

---

### 5. 收入分析仪表板 (revenue_dashboard.xlsx)

#### 数据输入 (Daily_Data)

| 字段 | 说明 |
|------|------|
| date | 日期 |
| dau | 日活跃用户 |
| revenue | 日收入 |
| new_users | 新增用户 |
| paying_users | 付费用户数 |

#### 核心指标公式

```excel
# ARPU
=revenue/DAU

# ARPPU
=revenue/paying_users

# 付费率
=paying_users/DAU

# 新增付费率
=新增付费用户数/new_users

# 环比增长率
=(今日值-昨日值)/昨日值
```

#### 图表配置

**仪表板包含以下图表：**

1. **收入趋势图**（折线图）
   - 7日移动平均线
   - 同比/环比标注

2. **指标卡片**
   - 今日DAU
   - 今日收入
   - 今日ARPU
   - 付费率

3. **渠道对比图**（柱状图）
   - 各渠道收入占比
   - 各渠道ARPU对比

4. **用户构成图**（饼图/环形图）
   - 新用户vs老用户
   - 付费用户vs非付费用户

---

## 使用技巧

### 数据刷新

1. **手动刷新**
   - 数据 → 全部刷新

2. **自动刷新（打开文件时）**
   - 数据 → 连接属性 → 刷新频率

### 条件格式

为留存热力图设置条件格式：
1. 选中留存率数据区域
2. 开始 → 条件格式 → 色阶
3. 选择红-黄-绿色阶
4. 自定义阈值：0%-20%红色，20%-40%黄色，40%+绿色

### 数据验证

防止输入错误：
1. 选中数据输入列
2. 数据 → 数据验证
3. 设置允许的数值范围或日期范围

### 保护工作表

1. 审阅 → 保护工作表
2. 允许用户编辑：数据输入区域
3. 锁定公式和计算区域

---

## 常见问题

**Q: 数据量大时Excel卡顿？**
A: 
- 使用数据模型(Power Pivot)替代普通透视表
- 将历史数据归档到单独文件
- 使用Power Query进行数据预处理

**Q: 如何自动导入外部数据？**
A:
- 数据 → 获取数据 → 从文件/数据库
- 设置定期刷新计划

**Q: 如何分享仪表板？**
A:
- 上传到OneDrive/SharePoint
- 使用Excel Online分享
- 导出为PDF或截图

---

## 扩展功能

### Power Query 自动化

使用Power Query进行数据清洗：
```m
// 示例：过滤异常值
= Table.SelectRows(源, each [session_duration] <= 86400)

// 示例：日期分组
= Table.Group(源, {"registration_date"}, {{"用户数量", each Table.RowCount(_), type number}})
```

### VBA 宏示例

自动更新图表：
```vba
Sub RefreshAllCharts()
    Dim cht As ChartObject
    For Each cht In ActiveSheet.ChartObjects
        cht.Chart.Refresh
    Next cht
    MsgBox "图表已更新！"
End Sub
```
