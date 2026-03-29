#!/usr/bin/env python3
"""
游戏数据分析脚本集合
Game Analytics Scripts Collection

使用方法:
    python game_analytics.py --action retention --input data.csv
    python game_analytics.py --action rfm --input users.csv
    python game_analytics.py --action level --input levels.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import argparse
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GameAnalytics:
    """游戏数据分析核心类"""
    
    def __init__(self, data_path=None):
        self.data = None
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, filepath):
        """加载数据"""
        self.data = pd.read_csv(filepath)
        print(f"数据加载完成: {len(self.data)} 行")
        return self
    
    # ==================== 留存分析 ====================
    
    def calculate_retention(self, user_col='user_id', date_col='date', 
                           register_col='registration_date'):
        """
        计算同群留存率
        """
        df = self.data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df[register_col] = pd.to_datetime(df[register_col])
        
        # 计算注册日期
        df['cohort'] = df[register_col].dt.date
        df['days_since_reg'] = (df[date_col] - df[register_col]).dt.days
        
        # 创建同群矩阵
        cohort_data = df.groupby(['cohort', 'days_since_reg'])[user_col].nunique().reset_index()
        cohort_counts = cohort_data.pivot(index='cohort', columns='days_since_reg', values=user_col)
        
        # 计算留存率
        cohort_sizes = df.groupby('cohort')[user_col].nunique()
        retention_matrix = cohort_counts.divide(cohort_sizes, axis=0) * 100
        
        return retention_matrix
    
    def plot_retention_heatmap(self, retention_matrix, save_path='retention_heatmap.png'):
        """
        绘制留存热力图
        """
        plt.figure(figsize=(16, 10))
        
        # 限制显示前30天
        retention_display = retention_matrix.iloc[:, :31]
        
        sns.heatmap(retention_display, 
                    annot=True, 
                    fmt='.1f',
                    cmap='YlOrRd',
                    cbar_kws={'label': 'Retention %'},
                    annot_kws={'size': 8})
        
        plt.title('Cohort Retention Analysis', fontsize=16, fontweight='bold')
        plt.xlabel('Days Since Registration', fontsize=12)
        plt.ylabel('Cohort Date', fontsize=12)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"留存热力图已保存: {save_path}")
        plt.close()
    
    def retention_summary(self, retention_matrix, days=[1, 7, 14, 30]):
        """
        留存汇总统计
        """
        summary = {}
        for day in days:
            if day < retention_matrix.shape[1]:
                values = retention_matrix.iloc[:, day].dropna()
                summary[f'D{day}'] = {
                    'mean': values.mean(),
                    'median': values.median(),
                    'min': values.min(),
                    'max': values.max()
                }
        return pd.DataFrame(summary).T
    
    # ==================== RFM分析 ====================
    
    def rfm_analysis(self, user_col='user_id', date_col='last_purchase_date',
                    freq_col='purchase_count', monetary_col='total_spent',
                    reference_date=None):
        """
        RFM玩家分群分析
        """
        df = self.data.copy()
        
        if reference_date is None:
            reference_date = pd.to_datetime(df[date_col]).max()
        else:
            reference_date = pd.to_datetime(reference_date)
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        # 计算RFM值
        rfm = pd.DataFrame()
        rfm['user_id'] = df[user_col]
        rfm['recency'] = (reference_date - df[date_col]).dt.days
        rfm['frequency'] = df[freq_col]
        rfm['monetary'] = df[monetary_col]
        
        # 计算RFM分数（1-5分）
        rfm['R_Score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])
        rfm['F_Score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['M_Score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5])
        
        # 组合分数
        rfm['RFM_Score'] = (rfm['R_Score'].astype(str) + 
                           rfm['F_Score'].astype(str) + 
                           rfm['M_Score'].astype(str))
        
        # 玩家分群
        def segment_player(row):
            r, f, m = int(row['R_Score']), int(row['F_Score']), int(row['M_Score'])
            
            if r >= 4 and f >= 4 and m >= 4:
                return '超级VIP'
            elif r >= 3 and f >= 3 and m >= 4:
                return '高价值玩家'
            elif r >= 4 and f <= 2 and m <= 2:
                return '新玩家潜力'
            elif r <= 2 and f >= 4:
                return '流失风险-高频'
            elif r <= 2 and m >= 4:
                return '流失风险-高值'
            elif f >= 3 and m >= 3:
                return '普通价值玩家'
            else:
                return '低价值玩家'
        
        rfm['segment'] = rfm.apply(segment_player, axis=1)
        
        return rfm
    
    def plot_rfm_distribution(self, rfm_df, save_path='rfm_distribution.png'):
        """
        绘制RFM分布图
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 分群数量
        segment_counts = rfm_df['segment'].value_counts()
        axes[0, 0].bar(range(len(segment_counts)), segment_counts.values)
        axes[0, 0].set_xticks(range(len(segment_counts)))
        axes[0, 0].set_xticklabels(segment_counts.index, rotation=45, ha='right')
        axes[0, 0].set_title('Player Segment Distribution')
        axes[0, 0].set_ylabel('Count')
        
        # R分布
        axes[0, 1].hist(rfm_df['recency'], bins=30, edgecolor='black')
        axes[0, 1].set_title('Recency Distribution')
        axes[0, 1].set_xlabel('Days Since Last Purchase')
        
        # F分布
        axes[1, 0].hist(rfm_df['frequency'], bins=30, edgecolor='black')
        axes[1, 0].set_title('Frequency Distribution')
        axes[1, 0].set_xlabel('Purchase Count')
        
        # M分布
        axes[1, 1].hist(rfm_df['monetary'], bins=30, edgecolor='black')
        axes[1, 1].set_title('Monetary Distribution')
        axes[1, 1].set_xlabel('Total Spent')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"RFM分布图已保存: {save_path}")
        plt.close()
    
    # ==================== 关卡分析 ====================
    
    def level_difficulty_analysis(self, level_col='level_id', 
                                  start_col='start_count',
                                  complete_col='complete_count',
                                  time_col='avg_time'):
        """
        关卡难度分析
        """
        df = self.data.copy()
        
        analysis = pd.DataFrame()
        analysis['level_id'] = df[level_col]
        analysis['start_count'] = df[start_col]
        analysis['complete_count'] = df[complete_col]
        analysis['completion_rate'] = df[complete_col] / df[start_col]
        analysis['drop_off_rate'] = 1 - analysis['completion_rate']
        
        if time_col in df.columns:
            analysis['avg_time'] = df[time_col]
        
        # 难度评级
        def rate_difficulty(row):
            rate = row['completion_rate']
            if rate > 0.8:
                return 'Easy'
            elif rate > 0.6:
                return 'Normal'
            elif rate > 0.4:
                return 'Hard'
            else:
                return 'Very Hard'
        
        analysis['difficulty_rating'] = analysis.apply(rate_difficulty, axis=1)
        
        return analysis
    
    def plot_level_difficulty(self, level_df, save_path='level_difficulty.png'):
        """
        绘制关卡难度曲线
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # 完成率曲线
        axes[0].plot(level_df['level_id'], level_df['completion_rate'], 
                    marker='o', linewidth=2, markersize=6)
        axes[0].axhline(y=0.6, color='r', linestyle='--', label='Target Min (60%)')
        axes[0].axhline(y=0.8, color='g', linestyle='--', label='Target Max (80%)')
        axes[0].fill_between(level_df['level_id'], 0.6, 0.8, alpha=0.2, color='green')
        axes[0].set_title('Level Completion Rate Curve')
        axes[0].set_xlabel('Level ID')
        axes[0].set_ylabel('Completion Rate')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 尝试次数柱状图
        axes[1].bar(level_df['level_id'], level_df['start_count'], 
                   alpha=0.7, label='Started')
        axes[1].bar(level_df['level_id'], level_df['complete_count'], 
                   alpha=0.7, label='Completed')
        axes[1].set_title('Level Attempts vs Completions')
        axes[1].set_xlabel('Level ID')
        axes[1].set_ylabel('Count')
        axes[1].legend()
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"关卡难度图已保存: {save_path}")
        plt.close()
    
    # ==================== 收入分析 ====================
    
    def revenue_analysis(self, date_col='date', revenue_col='revenue',
                        user_col='user_id'):
        """
        收入分析
        """
        df = self.data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # 日收入趋势
        daily_revenue = df.groupby(date_col)[revenue_col].sum()
        
        # ARPU计算
        daily_users = df.groupby(date_col)[user_col].nunique()
        daily_arpu = daily_revenue / daily_users
        
        # 付费率
        daily_payers = df[df[revenue_col] > 0].groupby(date_col)[user_col].nunique()
        daily_pay_rate = daily_payers / daily_users * 100
        
        return pd.DataFrame({
            'revenue': daily_revenue,
            'active_users': daily_users,
            'arpu': daily_arpu,
            'pay_rate': daily_pay_rate
        })
    
    def plot_revenue_trend(self, revenue_df, save_path='revenue_trend.png'):
        """
        绘制收入趋势图
        """
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        # 收入趋势
        axes[0].plot(revenue_df.index, revenue_df['revenue'], 
                    marker='o', linewidth=2)
        axes[0].set_title('Daily Revenue Trend')
        axes[0].set_ylabel('Revenue')
        axes[0].grid(True, alpha=0.3)
        
        # ARPU趋势
        axes[1].plot(revenue_df.index, revenue_df['arpu'], 
                    marker='s', color='orange', linewidth=2)
        axes[1].set_title('Daily ARPU Trend')
        axes[1].set_ylabel('ARPU')
        axes[1].grid(True, alpha=0.3)
        
        # 付费率趋势
        axes[2].plot(revenue_df.index, revenue_df['pay_rate'], 
                    marker='^', color='green', linewidth=2)
        axes[2].set_title('Daily Pay Rate Trend')
        axes[2].set_ylabel('Pay Rate (%)')
        axes[2].set_xlabel('Date')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"收入趋势图已保存: {save_path}")
        plt.close()


def generate_sample_data(data_type='retention', n_users=1000):
    """
    生成示例数据用于测试
    """
    np.random.seed(42)
    
    if data_type == 'retention':
        # 生成留存分析数据
        data = []
        start_date = datetime(2024, 1, 1)
        
        for i in range(n_users):
            reg_date = start_date + timedelta(days=np.random.randint(0, 30))
            user_id = f'user_{i}'
            
            # 模拟30天的活跃记录
            for day in range(30):
                # 留存率随天数衰减
                retention_prob = max(0.05, 0.5 * (0.85 ** day))
                if np.random.random() < retention_prob:
                    data.append({
                        'user_id': user_id,
                        'date': reg_date + timedelta(days=day),
                        'registration_date': reg_date
                    })
        
        return pd.DataFrame(data)
    
    elif data_type == 'rfm':
        # 生成RFM分析数据
        data = []
        reference_date = datetime(2024, 3, 1)
        
        for i in range(n_users):
            recency = np.random.exponential(30)
            frequency = max(1, int(np.random.exponential(5)))
            monetary = max(0.99, np.random.lognormal(3, 1.5))
            
            data.append({
                'user_id': f'user_{i}',
                'last_purchase_date': reference_date - timedelta(days=int(recency)),
                'purchase_count': frequency,
                'total_spent': round(monetary, 2)
            })
        
        return pd.DataFrame(data)
    
    elif data_type == 'level':
        # 生成关卡分析数据
        data = []
        
        for level in range(1, 51):
            # 难度随关卡递增
            base_difficulty = 0.9 - (level * 0.01)
            completion_rate = max(0.2, base_difficulty + np.random.normal(0, 0.05))
            
            starts = int(1000 * (0.95 ** level))
            completions = int(starts * completion_rate)
            
            data.append({
                'level_id': level,
                'start_count': starts,
                'complete_count': completions,
                'avg_time': 60 + level * 5 + np.random.normal(0, 10)
            })
        
        return pd.DataFrame(data)
    
    elif data_type == 'revenue':
        # 生成收入分析数据
        data = []
        start_date = datetime(2024, 1, 1)
        
        for day in range(60):
            date = start_date + timedelta(days=day)
            n_daily_users = int(500 + np.sin(day/10) * 100 + np.random.normal(0, 50))
            
            for i in range(n_daily_users):
                is_payer = np.random.random() < 0.08
                revenue = 0
                if is_payer:
                    revenue = np.random.choice([0.99, 4.99, 9.99, 19.99, 49.99], 
                                              p=[0.4, 0.3, 0.15, 0.1, 0.05])
                
                data.append({
                    'date': date,
                    'user_id': f'user_{day}_{i}',
                    'revenue': revenue
                })
        
        return pd.DataFrame(data)


def main():
    parser = argparse.ArgumentParser(description='游戏数据分析工具')
    parser.add_argument('--action', choices=['retention', 'rfm', 'level', 'revenue', 'demo'],
                       required=True, help='分析类型')
    parser.add_argument('--input', help='输入数据文件路径')
    parser.add_argument('--output', default='./output', help='输出目录')
    
    args = parser.parse_args()
    
    import os
    os.makedirs(args.output, exist_ok=True)
    
    ga = GameAnalytics()
    
    if args.action == 'demo':
        print("生成示例数据并进行完整分析...")
        
        # 留存分析
        print("\n1. 留存分析")
        retention_data = generate_sample_data('retention', 1000)
        retention_data.to_csv(f'{args.output}/sample_retention.csv', index=False)
        ga.data = retention_data
        retention_matrix = ga.calculate_retention()
        ga.plot_retention_heatmap(retention_matrix, f'{args.output}/retention_heatmap.png')
        summary = ga.retention_summary(retention_matrix)
        print(summary)
        
        # RFM分析
        print("\n2. RFM分析")
        rfm_data = generate_sample_data('rfm', 1000)
        rfm_data.to_csv(f'{args.output}/sample_rfm.csv', index=False)
        ga.data = rfm_data
        rfm_df = ga.rfm_analysis()
        ga.plot_rfm_distribution(rfm_df, f'{args.output}/rfm_distribution.png')
        print(rfm_df['segment'].value_counts())
        
        # 关卡分析
        print("\n3. 关卡难度分析")
        level_data = generate_sample_data('level')
        level_data.to_csv(f'{args.output}/sample_level.csv', index=False)
        ga.data = level_data
        level_df = ga.level_difficulty_analysis()
        ga.plot_level_difficulty(level_df, f'{args.output}/level_difficulty.png')
        print(level_df[['level_id', 'completion_rate', 'difficulty_rating']].head(10))
        
        # 收入分析
        print("\n4. 收入分析")
        revenue_data = generate_sample_data('revenue')
        revenue_data.to_csv(f'{args.output}/sample_revenue.csv', index=False)
        ga.data = revenue_data
        revenue_df = ga.revenue_analysis()
        ga.plot_revenue_trend(revenue_df, f'{args.output}/revenue_trend.png')
        print(revenue_df.describe())
        
        print(f"\n✅ 分析完成！所有结果已保存到 {args.output}/")
    
    else:
        if not args.input:
            print("错误: 非demo模式需要提供 --input 参数")
            return
        
        ga.load_data(args.input)
        
        if args.action == 'retention':
            retention_matrix = ga.calculate_retention()
            ga.plot_retention_heatmap(retention_matrix, f'{args.output}/retention_heatmap.png')
            summary = ga.retention_summary(retention_matrix)
            summary.to_csv(f'{args.output}/retention_summary.csv')
            print(summary)
        
        elif args.action == 'rfm':
            rfm_df = ga.rfm_analysis()
            ga.plot_rfm_distribution(rfm_df, f'{args.output}/rfm_distribution.png')
            rfm_df.to_csv(f'{args.output}/rfm_segments.csv', index=False)
            print(rfm_df['segment'].value_counts())
        
        elif args.action == 'level':
            level_df = ga.level_difficulty_analysis()
            ga.plot_level_difficulty(level_df, f'{args.output}/level_difficulty.png')
            level_df.to_csv(f'{args.output}/level_analysis.csv', index=False)
            print(level_df)
        
        elif args.action == 'revenue':
            revenue_df = ga.revenue_analysis()
            ga.plot_revenue_trend(revenue_df, f'{args.output}/revenue_trend.png')
            revenue_df.to_csv(f'{args.output}/revenue_analysis.csv')
            print(revenue_df.describe())


if __name__ == '__main__':
    main()
