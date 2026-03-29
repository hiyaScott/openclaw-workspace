# Game Analytics 游戏数据分析

游戏数据分析是通过收集、处理和分析玩家行为数据，帮助游戏开发者和运营团队做出数据驱动决策的技术和方法论。

---

## 1. 核心数据指标

### 1.1 留存率（Retention Rate）

留存率是衡量游戏吸引力和长期价值的核心指标。

#### 定义与计算

$$\text{留存率} = \frac{\text{N日后仍活跃的用户数}}{\text{首日新增用户数}} \times 100\%$$

| 留存类型 | 时间窗口 | 行业基准 |
|---------|---------|---------|
| 次日留存 | D+1 | 30-40%（手游） |
| 7日留存 | D+7 | 10-15% |
| 30日留存 | D+30 | 5-8% |
| 90日留存 | D+90 | 2-4% |

#### 留存曲线分析

```python
# 留存曲线示例计算
def calculate_retention(new_users_day1, active_users_day_n, day):
    """
    计算N日留存率
    """
    return (active_users_day_n / new_users_day1) * 100

# 示例：计算30日留存矩阵
# 矩阵行为日期，列为留存天数
retention_matrix = {
    '2024-01-01': [100, 45, 38, 32, 28, 25, 22, 20, 19, 18, ..., 8],
    '2024-01-02': [100, 42, 35, 30, 26, 23, 20, 18, 17, 16, ..., 7],
    # ...
}
```

#### 留存率优化策略

1. **首日体验优化**：新手引导、核心玩法展示
2. **社交绑定**：好友系统、公会机制
3. **内容更新**：定期活动、新内容推送
4. **个性化推送**：基于行为的再激活策略

---

### 1.2 LTV（用户生命周期价值）

LTV表示单个用户在整个生命周期内为游戏带来的总价值。

#### 计算方法

**方法1：历史平均法**
$$\text{LTV} = \text{ARPU} \times \text{平均用户生命周期}$$

**方法2：留存曲线法**
$$\text{LTV} = \sum_{t=1}^{n} \text{ARPU}_t \times \text{Retention}_t \times \text{Discount Factor}$$

**方法3：付费预测法**
```python
def calculate_ltv(cohort_data, prediction_days=365):
    """
    基于同群分析计算LTV
    """
    daily_arpu = cohort_data['revenue'] / cohort_data['users']
    retention_curve = cohort_data['retention_rates']
    
    ltv = 0
    for day in range(1, prediction_days + 1):
        if day <= len(retention_curve):
            retention = retention_curve[day - 1]
        else:
            # 使用指数衰减模型预测
            retention = retention_curve[-1] * (0.95 ** (day - len(retention_curve)))
        
        ltv += daily_arpu * retention
    
    return ltv
```

#### LTV:CAC 比率

| 比率范围 | 含义 | 建议 |
|---------|-----|------|
| < 1:1 | 获客成本过高 | 立即停止投放 |
| 1:1 - 3:1 | 勉强盈利 | 优化转化或降低CAC |
| 3:1 - 5:1 | 健康状态 | 可继续扩张 |
| > 5:1 | 可能增长不足 | 增加市场投入 |

---

### 1.3 ARPU / ARPPU

#### ARPU（每用户平均收入）
$$\text{ARPU} = \frac{\text{总收入}}{\text{总活跃用户数}}$$

#### ARPPU（每付费用户平均收入）
$$\text{ARPPU} = \frac{\text{总收入}}{\text{付费用户数}}$$

#### 付费渗透率
$$\text{付费率} = \frac{\text{付费用户数}}{\text{总活跃用户数}} \times 100\%$$

#### 关系公式
$$\text{ARPU} = \text{ARPPU} \times \text{付费率}$$

#### 行业参考值

| 游戏类型 | ARPU（月） | ARPPU（月） | 付费率 |
|---------|-----------|------------|--------|
| 超休闲 | ¥1-5 | ¥30-50 | 2-5% |
| 中核 | ¥15-30 | ¥150-300 | 5-10% |
| 硬核/SLG | ¥50-100 | ¥500-1000 | 8-15% |
| MMO/RPG | ¥80-200 | ¥800-2000 | 10-20% |

---

### 1.4 转化率

#### 付费转化率

$$\text{付费转化率} = \frac{\text{首次付费用户数}}{\text{新增用户数}} \times 100\%$$

