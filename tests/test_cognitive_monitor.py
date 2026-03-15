#!/usr/bin/env python3
"""
认知负载监控 - 单元测试
测试核心功能：评分算法、数据处理等
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入被测函数（简化版本，避免依赖外部服务）
from cognitive_monitor import (
    calculate_cognitive_score,
    get_session_label,
    format_tokens,
    format_duration_short
)

class TestCognitiveScore(unittest.TestCase):
    """测试认知评分算法"""
    
    def test_idle_state(self):
        """空闲状态评分 < 20%"""
        data = {
            'pending_count': 0,
            'processing_count': 0,
            'total_tokens': 0,
            'max_wait_seconds': 0
        }
        score = calculate_cognitive_score(**data)
        self.assertLess(score, 20)
        self.assertEqual(score, 0)  # 完全空闲
    
    def test_low_load(self):
        """低负载 20-40%"""
        data = {
            'pending_count': 1,
            'processing_count': 0,
            'total_tokens': 5000,
            'max_wait_seconds': 5
        }
        score = calculate_cognitive_score(**data)
        self.assertGreaterEqual(score, 20)
        self.assertLess(score, 40)
    
    def test_medium_load(self):
        """中等负载 40-60%"""
        data = {
            'pending_count': 2,
            'processing_count': 1,
            'total_tokens': 50000,
            'max_wait_seconds': 20
        }
        score = calculate_cognitive_score(**data)
        self.assertGreaterEqual(score, 40)
        self.assertLess(score, 60)
    
    def test_high_load(self):
        """高负载 >= 60%"""
        data = {
            'pending_count': 5,
            'processing_count': 3,
            'total_tokens': 200000,
            'max_wait_seconds': 60
        }
        score = calculate_cognitive_score(**data)
        self.assertGreaterEqual(score, 60)

class TestFormatFunctions(unittest.TestCase):
    """测试格式化函数"""
    
    def test_format_tokens_small(self):
        """小数字直接显示"""
        self.assertEqual(format_tokens(500), '500')
    
    def test_format_tokens_k(self):
        """千位显示为k"""
        self.assertEqual(format_tokens(1500), '1.5k')
        self.assertEqual(format_tokens(10000), '10.0k')
    
    def test_format_tokens_m(self):
        """百万位显示为M"""
        self.assertEqual(format_tokens(1500000), '1.5M')
    
    def test_format_duration_seconds(self):
        """秒格式"""
        self.assertEqual(format_duration_short(45), '45s')
    
    def test_format_duration_minutes(self):
        """分钟格式"""
        self.assertEqual(format_duration_short(90), '1m')
        self.assertEqual(format_duration_short(300), '5m')
    
    def test_format_duration_hours(self):
        """小时格式"""
        self.assertEqual(format_duration_short(3600), '1h')
        self.assertEqual(format_duration_short(7200), '2h')

class TestSessionLabel(unittest.TestCase):
    """测试会话标签生成"""
    
    def test_srpg_label(self):
        """战棋研究标签"""
        content = '{"role": "user", "content": "分析天地劫的SRPG技能数据"}'
        result = get_session_label(content, 'test.txt')
        self.assertTrue('战棋' in result or 'SRPG' in result or '天地劫' in result)
    
    def test_godot_label(self):
        """游戏开发标签"""
        self.assertIn('开发', get_session_label('Godot导出设置', 'test.txt'))
    
    def test_default_label(self):
        """默认标签"""
        result = get_session_label('一些普通对话', 'test.txt')
        self.assertTrue(result.startswith('🟢'))

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
