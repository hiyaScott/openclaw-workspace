#!/usr/bin/env python3
"""
A/B测试分析脚本
A/B Test Analysis Script
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.8, 
                         ratio=1):
    """
    计算A/B测试所需样本量
    
    参数:
        baseline_rate: 基准转化率 (0-1)
        mde: 最小可检测效应 (绝对值)
        alpha: 显著性水平
        power: 统计功效
        ratio: 对照组与实验组样本比例
    
    返回:
        每组所需样本量
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    p_pooled = (p1 + p2) / 2
    
    n = ((z_alpha * np.sqrt(2 * p_pooled * (1 - p_pooled)) + 
          z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / (p1 - p2) ** 2
    
    return int(np.ceil(n))


def chi_square_test(control_conversions, control_total,
                   treatment_conversions, treatment_total):
    """
    卡方检验分析A/B测试结果
    
    参数:
        control_conversions: 对照组转化数
        control_total: 对照组总数
        treatment_conversions: 实验组转化数
        treatment_total: 实验组总数
    
    返回:
        包含统计结果的字典
    """
    # 构建列联表
    contingency = np.array([
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ])
    
    # 卡方检验
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    
    # 计算转化率
    control_rate = control_conversions / control_total
    treatment_rate = treatment_conversions / treatment_total
    
    # 相对提升
    relative_uplift = (treatment_rate - control_rate) / control_rate
    
    # 置信区间 (使用正态近似)
    def proportion_ci(x, n, confidence=0.95):
        p = x / n
        z = stats.norm.ppf((1 + confidence) / 2)
        se = np.sqrt(p * (1 - p) / n)
        return p - z * se, p + z * se
    
    control_ci = proportion_ci(control_conversions, control_total)
    treatment_ci = proportion_ci(treatment_conversions, treatment_total)
    
    # 差异的置信区间
    se_diff = np.sqrt(control_rate * (1 - control_rate) / control_total + 
                     treatment_rate * (1 - treatment_rate) / treatment_total)
    z = stats.norm.ppf(0.975)
    diff_ci = (treatment_rate - control_rate - z * se_diff,
              treatment_rate - control_rate + z * se_diff)
    
    return {
        'control_rate': control_rate,
        'treatment_rate': treatment_rate,
        'absolute_diff': treatment_rate - control_rate,
        'relative_uplift': relative_uplift,
        'chi2_statistic': chi2,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'control_ci': control_ci,
        'treatment_ci': treatment_ci,
        'diff_ci': diff_ci
    }


def sequential_testing(control_data, treatment_data, batch_size=100):
    """
    序贯测试 - 持续监控测试结果
    """
    results = []
    n_batches = min(len(control_data), len(treatment_data)) // batch_size
    
    for i in range(1, n_batches + 1):
        control_batch = control_data[:i * batch_size]
        treatment_batch = treatment_data[:i * batch_size]
        
        control_conv = control_batch.sum()
        treatment_conv = treatment_batch.sum()
        
        result = chi_square_test(
            control_conv, len(control_batch),
            treatment_conv, len(treatment_batch)
        )
        result['sample_size'] = i * batch_size
        results.append(result)
    
    return pd.DataFrame(results)


def plot_ab_test_results(results_df, save_path='ab_test_results.png'):
    """
    绘制A/B测试结果图表
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # 转化率趋势
    axes[0].plot(results_df['sample_size'], results_df['control_rate'] * 100, 
                label='Control', marker='o')
    axes[0].plot(results_df['sample_size'], results_df['treatment_rate'] * 100, 
                label='Treatment', marker='s')
    axes[0].set_xlabel('Sample Size')
    axes[0].set_ylabel('Conversion Rate (%)')
    axes[0].set_title('Conversion Rates Over Time')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # P值趋势
    axes[1].plot(results_df['sample_size'], results_df['p_value'], 
                marker='o', color='red')
    axes[1].axhline(y=0.05, color='black', linestyle='--', label='Significance (0.05)')
    axes[1].set_xlabel('Sample Size')
    axes[1].set_ylabel('P-value')
    axes[1].set_title('Statistical Significance Over Time')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"A/B测试结果图已保存: {save_path}")


def print_test_summary(result):
    """
    打印测试结果摘要
    """
    print("=" * 50)
    print("A/B测试结果摘要")
    print("=" * 50)
    print(f"对照组转化率: {result['control_rate']:.4f} ({result['control_rate']*100:.2f}%)")
    print(f"实验组转化率: {result['treatment_rate']:.4f} ({result['treatment_rate']*100:.2f}%)")
    print(f"绝对提升: {result['absolute_diff']:.4f} ({result['absolute_diff']*100:.2f}%)")
    print(f"相对提升: {result['relative_uplift']:.2%}")
    print(f"卡方统计量: {result['chi2_statistic']:.4f}")
    print(f"P值: {result['p_value']:.6f}")
    print(f"是否显著: {'是' if result['significant'] else '否'}")
    print(f"对照组95% CI: [{result['control_ci'][0]:.4f}, {result['control_ci'][1]:.4f}]")
    print(f"实验组95% CI: [{result['treatment_ci'][0]:.4f}, {result['treatment_ci'][1]:.4f}]")
    print(f"差异95% CI: [{result['diff_ci'][0]:.4f}, {result['diff_ci'][1]:.4f}]")
    print("=" * 50)


# 示例测试
if __name__ == '__main__':
    # 样本量计算示例
    print("=" * 50)
    print("样本量计算")
    print("=" * 50)
    
    baseline = 0.15  # 15%基准转化率
    mde = 0.03       # 期望检测到3%的绝对提升
    
    sample_size = calculate_sample_size(baseline, mde)
    print(f"基准转化率: {baseline:.2%}")
    print(f"期望提升: {mde:.2%} (绝对)")
    print(f"目标转化率: {baseline + mde:.2%}")
    print(f"每组所需样本量: {sample_size}")
    print(f"总计所需样本量: {sample_size * 2}")
    
    # 模拟测试数据
    print("\n" + "=" * 50)
    print("模拟A/B测试")
    print("=" * 50)
    
    np.random.seed(42)
    n = sample_size
    
    # 对照组: 15%转化率
    control_data = np.random.binomial(1, 0.15, n)
    
    # 实验组: 18%转化率 (3%提升)
    treatment_data = np.random.binomial(1, 0.18, n)
    
    result = chi_square_test(
        control_data.sum(), len(control_data),
        treatment_data.sum(), len(treatment_data)
    )
    
    print_test_summary(result)
    
    # 序贯测试
    print("\n序贯测试结果 (前10批次):")
    sequential_results = sequential_testing(control_data, treatment_data, batch_size=500)
    print(sequential_results[['sample_size', 'control_rate', 'treatment_rate', 
                             'relative_uplift', 'p_value']].head(10).to_string(index=False))
    
    # 绘制结果
    plot_ab_test_results(sequential_results)