**关键转化节点：**
- 首充转化（0→付费）
- 复购转化（1次→2次付费）
- 大额付费转化（小额→大额）

#### 关卡完成率

$$\text{关卡完成率} = \frac{\text{完成关卡用户数}}{\text{开始关卡用户数}} \times 100\%$$

```python
# 关卡漏斗分析
def level_funnel_analysis(level_data):
    """
    分析关卡完成漏斗
    """
    funnel = []
    for level in level_data:
        funnel.append({
            'level': level['level_id'],
            'started': level['start_count'],
            'completed': level['complete_count'],
            'completion_rate': level['complete_count'] / level['start_count'],
            'avg_attempts': level['total_attempts'] / level['start_count'],
            'avg_time': level['total_time'] / level['complete_count'] if level['complete_count'] > 0 else None
        })
    return funnel
```

---

## 2. 分析框架

### 2.1 AARRR漏斗模型

AARRR模型是游戏产品增长的核心框架，涵盖用户全生命周期。

```
┌─────────────────────────────────────────────────────────┐
│  Acquisition（获客）                                      │
│  → 下载量、安装量、获客成本(CPI/CPA)                        │
│  → 渠道归因、广告效果分析                                  │
├─────────────────────────────────────────────────────────┤
│  Activation（激活）                                       │
│  → 首日体验完成率、核心玩法触达率                           │
│  → 新手引导完成率、首次胜利/成就                            │
├─────────────────────────────────────────────────────────┤
│  Retention（留存）                                        │
│  → 次日/7日/30日留存率                                    │
│  → 留存曲线、流失预警                                      │
├─────────────────────────────────────────────────────────┤
│  Revenue（收入）                                          │
│  → ARPU、ARPPU、LTV                                      │
│  → 付费转化、付费频次、付费深度                            │
├─────────────────────────────────────────────────────────┤
│  Referral（传播）                                         │
│  → K因子、邀请率、病毒传播系数                             │
│  → 社交分享、口碑传播效果                                  │
└─────────────────────────────────────────────────────────┘
```

#### 关键指标拆解

| 阶段 | 核心指标 | 计算公式 |
|------|---------|---------|
| 获客 | CPI | 广告花费 / 安装量 |
| 激活 | 激活率 | 完成新手引导 / 安装量 |
| 留存 | D1/D7/D30 | 对应天数仍活跃 / 新增 |
| 收入 | ROAS | 回收收入 / 广告花费 |
| 传播 | K-factor | 每个用户带来的新用户 |

---

### 2.2 玩家分群（RFM模型）

RFM模型通过三个维度对玩家进行价值分群：

- **R（Recency）**：最近一次付费距今天数
- **F（Frequency）**：付费频次
- **M（Monetary）**：付费金额

#### 分群方法

```python
import pandas as pd

def rfm_segmentation(df, r_bins=5, f_bins=5, m_bins=5):
    """
    RFM玩家分群
    """
    # 计算RFM分数（1-5分，5分为最佳）
    df['R_Score'] = pd.qcut(df['recency'], r_bins, labels=[5,4,3,2,1])
    df['F_Score'] = pd.qcut(df['frequency'].rank(method='first'), f_bins, labels=[1,2,3,4,5])
    df['M_Score'] = pd.qcut(df['monetary'], m_bins, labels=[1,2,3,4,5])
    
    # 组合RFM分数
    df['RFM_Score'] = df['R_Score'].astype(str) + \
                      df['F_Score'].astype(str) + \
                      df['M_Score'].astype(str)
    
    # 定义玩家类型
    def segment_player(row):
        r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
        avg_rfm = (r + f + m) / 3
        
        if r >= 4 and f >= 4 and m >= 4:
            return '超级VIP'
        elif r >= 3 and f >= 3 and m >= 4:
            return '高价值玩家'
        elif r >= 4 and f >= 2:
            return '潜力玩家'
        elif r <= 2 and f >= 4:
            return '流失风险-高频'
        elif r <= 2 and m >= 4:
            return '流失风险-高值'
        elif avg_rfm >= 3:
            return '普通玩家'
        else:
            return '低价值玩家'
    
    df['Player_Segment'] = df.apply(segment_player, axis=1)
    return df
```

#### 分群运营策略

