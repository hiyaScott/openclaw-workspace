#!/usr/bin/env python3
"""
留存分析专用脚本
Retention Analysis Script
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def calculate_cohort_retention(df, user_col='user_id', date_col='date', 
                               reg_col='registration_date'):
    """
    计算同群留存率
    
    参数:
        df: DataFrame，包含用户活跃数据
        user_col: 用户ID列名
        date_col: 活跃日期列名
        reg_col: 注册日期列名
    
    返回:
        retention_matrix: 留存率矩阵
        cohort_sizes: 每群用户数量
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df[reg_col] = pd.to_datetime(df[reg_col])
    
    # 计算每个用户的同群和天数差
    df['cohort'] = df[reg_col].dt.to_period('W')  # 按周分群
    df['days_since_reg'] = (df[date_col] - df[reg_col]).dt.days
    df['period_since_reg'] = df['days_since_reg'] // 7  # 按周计算
    
    # 创建同群表
    cohort_data = df.groupby(['cohort', 'period_since_reg'])[user_col].nunique().reset_index()
    cohort_table = cohort_data.pivot(index='cohort', columns='period_since_reg', values=user_col)
    
    # 获取每群大小
    cohort_sizes = df.groupby('cohort')[user_col].nunique()
    
    # 计算留存率
    retention_matrix = cohort_table.divide(cohort_sizes, axis=0)
    
    return retention_matrix, cohort_sizes


def plot_retention_curves(retention_matrix, save_path='retention_curves.png'):
    """
    绘制多条留存曲线对比
    """
    plt.figure(figsize=(12, 7))
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(retention_matrix)))
    
    for idx, (cohort, row) in enumerate(retention_matrix.iterrows()):
        periods = row.index[:12]  # 只显示前12个周期
        values = row.values[:12]
        plt.plot(periods, values * 100, marker='o', label=str(cohort), 
                color=colors[idx], alpha=0.8)
    
    plt.title('Cohort Retention Curves (Weekly)', fontsize=16, fontweight='bold')
    plt.xlabel('Weeks Since Registration')
    plt.ylabel('Retention Rate (%)')
    plt.legend(title='Cohort', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"留存曲线已保存: {save_path}")


def retention_benchmark_analysis(retention_matrix):
    """
    留存率基准分析
    """
    # 计算平均留存率
    avg_retention = retention_matrix.mean()
    
    # 找出最佳和最差同群
    d7_retention = retention_matrix.iloc[:, 1] if retention_matrix.shape[1] > 1 else None
    d30_retention = retention_matrix.iloc[:, 4] if retention_matrix.shape[1] > 4 else None
    
    analysis = {
        'avg_d1': avg_retention.iloc[0] * 100 if len(avg_retention) > 0 else None,
        'avg_d7': avg_retention.iloc[1] * 100 if len(avg_retention) > 1 else None,
        'avg_d30': avg_retention.iloc[4] * 100 if len(avg_retention) > 4 else None,
    }
    
    if d7_retention is not None:
        analysis['best_d7_cohort'] = d7_retention.idxmax()
        analysis['best_d7_rate'] = d7_retention.max() * 100
        analysis['worst_d7_cohort'] = d7_retention.idxmin()
        analysis['worst_d7_rate'] = d7_retention.min() * 100
    
    return analysis


def predict_ltv_from_retention(retention_rates, arpu_values, days=365):
    """
    基于留存率预测LTV
    
    参数:
        retention_rates: 留存率列表（日留存）
        arpu_values: 每日ARPU列表
        days: 预测天数
    """
    ltv = 0
    for day in range(min(days, len(retention_rates))):
        ltv += arpu_values[day] * retention_rates[day]
    
    # 剩余天数的衰减预测
    if days > len(retention_rates):
        last_retention = retention_rates[-1]
        decay_rate = retention_rates[-1] / retention_rates[-2] if len(retention_rates) > 1 else 0.95
        
        for day in range(len(retention_rates), days):
            last_retention *= decay_rate
            ltv += arpu_values[-1] * last_retention
    
    return ltv


if __name__ == '__main__':
    # 示例用法
    print("留存分析模块加载完成")
    print("\n使用方法:")
    print("from retention_analysis import calculate_cohort_retention")
    print("retention_matrix, cohort_sizes = calculate_cohort_retention(df)")
