---
name: data-analysis
description: 数据分析与可视化能力，涵盖Python Pandas数据处理、数据清洗、统计分析、可视化呈现。从原始数据到商业洞察的完整分析流程。
---

# 数据分析

## 概述

数据分析是从原始数据中提取有价值信息的过程，通过统计方法、可视化技术和机器学习揭示数据背后的模式和趋势，支持商业决策。

## 核心能力

### 1. 数据处理 (Pandas)

**数据读取与基础操作**：
```python
import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('data.csv')
df = pd.read_excel('data.xlsx')
df = pd.read_json('data.json')

# 基础查看
print(df.head())        # 前5行
print(df.info())        # 数据类型和缺失值
print(df.describe())    # 统计摘要
print(df.shape)         # 行列数
```

**数据清洗技巧**：
```python
# 处理缺失值
df.dropna(subset=['critical_column'])  # 删除关键列缺失
df['column'].fillna(df['column'].mean(), inplace=True)  # 均值填充

# 处理重复
df.drop_duplicates(inplace=True)

# 类型转换
df['date'] = pd.to_datetime(df['date'])
df['category'] = df['category'].astype('category')

# 异常值检测
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['value'] < Q1 - 1.5*IQR) | (df['value'] > Q3 + 1.5*IQR)]
```

### 2. 数据转换与聚合

**分组聚合分析**：
```python
# 分组统计
summary = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': 'sum',
    'customer_id': 'nunique'
}).round(2)

# 透视表
pivot = pd.pivot_table(
    df, 
    values='sales', 
    index='region', 
    columns='month',
    aggfunc='sum',
    fill_value=0
)

# 时间序列分析
df.set_index('date', inplace=True)
monthly = df.resample('M')['sales'].sum()
rolling_avg = df['sales'].rolling(window=7).mean()
```

### 3. 数据可视化

**Matplotlib基础**：
```python
import matplotlib.pyplot as plt

# 基础图表
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# 折线图
df.plot(kind='line', x='date', y='sales', ax=axes[0,0], title='Sales Trend')

# 柱状图
df.groupby('category')['sales'].sum().plot(kind='bar', ax=axes[0,1], title='Sales by Category')

# 散点图
df.plot(kind='scatter', x='price', y='quantity', ax=axes[1,0], title='Price vs Quantity')

# 直方图
df['sales'].plot(kind='hist', bins=20, ax=axes[1,1], title='Sales Distribution')

plt.tight_layout()
plt.savefig('analysis.png', dpi=300)
```

**Seaborn高级可视化**：
```python
import seaborn as sns

# 热力图
correlation = df.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)

# 箱线图
sns.boxplot(data=df, x='category', y='sales')

# 分布图
sns.histplot(data=df, x='sales', hue='category', kde=True)

# 关系图
sns.pairplot(df[['sales', 'profit', 'expenses', 'customers']])
```

### 4. 统计分析

**描述性统计**：
```python
from scipy import stats

# 基础统计
mean = df['value'].mean()
median = df['value'].median()
std = df['value'].std()
skewness = df['value'].skew()
kurtosis = df['value'].kurtosis()

# 假设检验
# 单样本t检验
t_stat, p_value = stats.ttest_1samp(df['value'], 0)

# 独立样本t检验
group_a = df[df['group'] == 'A']['value']
group_b = df[df['group'] == 'B']['value']
t_stat, p_value = stats.ttest_ind(group_a, group_b)

# 卡方检验
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
```

### 5. 数据报告生成

**自动化报告**：
```python
from datetime import datetime

def generate_report(df, output_file='report.html'):
    """生成数据分析报告"""
    
    html_content = f"""
    <html>
    <head><title>数据分析报告 - {datetime.now().strftime('%Y-%m-%d')}</title></head>
    <body>
        <h1>数据分析报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <h2>数据概览</h2>
        <ul>
            <li>总记录数: {len(df):,}</li>
            <li>总销售额: ${df['sales'].sum():,.2f}</li>
            <li>平均客单价: ${df['sales'].mean():.2f}</li>
        </ul>
        
        <h2>关键指标</h2>
        {df.describe().to_html()}
        
        <h2>分类统计</h2>
        {df.groupby('category')['sales'].sum().to_frame().to_html()}
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file
```

## 数据处理流程

```
原始数据 → 清洗 → 转换 → 分析 → 可视化 → 洞察
    ↓        ↓       ↓       ↓        ↓        ↓
  多源    缺失值   特征    统计    图表    报告
  数据    异常值   工程    建模    仪表板   决策
```

## 工具生态

| 工具 | 用途 | 适用场景 |
|------|------|----------|
| **Pandas** | 数据处理 | 结构化数据分析 |
| **NumPy** | 数值计算 | 数组操作、数学运算 |
| **Matplotlib** | 基础可视化 | 静态图表 |
| **Seaborn** | 统计可视化 | 高级统计图表 |
| **Plotly** | 交互式可视化 | Web仪表板 |
| **Jupyter** | 交互式分析 | 探索性分析 |

## 最佳实践

1. **数据质量优先** - 清洗比分析更重要
2. **可视化探索** - 用图表发现模式
3. **版本控制** - 记录分析过程
4. **可重复性** - 脚本化整个流程
5. **业务理解** - 结合领域知识解读数据

## 参考资源

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python for Data Analysis - Wes McKinney](https://wesmckinney.com/book/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
- [Kaggle Learn](https://www.kaggle.com/learn)