| 玩家类型 | 特征 | 运营策略 |
|---------|------|---------|
| 超级VIP | 高活跃、高频付费、高金额 | 专属客服、定制化内容、提前体验 |
| 高价值玩家 | 稳定付费、中等活跃 | 付费礼包、成长基金、限时活动 |
| 潜力玩家 | 高活跃但付费少 | 首充引导、小额礼包、价值教育 |
| 流失风险-高频 | 曾高频但近期不活跃 | 回流活动、老玩家专属奖励 |
| 流失风险-高值 | 曾高付费但近期不活跃 | 个性化召回、专属折扣 |
| 普通玩家 | 各项指标中等 | 常规运营、活动参与 |
| 低价值玩家 | 各项指标较低 | 低成本维护、偶尔激活 |

---

### 2.3 流失预警模型

#### 流失定义

- **硬流失**：连续N天未登录（如7天、14天、30天）
- **软流失**：活跃度显著下降（如游戏时长减少50%以上）

#### 预警指标

```python
# 流失预警特征工程
def extract_churn_features(player_logs):
    """
    提取流失预测特征
    """
    features = {
        # 活跃度特征
        'days_since_last_login': calculate_recency(player_logs),
        'login_frequency_7d': count_logins_last_7_days(player_logs),
        'login_frequency_30d': count_logins_last_30_days(player_logs),
        'session_duration_avg': avg_session_duration(player_logs),
        'session_duration_trend': session_duration_trend(player_logs),
        
        # 游戏行为特征
        'levels_completed_7d': levels_completed_last_7_days(player_logs),
        'progression_speed': calculate_progression_speed(player_logs),
        'stuck_level_count': count_consecutive_failures(player_logs),
        
        # 社交特征
        'friends_count': count_friends(player_logs),
        'social_interactions': count_social_actions(player_logs),
        'guild_activity': guild_participation_rate(player_logs),
        
        # 付费特征
        'days_since_last_purchase': recency_of_purchase(player_logs),
        'purchase_frequency': purchase_frequency(player_logs),
        'purchase_amount_trend': spending_trend(player_logs),
        
        # 情绪特征
        'negative_events': count_negative_events(player_logs),
        'support_tickets': count_support_requests(player_logs),
    }
    return features
```

#### 简单规则预警

```python
def simple_churn_prediction(features):
    """
    基于规则的流失预警
    """
    risk_score = 0
    
    # 活跃度风险
    if features['days_since_last_login'] >= 3:
        risk_score += 30
    if features['login_frequency_7d'] == 0:
        risk_score += 25
    if features['session_duration_trend'] < -0.3:
        risk_score += 20
    
    # 游戏行为风险
    if features['stuck_level_count'] >= 5:
        risk_score += 15
    if features['progression_speed'] < 0.5:
        risk_score += 10
    
    # 社交风险
    if features['friends_count'] == 0:
        risk_score += 10
    
    # 风险等级
    if risk_score >= 70:
        return '高风险', risk_score
    elif risk_score >= 40:
        return '中风险', risk_score
    else:
        return '低风险', risk_score
```

---

## 3. 工具与实践

### 3.1 Google Analytics for Games

#### 集成要点

```javascript
// Firebase Analytics 游戏事件示例
import { getAnalytics, logEvent } from 'firebase/analytics';

const analytics = getAnalytics();

// 关卡开始
logEvent(analytics, 'level_start', {
  level_name: 'level_1_5',
  level_difficulty: 'easy'
});

// 关卡完成
logEvent(analytics, 'level_complete', {
  level_name: 'level_1_5',
  success: true,
  attempts: 3,
  time_spent: 120
});

// 虚拟商品购买
logEvent(analytics, 'purchase', {
  transaction_id: 'txn_12345',
  value: 9.99,
  currency: 'USD',
  items: [{
    item_name: 'gem_pack_small',
    item_category: 'virtual_currency'
  }]
});
```

#### 自定义事件设计

| 事件类别 | 事件名称 | 关键参数 |
|---------|---------|---------|
| 进度 | tutorial_complete | tutorial_id, completion_time |
| 进度 | achievement_unlocked | achievement_id |
| 经济 | currency_earned | currency_type, amount, source |
| 经济 | currency_spent | currency_type, amount, sink |
| 社交 | friend_added | method (invite/search) |
| 竞技 | match_completed | match_type, result, rank |

---

### 3.2 Unity Analytics

