#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRPG 数值平衡性测试脚本
===================
用于模拟战斗、统计胜率、检测数值异常

使用方法:
    python balance_test.py --mode full
    python balance_test.py --mode quick --battles 500
    python balance_test.py --sensitivity

作者: SRPG Designer Skill
版本: 1.0
"""

import random
import json
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import statistics


# ==================== 数据模型 ====================

@dataclass
class Character:
    """角色数据模型"""
    name: str
    profession: str  # 职业
    level: int
    
    # 基础属性
    hp: int
    attack: int
    defense: int
    speed: int
    technique: int  # 技巧/技量
    luck: int       # 幸运
    
    # 战斗属性
    mobility: int   # 移动力
    range_: int     # 攻击射程
    
    # 成长率 (用于升级模拟)
    growth_hp: float = 0.8
    growth_attack: float = 0.7
    growth_defense: float = 0.5
    growth_speed: float = 0.6
    growth_technique: float = 0.6
    growth_luck: float = 0.5
    
    def get_max_hp(self) -> int:
        """获取当前最大HP"""
        return self.hp
    
    def clone(self) -> 'Character':
        """克隆角色 (用于战斗模拟)"""
        return Character(
            name=self.name,
            profession=self.profession,
            level=self.level,
            hp=self.hp,
            attack=self.attack,
            defense=self.defense,
            speed=self.speed,
            technique=self.technique,
            luck=self.luck,
            mobility=self.mobility,
            range_=self.range_,
            growth_hp=self.growth_hp,
            growth_attack=self.growth_attack,
            growth_defense=self.growth_defense,
            growth_speed=self.growth_speed,
            growth_technique=self.growth_technique,
            growth_luck=self.growth_luck
        )


@dataclass
class BattleResult:
    """战斗结果"""
    winner: str
    turns: int
    attacker_damage_dealt: int
    defender_damage_dealt: int
    attacker_hp_remaining: int
    defender_hp_remaining: int
    hit_count_attacker: int
    hit_count_defender: int
    crit_count_attacker: int
    crit_count_defender: int


# ==================== 职业模板 ====================

PROFESSION_TEMPLATES = {
    "战士": {
        "hp": 28, "attack": 12, "defense": 8, "speed": 8,
        "technique": 10, "luck": 8,
        "mobility": 5, "range_": 1,
        "growth_hp": 0.9, "growth_attack": 0.8, "growth_defense": 0.6,
        "growth_speed": 0.5, "growth_technique": 0.5, "growth_luck": 0.4
    },
    "骑士": {
        "hp": 32, "attack": 10, "defense": 12, "speed": 5,
        "technique": 8, "luck": 10,
        "mobility": 4, "range_": 1,
        "growth_hp": 0.85, "growth_attack": 0.65, "growth_defense": 0.8,
        "growth_speed": 0.35, "growth_technique": 0.45, "growth_luck": 0.5
    },
    "弓手": {
        "hp": 20, "attack": 11, "defense": 5, "speed": 10,
        "technique": 12, "luck": 9,
        "mobility": 4, "range_": 3,
        "growth_hp": 0.65, "growth_attack": 0.75, "growth_defense": 0.35,
        "growth_speed": 0.6, "growth_technique": 0.7, "growth_luck": 0.6
    },
    "法师": {
        "hp": 18, "attack": 14, "defense": 4, "speed": 8,
        "technique": 11, "luck": 8,
        "mobility": 4, "range_": 2,
        "growth_hp": 0.55, "growth_attack": 0.85, "growth_defense": 0.3,
        "growth_speed": 0.55, "growth_technique": 0.65, "growth_luck": 0.55
    },
    "骑兵": {
        "hp": 25, "attack": 11, "defense": 7, "speed": 12,
        "technique": 9, "luck": 7,
        "mobility": 7, "range_": 1,
        "growth_hp": 0.8, "growth_attack": 0.7, "growth_defense": 0.5,
        "growth_speed": 0.75, "growth_technique": 0.5, "growth_luck": 0.4
    }
}


# ==================== 战斗公式配置 ====================

class CombatConfig:
    """战斗公式配置"""
    
    # 伤害公式参数
    DAMAGE_FORMULA = "subtraction"  # subtraction | percentage | hybrid
    DEFENSE_CONSTANT_K = 100        # 百分比公式中的K值
    HYBRID_DEFENSE_FACTOR = 0.5     # 混合公式中防御的系数
    
    # 伤害波动
    DAMAGE_VARIANCE = 0.1           # ±10% 波动
    
    # 命中公式参数
    BASE_HIT_RATE = 85              # 基础命中率
    HIT_PER_TECHNIQUE = 0.5         # 每点技巧提供的命中
    EVADE_PER_SPEED = 0.5           # 每点速度提供的回避
    MIN_HIT_RATE = 5                # 最低命中率
    MAX_HIT_RATE = 95               # 最高命中率
    
    # 暴击公式参数
    BASE_CRIT_RATE = 5              # 基础暴击率
    CRIT_PER_TECHNIQUE_DIFF = 0.2   # 每点技巧差提供的暴击
    CRIT_DAMAGE_MULTIPLIER = 1.5    # 暴击伤害倍数
    MAX_CRIT_RATE = 30              # 最高暴击率
    
    # 克制关系
    ADVANTAGE_BONUS = 0.25          # 克制时+25%伤害
    DISADVANTAGE_PENALTY = 0.20     # 被克时-20%伤害


# ==================== 战斗模拟器 ====================

class CombatSimulator:
    """战斗模拟器"""
    
    # 职业克制表 (攻击方 → 防御方)
    ADVANTAGE_MATRIX = {
        "战士": ["骑兵"],
        "骑兵": ["弓手", "法师"],
        "弓手": ["法师"],
        "法师": ["骑士", "战士"],
        "骑士": ["战士", "弓手"]
    }
    
    def __init__(self, config: CombatConfig = None):
        self.config = config or CombatConfig()
    
    def calculate_damage(self, attacker: Character, defender: Character) -> Tuple[int, bool, bool]:
        """
        计算伤害
        返回: (伤害值, 是否命中, 是否暴击)
        """
        # 1. 命中率判定
        hit_rate = self._calculate_hit_rate(attacker, defender)
        is_hit = random.randint(1, 100) <= hit_rate
        
        if not is_hit:
            return 0, False, False
        
        # 2. 基础伤害计算
        if self.config.DAMAGE_FORMULA == "subtraction":
            base_damage = max(1, attacker.attack - defender.defense)
        elif self.config.DAMAGE_FORMULA == "percentage":
            reduction = defender.defense / (defender.defense + self.config.DEFENSE_CONSTANT_K)
            base_damage = max(1, int(attacker.attack * (1 - reduction)))
        else:  # hybrid
            base = max(1, attacker.attack - int(defender.defense * self.config.HYBRID_DEFENSE_FACTOR))
            reduction = defender.defense / (defender.defense + self.config.DEFENSE_CONSTANT_K)
            base_damage = int(base * (1 - reduction * self.config.HYBRID_DEFENSE_FACTOR))
        
        # 3. 暴击判定
        crit_rate = self._calculate_crit_rate(attacker, defender)
        is_crit = random.randint(1, 100) <= crit_rate
        
        # 4. 克制系数
        advantage_multiplier = self._calculate_advantage(attacker, defender)
        
        # 5. 最终伤害
        damage = int(base_damage * advantage_multiplier)
        if is_crit:
            damage = int(damage * self.config.CRIT_DAMAGE_MULTIPLIER)
        
        # 6. 伤害波动
        variance = random.uniform(-self.config.DAMAGE_VARIANCE, self.config.DAMAGE_VARIANCE)
        damage = int(damage * (1 + variance))
        
        return max(1, damage), True, is_crit
    
    def _calculate_hit_rate(self, attacker: Character, defender: Character) -> int:
        """计算命中率"""
        base = self.config.BASE_HIT_RATE
        tech_bonus = (attacker.technique - defender.speed) * self.config.HIT_PER_TECHNIQUE
        hit_rate = base + tech_bonus
        return max(self.config.MIN_HIT_RATE, min(self.config.MAX_HIT_RATE, int(hit_rate)))
    
    def _calculate_crit_rate(self, attacker: Character, defender: Character) -> int:
        """计算暴击率"""
        base = self.config.BASE_CRIT_RATE
        tech_diff = attacker.technique - defender.luck
        crit_rate = base + tech_diff * self.config.CRIT_PER_TECHNIQUE_DIFF
        return max(0, min(self.config.MAX_CRIT_RATE, int(crit_rate)))
    
    def _calculate_advantage(self, attacker: Character, defender: Character) -> float:
        """计算克制系数"""
        advantage_targets = self.ADVANTAGE_MATRIX.get(attacker.profession, [])
        if defender.profession in advantage_targets:
            return 1 + self.config.ADVANTAGE_BONUS
        
        # 检查被克
        defender_targets = self.ADVANTAGE_MATRIX.get(defender.profession, [])
        if attacker.profession in defender_targets:
            return 1 - self.config.DISADVANTAGE_PENALTY
        
        return 1.0
    
    def simulate_battle(self, char1: Character, char2: Character, max_turns: int = 50) -> BattleResult:
        """
        模拟一场1v1战斗
        
        战斗规则:
        - 双方轮流攻击
        - 速度高的先攻
        - 直到一方HP归零或达到最大回合数
        """
        attacker = char1.clone()
        defender = char2.clone()
        
        # 速度高的先攻
        if defender.speed > attacker.speed:
            attacker, defender = defender, attacker
        
        attacker_hp = attacker.hp
        defender_hp = defender.hp
        
        damage_dealt_attacker = 0
        damage_dealt_defender = 0
        hit_count_attacker = 0
        hit_count_defender = 0
        crit_count_attacker = 0
        crit_count_defender = 0
        
        turn = 0
        
        while turn < max_turns:
            turn += 1
            
            # 攻击方回合
            damage, hit, crit = self.calculate_damage(attacker, defender)
            if hit:
                hit_count_attacker += 1
                if crit:
                    crit_count_attacker += 1
                defender_hp -= damage
                damage_dealt_attacker += damage
            
            if defender_hp <= 0:
                return BattleResult(
                    winner=attacker.name,
                    turns=turn,
                    attacker_damage_dealt=damage_dealt_attacker,
                    defender_damage_dealt=damage_dealt_defender,
                    attacker_hp_remaining=attacker_hp,
                    defender_hp_remaining=0,
                    hit_count_attacker=hit_count_attacker,
                    hit_count_defender=hit_count_defender,
                    crit_count_attacker=crit_count_attacker,
                    crit_count_defender=crit_count_defender
                )
            
            # 防御方回合
            damage, hit, crit = self.calculate_damage(defender, attacker)
            if hit:
                hit_count_defender += 1
                if crit:
                    crit_count_defender += 1
                attacker_hp -= damage
                damage_dealt_defender += damage
            
            if attacker_hp <= 0:
                return BattleResult(
                    winner=defender.name,
                    turns=turn,
                    attacker_damage_dealt=damage_dealt_attacker,
                    defender_damage_dealt=damage_dealt_defender,
                    attacker_hp_remaining=0,
                    defender_hp_remaining=defender_hp,
                    hit_count_attacker=hit_count_attacker,
                    hit_count_defender=hit_count_defender,
                    crit_count_attacker=crit_count_attacker,
                    crit_count_defender=crit_count_defender
                )
        
        # 超时判定: HP多者胜
        if attacker_hp > defender_hp:
            winner = attacker.name
        elif defender_hp > attacker_hp:
            winner = defender.name
        else:
            winner = "平局"
        
        return BattleResult(
            winner=winner,
            turns=turn,
            attacker_damage_dealt=damage_dealt_attacker,
            defender_damage_dealt=damage_dealt_defender,
            attacker_hp_remaining=max(0, attacker_hp),
            defender_hp_remaining=max(0, defender_hp),
            hit_count_attacker=hit_count_attacker,
            hit_count_defender=hit_count_defender,
            crit_count_attacker=crit_count_attacker,
            crit_count_defender=crit_count_defender
        )


# ==================== 平衡性测试 ====================

class BalanceTester:
    """平衡性测试器"""
    
    def __init__(self, simulator: CombatSimulator = None):
        self.simulator = simulator or CombatSimulator()
    
    def create_character_from_template(self, name: str, profession: str, level: int = 1) -> Character:
        """从模板创建角色"""
        template = PROFESSION_TEMPLATES.get(profession, PROFESSION_TEMPLATES["战士"])
        
        char = Character(
            name=name,
            profession=profession,
            level=level,
            hp=template["hp"],
            attack=template["attack"],
            defense=template["defense"],
            speed=template["speed"],
            technique=template["technique"],
            luck=template["luck"],
            mobility=template["mobility"],
            range_=template["range_"],
            growth_hp=template["growth_hp"],
            growth_attack=template["growth_attack"],
            growth_defense=template["growth_defense"],
            growth_speed=template["growth_speed"],
            growth_technique=template["growth_technique"],
            growth_luck=template["growth_luck"]
        )
        
        # 根据等级应用成长
        for _ in range(level - 1):
            self._level_up(char)
        
        return char
    
    def _level_up(self, char: Character):
        """升级角色"""
        import random
        if random.randint(1, 100) <= char.growth_hp * 100:
            char.hp += 1
        if random.randint(1, 100) <= char.growth_attack * 100:
            char.attack += 1
        if random.randint(1, 100) <= char.growth_defense * 100:
            char.defense += 1
        if random.randint(1, 100) <= char.growth_speed * 100:
            char.speed += 1
        if random.randint(1, 100) <= char.growth_technique * 100:
            char.technique += 1
        if random.randint(1, 100) <= char.growth_luck * 100:
            char.luck += 1
        char.level += 1
    
    def run_matchup_test(self, profession1: str, profession2: str, 
                         battles: int = 1000, level: int = 10) -> Dict:
        """
        运行两个职业的对战测试
        
        返回统计信息:
        - 胜率
        - 平均回合数
        - 平均伤害
        - 暴击率
        """
        char1 = self.create_character_from_template(f"{profession1}_A", profession1, level)
        char2 = self.create_character_from_template(f"{profession2}_B", profession2, level)
        
        results = []
        for i in range(battles):
            # 交替先后手
            if i % 2 == 0:
                result = self.simulator.simulate_battle(char1, char2)
            else:
                result = self.simulator.simulate_battle(char2, char1)
            results.append(result)
        
        # 统计
        char1_wins = sum(1 for r in results if r.winner == char1.name)
        char2_wins = sum(1 for r in results if r.winner == char2.name)
        draws = battles - char1_wins - char2_wins
        
        turns = [r.turns for r in results]
        
        # 汇总伤害统计
        total_hits_1 = sum(r.hit_count_attacker for r in results)
        total_crits_1 = sum(r.crit_count_attacker for r in results)
        total_hits_2 = sum(r.hit_count_defender for r in results)
        total_crits_2 = sum(r.crit_count_defender for r in results)
        
        crit_rate_1 = (total_crits_1 / total_hits_1 * 100) if total_hits_1 > 0 else 0
        crit_rate_2 = (total_crits_2 / total_hits_2 * 100) if total_hits_2 > 0 else 0
        
        return {
            "profession1": profession1,
            "profession2": profession2,
            "battles": battles,
            "level": level,
            "win_rate_p1": char1_wins / battles * 100,
            "win_rate_p2": char2_wins / battles * 100,
            "draw_rate": draws / battles * 100,
            "avg_turns": statistics.mean(turns),
            "min_turns": min(turns),
            "max_turns": max(turns),
            "crit_rate_p1": crit_rate_1,
            "crit_rate_p2": crit_rate_2
        }
    
    def run_full_balance_test(self, battles_per_matchup: int = 1000, level: int = 10) -> Dict:
        """
        运行全职业平衡性测试
        
        测试所有职业两两组合的对战
        """
        professions = list(PROFESSION_TEMPLATES.keys())
        results = {}
        
        print(f"开始全职业平衡测试 (每对 {battles_per_matchup} 场战斗, 等级 {level})")
        print("=" * 60)
        
        for i, p1 in enumerate(professions):
            for p2 in professions[i:]:  # 只测试一半，避免重复
                print(f"测试: {p1} vs {p2} ...", end=" ")
                result = self.run_matchup_test(p1, p2, battles_per_matchup, level)
                key = f"{p1}_vs_{p2}"
                results[key] = result
                
                if p1 == p2:
                    print(f"胜率: {result['win_rate_p1']:.1f}% (理论应接近50%)")
                else:
                    print(f"胜率: {result['win_rate_p1']:.1f}% vs {result['win_rate_p2']:.1f}%")
        
        return results
    
    def detect_balance_issues(self, results: Dict, tolerance: float = 15.0) -> List[Dict]:
        """
        检测平衡性问题
        
        标记胜率偏差超过容忍度的对战组合
        """
        issues = []
        
        for key, result in results.items():
            p1, p2 = result["profession1"], result["profession2"]
            
            # 同职业对战应该接近50%
            if p1 == p2:
                deviation = abs(result["win_rate_p1"] - 50)
                if deviation > tolerance:
                    issues.append({
                        "type": "同职业偏差",
                        "matchup": key,
                        "deviation": deviation,
                        "details": f"{p1} vs {p1} 胜率偏差 {deviation:.1f}% (理论应为50%)"
                    })
            else:
                # 不同职业对战检查极端不平衡
                win_rate_diff = abs(result["win_rate_p1"] - result["win_rate_p2"])
                if win_rate_diff > 2 * tolerance:  # 40%胜率差视为严重不平衡
                    dominant = p1 if result["win_rate_p1"] > result["win_rate_p2"] else p2
                    issues.append({
                        "type": "严重不平衡",
                        "matchup": key,
                        "win_rate_diff": win_rate_diff,
                        "dominant": dominant,
                        "details": f"{p1} vs {p2} 胜率差 {win_rate_diff:.1f}%, {dominant} 过强"
                    })
                elif win_rate_diff > tolerance:  # 轻度不平衡
                    dominant = p1 if result["win_rate_p1"] > result["win_rate_p2"] else p2
                    issues.append({
                        "type": "轻度不平衡",
                        "matchup": key,
                        "win_rate_diff": win_rate_diff,
                        "dominant": dominant,
                        "details": f"{p1} vs {p2} 胜率差 {win_rate_diff:.1f}%, {dominant} 略强"
                    })
        
        return issues
    
    def sensitivity_analysis(self, profession: str, attribute: str, 
                            variations: List[float] = None, battles: int = 500) -> Dict:
        """
        数值敏感性分析
        
        测试某个属性的变化对胜率的影响
        """
        if variations is None:
            variations = [-0.2, -0.1, 0, 0.1, 0.2]  # ±20%, ±10%
        
        results = {}
        base_char = self.create_character_from_template(profession, profession, 10)
        
        # 找一个标准对手
        opponent_prof = "战士" if profession != "战士" else "骑士"
        opponent = self.create_character_from_template(opponent_prof, opponent_prof, 10)
        
        print(f"\n敏感性分析: {profession} 的 {attribute} 属性")
        print("-" * 50)
        
        for var in variations:
            test_char = base_char.clone()
            
            # 应用变化
            current_val = getattr(test_char, attribute)
            new_val = int(current_val * (1 + var))
            setattr(test_char, attribute, new_val)
            test_char.name = f"{profession}_{var:+.0%}"
            
            # 运行测试
            wins = 0
            for i in range(battles):
                if i % 2 == 0:
                    result = self.simulator.simulate_battle(test_char, opponent)
                    if result.winner == test_char.name:
                        wins += 1
                else:
                    result = self.simulator.simulate_battle(opponent, test_char)
                    if result.winner != opponent.name:  # 平局或test_char胜
                        wins += 1
            
            win_rate = wins / battles * 100
            results[f"{var:+.0%}"] = win_rate
            print(f"  {attribute} {var:+.0%} ({current_val} → {new_val}): 胜率 {win_rate:.1f}%")
        
        return results


# ==================== 输出格式化 ====================

def print_balance_report(results: Dict, issues: List[Dict]):
    """打印平衡性报告"""
    print("\n" + "=" * 70)
    print("SRPG 数值平衡性测试报告")
    print("=" * 70)
    
    # 汇总表格
    print("\n【对战胜率矩阵】")
    print("-" * 70)
    
    professions = list(PROFESSION_TEMPLATES.keys())
    
    # 打印表头
    header = "{:10}".format("")
    for p in professions:
        header += "{:>10}".format(p[:8])
    print(header)
    
    # 打印每行
    for p1 in professions:
        row = "{:10}".format(p1[:8])
        for p2 in professions:
            key = f"{p1}_vs_{p2}" if p1 <= p2 else f"{p2}_vs_{p1}"
            if key in results:
                if p1 == p2:
                    win_rate = 50.0  # 同职业对战显示50%
                else:
                    result = results[key]
                    win_rate = result["win_rate_p1"] if result["profession1"] == p1 else result["win_rate_p2"]
                row += "{:>9.1f}%".format(win_rate)
            else:
                row += "{:>10}".format("-")
        print(row)
    
    # 平均回合数
    print("\n【战斗时长统计】")
    print("-" * 70)
    all_turns = [r["avg_turns"] for r in results.values()]
    print(f"  平均回合数: {statistics.mean(all_turns):.1f}")
    print(f"  最短战斗: {min(r['min_turns'] for r in results.values())} 回合")
    print(f"  最长战斗: {max(r['max_turns'] for r in results.values())} 回合")
    
    # 平衡性问题
    print("\n【平衡性问题检测】")
    print("-" * 70)
    
    if not issues:
        print("  ✅ 未发现明显平衡性问题")
    else:
        severe = [i for i in issues if i["type"] == "严重不平衡"]
        mild = [i for i in issues if i["type"] == "轻度不平衡"]
        other = [i for i in issues if i["type"] not in ["严重不平衡", "轻度不平衡"]]
        
        if severe:
            print(f"\n  ⚠️  严重不平衡 ({len(severe)}项):")
            for issue in severe:
                print(f"     - {issue['details']}")
        
        if mild:
            print(f"\n  ⚡ 轻度不平衡 ({len(mild)}项):")
            for issue in mild:
                print(f"     - {issue['details']}")
        
        if other:
            print(f"\n  ℹ️  其他问题 ({len(other)}项):")
            for issue in other:
                print(f"     - {issue['details']}")
    
    # 建议
    print("\n【优化建议】")
    print("-" * 70)
    
    # 统计各职业胜率
    profession_win_rates = defaultdict(list)
    for key, result in results.items():
        p1, p2 = result["profession1"], result["profession2"]
        if p1 != p2:
            profession_win_rates[p1].append(result["win_rate_p1"])
            profession_win_rates[p2].append(result["win_rate_p2"])
    
    avg_win_rates = {p: statistics.mean(rates) for p, rates in profession_win_rates.items()}
    
    print(f"  各职业平均胜率:")
    for p, rate in sorted(avg_win_rates.items(), key=lambda x: x[1], reverse=True):
        status = "🔥 偏强" if rate > 60 else "❄️ 偏弱" if rate < 40 else "✅ 正常"
        print(f"    {p:8}: {rate:5.1f}% {status}")
    
    print("\n" + "=" * 70)


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description="SRPG 数值平衡性测试工具")
    parser.add_argument("--mode", choices=["quick", "full", "matchup", "sensitivity"], 
                       default="quick", help="测试模式")
    parser.add_argument("--battles", type=int, default=1000, help="每场对战模拟次数")
    parser.add_argument("--level", type=int, default=10, help="测试角色等级")
    parser.add_argument("--p1", type=str, help="职业1 (用于 matchup 模式)")
    parser.add_argument("--p2", type=str, help="职业2 (用于 matchup 模式)")
    parser.add_argument("--profession", type=str, help="职业 (用于 sensitivity 模式)")
    parser.add_argument("--attribute", type=str, default="attack", 
                       help="属性名 (用于 sensitivity 模式)")
    parser.add_argument("--output", type=str, help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 初始化
    simulator = CombatSimulator()
    tester = BalanceTester(simulator)
    
    if args.mode == "quick":
        # 快速测试: 少量对战
        print("运行快速平衡测试...")
        results = tester.run_full_balance_test(battles_per_matchup=args.battles // 2, level=args.level)
        issues = tester.detect_balance_issues(results)
        print_balance_report(results, issues)
    
    elif args.mode == "full":
        # 完整测试
        print("运行完整平衡测试...")
        results = tester.run_full_balance_test(battles_per_matchup=args.battles, level=args.level)
        issues = tester.detect_balance_issues(results)
        print_balance_report(results, issues)
    
    elif args.mode == "matchup":
        # 单一对战测试
        if not args.p1 or not args.p2:
            print("错误: matchup 模式需要指定 --p1 和 --p2")
            return
        
        result = tester.run_matchup_test(args.p1, args.p2, args.battles, args.level)
        print(f"\n对战结果: {args.p1} vs {args.p2}")
        print(f"  {args.p1} 胜率: {result['win_rate_p1']:.1f}%")
        print(f"  {args.p2} 胜率: {result['win_rate_p2']:.1f}%")
        print(f"  平局率: {result['draw_rate']:.1f}%")
        print(f"  平均回合: {result['avg_turns']:.1f}")
        print(f"  {args.p1} 暴击率: {result['crit_rate_p1']:.1f}%")
        print(f"  {args.p2} 暴击率: {result['crit_rate_p2']:.1f}%")
    
    elif args.mode == "sensitivity":
        # 敏感性分析
        if not args.profession:
            print("错误: sensitivity 模式需要指定 --profession")
            return
        
        tester.sensitivity_analysis(args.profession, args.attribute, battles=args.battles)
    
    # 保存结果
    if args.output and 'results' in locals():
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