```csharp
using UnityEngine;
using Unity.Services.Analytics;

public class GameAnalytics : MonoBehaviour
{
    // 自定义事件
    public void TrackLevelStart(string levelId)
    {
        Analytics.CustomEvent("level_start", new Dictionary<string, object>
        {
            { "level_id", levelId },
            { "player_level", PlayerData.Instance.Level }
        });
    }
    
    // 标准事件 - 虚拟商品购买
    public void TrackVirtualPurchase(string itemId, int quantity, string currency, int price)
    {
        var parameters = new Dictionary<string, object>
        {
            { "item_id", itemId },
            { "item_quantity", quantity },
            { "currency_type", currency },
            { "price", price }
        };
        
        Analytics.CustomEvent("virtual_purchase", parameters);
    }
}
```

---

### 3.3 Python 数据分析实践

#### 数据清洗与预处理

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_and_clean_game_data(filepath):
    """
    加载并清洗游戏数据
    """
    df = pd.read_csv(filepath)
    
    # 数据类型转换
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['user_id'] = df['user_id'].astype(str)
    
    # 处理异常值
    df = df[df['session_duration'] <= 86400]  # 排除超过24小时的异常会话
    df = df[df['level'] >= 0]  # 排除负等级
    
    # 缺失值处理
    df['revenue'] = df['revenue'].fillna(0)
    df['country'] = df['country'].fillna('unknown')
    
    return df
```

#### 留存分析可视化

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_retention_heatmap(retention_matrix):
    """
    绘制留存热力图
    """
    plt.figure(figsize=(14, 8))
    sns.heatmap(retention_matrix, 
                annot=True, 
                fmt='.1f', 
                cmap='YlOrRd',
                cbar_kws={'label': 'Retention %'})
    plt.title('Cohort Retention Heatmap', fontsize=16)
    plt.xlabel('Days Since Registration')
    plt.ylabel('Cohort Date')
    plt.tight_layout()
    plt.savefig('retention_heatmap.png', dpi=300)
    plt.show()

def plot_retention_curve(cohorts):
    """
    绘制留存曲线
    """
    plt.figure(figsize=(12, 6))
    
    for cohort_date, retention_rates in cohorts.items():
        days = list(range(len(retention_rates)))
        plt.plot(days, retention_rates, marker='o', label=cohort_date, alpha=0.7)
    
    plt.title('Retention Curves by Cohort', fontsize=16)
    plt.xlabel('Days')
    plt.ylabel('Retention Rate (%)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('retention_curves.png', dpi=300)
    plt.show()
```

#### 付费分析

```python
def analyze_purchasing_behavior(df):
    """
    分析付费行为
    """
    # 识别付费用户
    df['is_payer'] = df['revenue'] > 0
    
    # 首次付费间隔
    first_purchase = df[df['is_payer']].groupby('user_id')['timestamp'].min().reset_index()
    first_purchase.columns = ['user_id', 'first_purchase_date']
    
    # 计算从注册到首次付费的天数
    user_registration = df.groupby('user_id')['timestamp'].min().reset_index()
    user_registration.columns = ['user_id', 'registration_date']
    
    purchase_timing = pd.merge(first_purchase, user_registration, on='user_id')
    purchase_timing['days_to_first_purchase'] = (
        purchase_timing['first_purchase_date'] - purchase_timing['registration_date']
    ).dt.days
    
    print("首次付费间隔分布：")
    print(purchase_timing['days_to_first_purchase'].describe())
    
    # 付费频次分析
    purchase_frequency = df[df['is_payer']].groupby('user_id').size()
    print(f"\n付费频次：")
    print(f"平均付费次数: {purchase_frequency.mean():.2f}")
    print(f"中位数付费次数: {purchase_frequency.median():.2f}")
    
    return purchase_timing, purchase_frequency
```

---

## 4. 实战案例

### 4.1 关卡难度曲线分析

#### 分析目标
识别关卡难度是否合理，发现玩家流失的关键节点。

```python
def analyze_level_difficulty(level_data):
    """
    分析关卡难度曲线
    """
    analysis = []
    
    for level_id, data in level_data.groupby('level_id'):
        total_starts = len(data)
        completions = data['completed'].sum()
        
        analysis.append({
            'level_id': level_id,
            'attempts': total_starts,
            'completions': completions,
            'completion_rate': completions / total_starts if total_starts > 0 else 0,
            'avg_attempts_to_complete': data[data['completed']]['attempts'].mean(),
            'avg_time_spent': data['time_spent'].mean(),
            'drop_off_rate': 1 - (data['next_level_started'].sum() / completions) if completions > 0 else 0
        })
    
    return pd.DataFrame(analysis)

# 难度评估标准
def evaluate_difficulty(completion_rate, avg_attempts):
    """
    评估关卡难度
    """
    if completion_rate > 0.8 and avg_attempts < 2:
        return '太简单'
    elif completion_rate > 0.6 and avg_attempts <= 3:
        return '适中'
    elif completion_rate > 0.4 and avg_attempts <= 5:
        return '偏难'
    else:
        return '过难'
```

#### 理想难度曲线

```
完成率
  │
100%├─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │ 90% │ 85% │ 80% │ 75% │ 70% │ 68% │ 65% │ 62% │ 60% │
 80%├─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┤
    │                                                      │
 60%│                     目标区间                         │
    │                  (60%-80%)                           │
 40%├──────────────────────────────────────────────────────┤
    │                                                      │
 20%│                                                      │
    │                                                      │
  0%└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
       L1   L5   L10   L15   L20   L25   L30   L35   L40
                       关卡编号
```

### 4.2 付费点效果评估

```python
def evaluate_purchase_points(transaction_data, user_data):
    """
    评估各付费点效果
    """
    results = []
    
    for product_id in transaction_data['product_id'].unique():
        product_txns = transaction_data[transaction_data['product_id'] == product_id]
        
        results.append({
            'product_id': product_id,
            'total_revenue': product_txns['amount'].sum(),
            'purchase_count': len(product_txns),
            'unique_buyers': product_txns['user_id'].nunique(),
            'avg_purchase_value': product_txns['amount'].mean(),
            'conversion_rate': calculate_conversion_rate(product_id, user_data),
            'repeat_purchase_rate': calculate_repeat_rate(product_txns),
            'revenue_per_user': product_txns['amount'].sum() / user_data['user_id'].nunique()
        })
    
    return pd.DataFrame(results).sort_values('total_revenue', ascending=False)

# 付费点优化建议框架
def generate_optimization_suggestions(evaluation_df):
    """
    生成付费点优化建议
    """
    suggestions = []
    
    for _, row in evaluation_df.iterrows():
        product_id = row['product_id']
        
        if row['conversion_rate'] < 0.01:
            suggestions.append({
                'product': product_id,
                'issue': '转化率过低',
                'suggestion': '考虑降低价格或增加价值感知'
            })
        elif row['repeat_purchase_rate'] < 0.1 and row['purchase_count'] > 100:
            suggestions.append({
                'product': product_id,
                'issue': '复购率低',
                'suggestion': '可能是一次性商品，考虑推出消耗型版本'
            })
        elif row['avg_purchase_value'] < 1.0:
            suggestions.append({
                'product': product_id,
                'issue': '客单价过低',
                'suggestion': '捆绑销售或推出高阶版本'
            })
    
    return suggestions
```

### 4.3 A/B测试设计与分析

#### 测试设计

```python
import scipy.stats as stats

def design_ab_test(baseline_rate, mde, alpha=0.05, power=0.8):
    """
    设计A/B测试样本量
    
    Args:
        baseline_rate: 基准转化率
        mde: 最小可检测效应
        alpha: 显著性水平
        power: 统计功效
    """
    from scipy.stats import norm
    
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    
    p1 = baseline_rate
    p2 = baseline_rate + mde
    p_pooled = (p1 + p2) / 2
    
    n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (p1 - p2)**2
    
    return int(np.ceil(n))

# 示例：测试新用户引导优化
# 假设当前转化率15%，期望提升到18%
sample_size = design_ab_test(baseline_rate=0.15, mde=0.03)
print(f"每组需要样本量: {sample_size}")
```

#### 结果分析

```python
def analyze_ab_test(control_data, treatment_data):
    """
    分析A/B测试结果
    """
    # 转化率
    control_rate = control_data['converted'].mean()
    treatment_rate = treatment_data['converted'].mean()
    
    # 提升率
    uplift = (treatment_rate - control_rate) / control_rate
    
    # 卡方检验
    contingency_table = pd.crosstab(
        pd.concat([control_data, treatment_data])['group'],
        pd.concat([control_data, treatment_data])['converted']
    )
    
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    # 置信区间
    from statsmodels.stats.proportion import confint_proportions_2indep
    ci_low, ci_high = confint_proportions_2indep(
        treatment_data['converted'].sum(), len(treatment_data),
        control_data['converted'].sum(), len(control_data),
        method='wald'
    )
    
    return {
        'control_rate': control_rate,
        'treatment_rate': treatment_rate,
        'absolute_uplift': treatment_rate - control_rate,
        'relative_uplift': uplift,
        'p_value': p_value,
        'ci_95': (ci_low, ci_high),
        'significant': p_value < 0.05
    }
```

---

## 5. 最佳实践

### 数据治理

1. **数据质量**：建立数据校验规则，定期检查异常值
2. **隐私合规**：遵循GDPR、COPPA等法规要求
3. **实时性**：平衡实时分析与数据准确性

### 分析流程

1. **定义问题**：明确业务目标和分析假设
2. **设计指标**：选择合适的数据指标
3. **收集数据**：确保数据完整性和准确性
4. **分析解读**：结合业务理解进行分析
5. **行动验证**：实施改进并验证效果

### 常见误区

- ** Vanity Metrics**：关注虚荣指标而非 actionable metrics
- **幸存者偏差**：只分析留存用户，忽略流失用户
- **相关性≠因果性**：避免将相关性误判为因果关系
- **样本偏差**：确保样本代表性

---

## 6. 数据收集与埋点设计

### 6.1 事件追踪设计原则

#### 事件命名规范

采用 `Object_Action` 的命名方式，确保事件语义清晰：

| 事件名 | 说明 | 参数 |
|--------|------|------|
| `level_start` | 关卡开始 | level_id, difficulty |
| `level_complete` | 关卡完成 | level_id, stars, time_spent |
| `item_purchase` | 道具购买 | item_id, currency, price |
| `ad_impression` | 广告展示 | ad_type, placement |
| `ad_click` | 广告点击 | ad_type, placement |

#### 用户属性维度

```python
# 核心用户属性（随每次事件发送）
user_properties = {
    'user_id': 'unique_identifier',
    'user_type': 'new' | 'returning',
    'level': 15,  # 玩家等级
    'total_play_time': 3600,  # 累计游戏时长
    'total_purchase': 99.99,  # 累计付费
    'country': 'CN',
    'device_type': 'iOS' | 'Android',
    'acquisition_channel': 'organic' | 'facebook' | 'google'
}

# 会话属性
session_properties = {
    'session_id': 'session_uuid',
    'session_number': 5,  # 第几次会话
    'session_duration': 600,  # 会话时长(秒)
}
```

### 6.2 核心事件清单

#### 用户生命周期事件

| 阶段 | 事件 | 触发时机 | 关键参数 |
|------|------|----------|----------|
| 获客 | app_install | 首次安装 | source, campaign_id |
| 获客 | app_open | 每次启动 | launch_type |
| 激活 | tutorial_start | 新手引导开始 | tutorial_id |
| 激活 | tutorial_complete | 新手引导完成 | tutorial_id, duration |
| 激活 | first_win | 首次获胜 | level_id |
| 留存 | session_start | 会话开始 | day_number |
| 留存 | session_end | 会话结束 | duration, levels_played |
| 收入 | purchase_initiated | 发起购买 | product_id |
| 收入 | purchase_completed | 完成购买 | product_id, value, currency |
| 收入 | purchase_refunded | 退款 | product_id, reason |

#### 游戏玩法事件

```python
# 进度事件
gameplay_events = {
    'level_start': {
        'level_id': 'level_1_5',
        'level_difficulty': 'medium',
        'player_lives': 5,
        'player_powerups': ['bomb', 'rainbow']
    },
    'level_end': {
        'level_id': 'level_1_5',
        'success': True,
        'score': 15000,
        'stars': 3,
        'time_spent': 120,
        'attempts': 2,
        'powerups_used': ['bomb']
    },
    'achievement_unlocked': {
        'achievement_id': 'first_blood',
        'achievement_type': 'combat'
    }
}
```

---

## 7. 数据仓库与报表体系

### 7.1 数据分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层 (ADS)                              │
│   留存报表 │ 收入报表 │ 用户画像 │ 运营指标看板              │
├─────────────────────────────────────────────────────────────┤
│                    主题层 (DWS)                              │
│   用户主题 │ 交易主题 │ 内容主题 │ 运营主题                  │
├─────────────────────────────────────────────────────────────┤
│                    明细层 (DWD)                              │
│   用户行为事件 │ 交易流水 │ 游戏日志 │ 广告数据              │
├─────────────────────────────────────────────────────────────┤
│                    原始层 (ODS)                              │
│   埋点原始数据 │ 渠道数据 │ 支付回调 │ 广告平台数据          │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 核心数据表设计

#### 用户日活跃表 (user_daily_activity)

| 字段 | 类型 | 说明 |
|------|------|------|
| dt | DATE | 日期分区 |
| user_id | STRING | 用户ID |
| is_new_user | BOOLEAN | 是否新用户 |
| session_count | INT | 会话次数 |
| total_play_time | INT | 总游戏时长(秒) |
| levels_completed | INT | 完成关卡数 |
| revenue | DECIMAL | 当日收入 |
| country | STRING | 国家 |
| channel | STRING | 获客渠道 |

#### 用户属性表 (user_profile)

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | STRING | 用户ID |
| register_date | DATE | 注册日期 |
| register_channel | STRING | 注册渠道 |
| last_active_date | DATE | 最后活跃 |
| total_revenue | DECIMAL | 累计收入 |
| total_purchases | INT | 购买次数 |
| highest_level | INT | 最高关卡 |
| vip_level | INT | VIP等级 |
| current_segment | STRING | 当前分群 |

---

## 8. 常见分析场景

### 8.1 新功能效果评估

当游戏推出新功能时，按以下框架评估：

```python
def evaluate_feature_impact(control_group, treatment_group, metrics):
    """
    新功能效果评估框架
    """
    results = {}
    
    for metric in metrics:
        control_value = control_group[metric].mean()
        treatment_value = treatment_group[metric].mean()
        
        # 统计显著性检验
        t_stat, p_value = stats.ttest_ind(
            control_group[metric], 
            treatment_group[metric]
        )
        
        results[metric] = {
            'control': control_value,
            'treatment': treatment_value,
            'lift': (treatment_value - control_value) / control_value,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    return results

# 评估维度
metrics_to_check = [
    'retention_d1',
    'retention_d7', 
    'avg_session_duration',
    'levels_per_session',
    'revenue_per_user'
]
```

### 8.2 活动效果分析

```python
def analyze_campaign_performance(campaign_data, pre_period=7, post_period=7):
    """
    活动效果分析
    """
    # 活动前后对比
    pre_campaign = campaign_data[
        campaign_data['date'] < campaign_data['campaign_start']
    ].iloc[-pre_period:]
    
    during_campaign = campaign_data[
        (campaign_data['date'] >= campaign_data['campaign_start']) &
        (campaign_data['date'] <= campaign_data['campaign_end'])
    ]
    
    post_campaign = campaign_data[
        campaign_data['date'] > campaign_data['campaign_end']
    ].iloc[:post_period]
    
    analysis = {
        'pre_avg_revenue': pre_campaign['revenue'].mean(),
        'during_avg_revenue': during_campaign['revenue'].mean(),
        'post_avg_revenue': post_campaign['revenue'].mean(),
        'lift_vs_pre': (during_campaign['revenue'].mean() / pre_campaign['revenue'].mean() - 1),
        'sustained_lift': (post_campaign['revenue'].mean() / pre_campaign['revenue'].mean() - 1)
    }
    
    return analysis
```

### 8.3 渠道质量评估

```python
def evaluate_channel_quality(user_data, channel_col='channel', 
                            revenue_col='total_revenue',
                            register_col='register_date'):
    """
    评估各获客渠道质量
    """
    channel_metrics = user_data.groupby(channel_col).agg({
        'user_id': 'count',
        revenue_col: ['sum', 'mean'],
        'days_active': 'mean',
        'max_level': 'mean'
    }).round(2)
    
    channel_metrics.columns = ['users', 'total_revenue', 'arpu', 
                              'avg_active_days', 'avg_max_level']
    
    # 计算渠道评分
    channel_metrics['ltv_score'] = (
        channel_metrics['arpu'] * 0.4 +
        channel_metrics['avg_active_days'] * 0.3 +
        channel_metrics['avg_max_level'] * 0.3
    )
    
    return channel_metrics.sort_values('ltv_score', ascending=False)
```

---

## 参考目录

- `references/resources.md` - 学习资源和工具清单
- `examples/` - 实际分析案例代码
- `templates/` - 分析模板和报表模板
- `scripts/` - 常用分析脚本

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2024-03 | 初始版本，包含核心指标、分析框架和基础工具 |

