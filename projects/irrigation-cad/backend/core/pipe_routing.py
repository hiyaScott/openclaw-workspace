"""
管路路径规划算法 - 干线+支线模式

核心约束:
1. 主管必须从水源出发，连接所有绿化区域
2. 主管不能穿过禁区（房屋）
3. 主管穿过硬化区域时，自动标记过路保护管（de63，控制线与主管共用）
4. 支管从主管分岔进入各绿化区域，连接喷头
5. 支管也不能穿过禁区
6. 阀门位置规则（Scott确认）:
   - 放在主管和支管连接处
   - 靠绿化区域边缘布置
   - 不同类型喷头不能共用阀门
   - 一个阀门下带的喷头数量不能超过水源供水流量
"""

from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
import math
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import nearest_points


@dataclass
class Zone:
    """区域定义"""
    id: str
    polygon: Polygon  # 区域多边形
    zone_type: str    # 'green'绿化区 / 'forbidden'禁区 / 'hard'硬化区
    
    # 绿化区特有属性
    plant_type: Optional[str] = None  # 'lawn'草坪 / 'shrub'灌木 / 'flower'花卉
    sprinkler_positions: List[Tuple[float, float]] = None
    
    # 硬化区特有属性
    requires_conduit: bool = False  # 是否需要过路保护管


@dataclass  
class PipeRoute:
    """管路路径"""
    path: List[Tuple[float, float]]  # 路径点序列
    pipe_type: str                   # 'main'主管 / 'branch'支管 / 'control'控制线
    diameter: float                  # 管径(mm)
    
    # 过路管信息（穿过硬化区时）
    conduit_sections: List[Tuple[int, int]] = None  # [(start_idx, end_idx), ...]
    conduit_diameter: float = None


@dataclass
class IrrigationDesign:
    """完整灌溉设计方案"""
    zones: List[Zone]
    water_source: Tuple[float, float]
    
    # 生成的管路
    main_pipes: List[PipeRoute]
    branch_pipes: List[PipeRoute]
    control_lines: List[PipeRoute]
    
    # 过路管统计
    conduit_sections: List[Dict]  # 过路管位置和规格
    
    # 阀门位置
    valve_positions: List[Tuple[float, float]]


class PipeRoutePlanner:
    """管路路径规划器"""
    
    def __init__(self, zones: List[Zone], water_source: Tuple[float, float]):
        self.zones = zones
        self.water_source = water_source
        
        # 分类区域
        self.green_zones = [z for z in zones if z.zone_type == 'green']
        self.forbidden_zones = [z for z in zones if z.zone_type == 'forbidden']
        self.hard_zones = [z for z in zones if z.zone_type == 'hard']
        
        # 合并禁区用于碰撞检测
        self.forbidden_union = None
        if self.forbidden_zones:
            from shapely.ops import unary_union
            self.forbidden_union = unary_union([z.polygon for z in self.forbidden_zones])
    
    def plan_route(self, water_flow: float = 2.5) -> IrrigationDesign:
        """规划完整管路系统"""
        design = IrrigationDesign(
            zones=self.zones,
            water_source=self.water_source,
            main_pipes=[],
            branch_pipes=[],
            control_lines=[],
            conduit_sections=[],
            valve_positions=[]
        )
        
        # Step 1: 规划主管主干线
        main_route = self._plan_main_route()
        design.main_pipes.append(main_route)
        
        # Step 2: 识别过路管位置（de63统一规格，控制线共用）
        conduit_sections = self._identify_conduit_sections(main_route)
        design.conduit_sections = conduit_sections
        main_route.conduit_sections = [(s['start_idx'], s['end_idx']) for s in conduit_sections]
        
        # Step 3: 规划各绿化区的支管
        for zone in self.green_zones:
            branch_routes = self._plan_branch_pipes(zone, main_route)
            design.branch_pipes.extend(branch_routes)
        
        # Step 4: 规划阀门位置（Scott规则）
        valve_positions = self._plan_valve_positions(design, water_flow)
        design.valve_positions = valve_positions
        
        # Step 5: 规划控制线（从水源到各阀门，跟随主管，共用de63过路管）
        control_routes = self._plan_control_lines(design)
        design.control_lines.extend(control_routes)
        
        return design
    
    def _plan_main_route(self) -> PipeRoute:
        """
        规划主管主干线
        
        策略：
        1. 找出连接水源和所有绿化区的最短路径（考虑禁区避让）
        2. 优先沿硬化区边缘走（方便施工和标记过路管）
        3. 使用A*算法或启发式路径规划
        """
        # 简化版：先连接水源到各绿化区中心的最近点
        # 然后沿绿化区外围连接成主干线
        
        waypoints = [self.water_source]
        
        # 找到各绿化区边缘上离水源最近的点
        for zone in self.green_zones:
            nearest_point = self._find_nearest_point_on_zone(self.water_source, zone)
            waypoints.append(nearest_point)
        
        # 用最近邻连接这些点，形成主干线路径
        path = self._connect_waypoints_avoiding_obstacles(waypoints)
        
        return PipeRoute(
            path=path,
            pipe_type='main',
            diameter=32.0,  # 默认主管32mm
            conduit_sections=[],
            conduit_diameter=63.0  # de63统一过路保护管
        )
    
    def _find_nearest_point_on_zone(self, source: Tuple[float, float], zone: Zone) -> Tuple[float, float]:
        """找到zone边界上离source最近的点"""
        point = Point(source)
        boundary = zone.polygon.boundary
        nearest = nearest_points(point, boundary)[1]
        return (nearest.x, nearest.y)
    
    def _connect_waypoints_avoiding_obstacles(self, waypoints: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        连接路径点，避开禁区
        
        简化实现：
        - 先尝试直线连接
        - 如果穿过禁区，则绕行禁区边界
        """
        if len(waypoints) < 2:
            return waypoints
        
        full_path = [waypoints[0]]
        
        for i in range(len(waypoints) - 1):
            start = waypoints[i]
            end = waypoints[i + 1]
            
            # 尝试直线路径
            direct_line = LineString([start, end])
            
            if self._line_intersects_forbidden(direct_line):
                # 需要绕行
                detour = self._calculate_detour(start, end)
                full_path.extend(detour[1:])  # 跳过第一个点（已添加）
            else:
                full_path.append(end)
        
        return full_path
    
    def _line_intersects_forbidden(self, line: LineString) -> bool:
        """检查线段是否与禁区相交"""
        if self.forbidden_union is None:
            return False
        return line.intersects(self.forbidden_union)
    
    def _calculate_detour(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        计算绕行禁区的路径
        
        简化策略：
        - 找到禁区边界上与start和end最近的两个点
        - 沿边界连接这两点（顺时针或逆时针取短边）
        """
        # 实际实现需要更复杂的几何计算
        # 这里先返回直线路径作为占位
        return [start, end]
    
    def _identify_conduit_sections(self, main_route: PipeRoute) -> List[Dict]:
        """
        识别主管穿过硬化区的部分，标记为过路管
        
        规格（Scott确认）:
        - de25/de32主管统一采用de63过路保护管
        - 控制线与主管共用一根过路保护管
        
        返回：
        [{
            'start_idx': int,      # 路径起点索引
            'end_idx': int,        # 路径终点索引  
            'length': float,       # 长度(米)
            'hard_zone_id': str,   # 所属硬化区ID
            'main_diameter': float, # 主管管径
            'conduit_diameter': float  # 过路保护管管径（统一de63）
        }, ...]
        """
        conduit_sections = []
        path = main_route.path
        
        for hard_zone in self.hard_zones:
            # 找出路径上位于硬化区内的连续段
            in_hard_sections = self._find_path_segments_in_zone(path, hard_zone)
            
            for start_idx, end_idx in in_hard_sections:
                length = self._calculate_path_length(path[start_idx:end_idx+1])
                
                # 过路管规格：统一de63（Scott确认）
                main_dia = main_route.diameter
                
                conduit_sections.append({
                    'start_idx': start_idx,
                    'end_idx': end_idx,
                    'length': round(length, 2),
                    'hard_zone_id': hard_zone.id,
                    'main_diameter': main_dia,
                    'conduit_diameter': 63.0,  # 统一de63
                    'shared_with_control': True  # 控制线共用
                })
        
        return conduit_sections
    
    def _find_path_segments_in_zone(self, path: List[Tuple[float, float]], zone: Zone) -> List[Tuple[int, int]]:
        """找出路径上位于zone内的连续段"""
        segments = []
        in_zone = False
        start_idx = 0
        
        for i, point in enumerate(path):
            p = Point(point)
            is_inside = zone.polygon.contains(p)
            
            if is_inside and not in_zone:
                # 进入zone
                in_zone = True
                start_idx = i
            elif not is_inside and in_zone:
                # 离开zone
                in_zone = False
                segments.append((start_idx, i - 1))
        
        # 如果路径终点在zone内
        if in_zone:
            segments.append((start_idx, len(path) - 1))
        
        return segments
    
    def _calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        """计算路径长度"""
        length = 0
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            length += math.sqrt((x2-x1)**2 + (y2-y1)**2)
        return length
    
    def _plan_valve_positions(self, design: IrrigationDesign, water_flow: float) -> List[Tuple[float, float]]:
        """
        规划阀门位置
        
        规则（Scott确认）:
        1. 阀门放在主管和支管连接处
        2. 靠绿化区域边缘布置
        3. 不同类型喷头不能共用阀门
        4. 一个阀门下带的喷头数量不能超过水源供水流量
        
        Args:
            water_flow: 水源供水流量 (m³/h)
        
        Returns:
            阀门位置列表
        """
        valve_positions = []
        main_route = design.main_pipes[0] if design.main_pipes else None
        
        # 按喷头类型分组（不同类型不能共用阀门）
        for zone in self.green_zones:
            if not zone.sprinkler_positions:
                continue
            
            # 根据喷头类型确定单喷头流量
            sprinkler_flow = self._get_sprinkler_flow(zone.plant_type)
            
            # 计算该区域的喷头数量
            num_sprinklers = len(zone.sprinkler_positions)
            total_flow = num_sprinklers * sprinkler_flow
            
            # 如果总流量超过水源流量，需要拆分多个阀门
            if total_flow > water_flow:
                # 计算每个阀门最多能带多少个喷头
                max_per_valve = int(water_flow / sprinkler_flow)
                
                # 将喷头分组，每组不超过流量限制
                groups = []
                for i in range(0, num_sprinklers, max_per_valve):
                    groups.append(zone.sprinkler_positions[i:i + max_per_valve])
                
                # 为每组喷头放置一个阀门
                for group in groups:
                    # 阀门位置：支管与主管连接处，靠近绿化区边缘
                    valve_pos = self._find_valve_position(zone, group, main_route)
                    valve_positions.append(valve_pos)
            else:
                # 总流量未超限，该区域一个阀门
                valve_pos = self._find_valve_position(zone, zone.sprinkler_positions, main_route)
                valve_positions.append(valve_pos)
        
        return valve_positions
    
    def _get_sprinkler_flow(self, plant_type: str) -> float:
        """
        获取单喷头流量 (m³/h)
        
        根据科雨喷头型号（从DXF图纸提取）:
        - KVF8:  0.54 m³/h (中值)
        - KVF10: 0.56 m³/h
        - KVF12: 0.66 m³/h
        - KVF15: 0.69 m³/h
        - KVF17: 0.71 m³/h
        - 微喷: 0.25 m³/h
        - 滴灌: 0.0023 m³/h (2.3L/H)
        """
        flow_map = {
            'lawn': 0.66,        # KVF12 中值
            'shrub': 0.56,       # KVF10 中值
            'flower': 0.25,      # 微喷
            'drip': 0.0023,      # 滴灌管 KA5-112P-CV
            'micro_stake': 0.25, # 地插微喷
        }
        return flow_map.get(plant_type, 0.56)
    
    def _find_valve_position(self, zone: Zone, sprinkler_group: List[Tuple[float, float]], 
                            main_route: PipeRoute) -> Tuple[float, float]:
        """
        找到阀门最佳位置
        
        原则（Scott确认）：
        1. 主管与支管连接处
        2. 靠近绿化区边缘（便于施工和检修）
        3. 不在绿化区内部（避免踩踏破坏）
        """
        # 计算这组喷头的中心点
        center_x = sum(p[0] for p in sprinkler_group) / len(sprinkler_group)
        center_y = sum(p[1] for p in sprinkler_group) / len(sprinkler_group)
        center = Point(center_x, center_y)
        
        # 找到zone边界上离中心最近的点
        boundary = zone.polygon.boundary
        nearest_on_boundary = nearest_points(center, boundary)[1]
        
        # 找到主管上离边界点最近的点
        best_point = main_route.path[0]
        min_dist = float('inf')
        
        for point in main_route.path:
            dist = Point(point).distance(Point(nearest_on_boundary.x, nearest_on_boundary.y))
            if dist < min_dist:
                min_dist = dist
                best_point = point
        
        # 阀门位置：在主管上，靠近绿化区边界
        return best_point
    
    def _plan_branch_pipes(self, zone: Zone, main_route: PipeRoute) -> List[PipeRoute]:
        """
        规划某个绿化区的支管
        
        从主管最近的点分岔，连接到各个喷头
        """
        branches = []
        
        if not zone.sprinkler_positions:
            return branches
        
        # 找到主管上离该区域最近的点作为分岔点
        branch_point = self._find_branch_point_on_main(zone, main_route)
        
        # 从分岔点连接到各个喷头
        for sprinkler_pos in zone.sprinkler_positions:
            path = self._connect_avoiding_obstacles(branch_point, sprinkler_pos)
            
            branches.append(PipeRoute(
                path=path,
                pipe_type='branch',
                diameter=25.0,  # 支管默认25mm
                conduit_sections=None,
                conduit_diameter=None
            ))
        
        return branches
    
    def _find_branch_point_on_main(self, zone: Zone, main_route: PipeRoute) -> Tuple[float, float]:
        """找到主管上离zone最近的点作为支管分岔点"""
        zone_center = zone.polygon.centroid
        
        min_dist = float('inf')
        best_point = main_route.path[0]
        
        for point in main_route.path:
            dist = Point(point).distance(zone_center)
            if dist < min_dist:
                min_dist = dist
                best_point = point
        
        return best_point
    
    def _connect_avoiding_obstacles(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """连接两点，避开禁区"""
        line = LineString([start, end])
        
        if self._line_intersects_forbidden(line):
            return self._calculate_detour(start, end)
        
        return [start, end]
    
    def _plan_control_lines(self, design: IrrigationDesign) -> List[PipeRoute]:
        """
        规划控制线（从水源到各阀门）
        
        控制线跟随主管走向，穿硬化区时共用de63过路保护管（Scott确认）
        """
        control_routes = []
        for valve_pos in design.valve_positions:
            # 从水源到阀门的控制线
            path = self._connect_avoiding_obstacles(self.water_source, valve_pos)
            
            control_routes.append(PipeRoute(
                path=path,
                pipe_type='control',
                diameter=0,  # 控制线不是管，是电缆
                conduit_sections=None,
                conduit_diameter=63.0  # 与主管共用de63过路保护管
            ))
        
        return control_routes


# ============ 材料统计 ============

def calculate_pipe_materials(design: IrrigationDesign) -> Dict:
    """
    计算管路材料清单
    
    返回：
    {
        'main_pipes': [
            {'diameter': 32, 'length': 45.5, 'type': 'PPR主管'}
        ],
        'branch_pipes': [
            {'diameter': 25, 'length': 120.3, 'type': 'PPR支管'}
        ],
        'conduits': [
            {'diameter': 63, 'length': 15.2, 'type': '过路保护管de63', 'locations': [...]}
        ],
        'control_lines': [
            {'spec': '2x1.5', 'length': 80.0, 'conduit_length': 15.2}
        ],
        'valves': [
            {'model': 'PROSERIES100-7001', 'count': 5}
        ]
    }
    """
    materials = {
        'main_pipes': [],
        'branch_pipes': [],
        'conduits': [],
        'control_lines': [],
        'valves': []
    }
    
    # 统计主管
    main_lengths = {}
    for pipe in design.main_pipes:
        dia = pipe.diameter
        length = sum(
            math.sqrt((pipe.path[i+1][0]-pipe.path[i][0])**2 + 
                     (pipe.path[i+1][1]-pipe.path[i][1])**2)
            for i in range(len(pipe.path)-1)
        )
        main_lengths[dia] = main_lengths.get(dia, 0) + length
    
    for dia, length in main_lengths.items():
        materials['main_pipes'].append({
            'diameter': dia,
            'length': round(length, 1),
            'type': f'PPR主管'
        })
    
    # 统计支管
    branch_lengths = {}
    for pipe in design.branch_pipes:
        dia = pipe.diameter
        length = sum(
            math.sqrt((pipe.path[i+1][0]-pipe.path[i][0])**2 + 
                     (pipe.path[i+1][1]-pipe.path[i][1])**2)
            for i in range(len(pipe.path)-1)
        )
        branch_lengths[dia] = branch_lengths.get(dia, 0) + length
    
    for dia, length in branch_lengths.items():
        materials['branch_pipes'].append({
            'diameter': dia,
            'length': round(length, 1),
            'type': f'PPR支管'
        })
    
    # 统计过路管（de63统一规格）
    materials['conduits'] = design.conduit_sections
    
    # 统计控制线
    control_length = sum(
        sum(
            math.sqrt((pipe.path[i+1][0]-pipe.path[i][0])**2 + 
                     (pipe.path[i+1][1]-pipe.path[i][1])**2)
            for i in range(len(pipe.path)-1)
        )
        for pipe in design.control_lines
    )
    
    # 控制线穿过硬化区的长度（与主管共用de63过路保护管）
    conduit_length = sum(c['length'] for c in design.conduit_sections)
    
    materials['control_lines'].append({
        'spec': 'RVV-2*1.5mm²',
        'length': round(control_length, 1),
        'conduit_length': round(conduit_length, 1),
        'type': '控制线',
        'conduit_diameter': 63.0  # 与主管共用de63
    })
    
    # 统计阀门
    if design.valve_positions:
        materials['valves'].append({
            'model': 'PROSERIES100-7001',
            'count': len(design.valve_positions),
            'type': '1寸电磁阀',
            'brand': 'Krain'
        })
    
    return materials


# ============ 测试用例 ============

def test_simple_case():
    """测试简单场景：1个水源，2个绿化区，1个房屋，1个硬化区"""
    from shapely.geometry import Polygon
    
    # 定义区域
    zones = [
        Zone(
            id='green1',
            polygon=Polygon([(10, 10), (30, 10), (30, 20), (10, 20)]),
            zone_type='green',
            plant_type='lawn',
            sprinkler_positions=[(15, 15), (25, 15)]
        ),
        Zone(
            id='green2',
            polygon=Polygon([(40, 10), (60, 10), (60, 25), (40, 25)]),
            zone_type='green',
            plant_type='shrub',
            sprinkler_positions=[(45, 15), (55, 15), (50, 20)]
        ),
        Zone(
            id='house',
            polygon=Polygon([(20, 30), (50, 30), (50, 50), (20, 50)]),
            zone_type='forbidden'
        ),
        Zone(
            id='road',
            polygon=Polygon([(0, 5), (70, 5), (70, 8), (0, 8)]),
            zone_type='hard',
            requires_conduit=True
        )
    ]
    
    water_source = (0, 0)
    
    # 规划管路（水源流量2.5m³/h）
    planner = PipeRoutePlanner(zones, water_source)
    design = planner.plan_route(water_flow=2.5)
    
    # 统计材料
    materials = calculate_pipe_materials(design)
    
    print("=" * 50)
    print("管路路径规划测试结果")
    print("=" * 50)
    print()
    print(f"主管数量: {len(design.main_pipes)}")
    print(f"支管数量: {len(design.branch_pipes)}")
    print(f"阀门数量: {len(design.valve_positions)}")
    print(f"过路管段: {len(design.conduit_sections)}")
    print()
    print("阀门位置:")
    for i, pos in enumerate(design.valve_positions):
        print(f"  阀门{i+1}: ({pos[0]:.1f}, {pos[1]:.1f})")
    print()
    print("材料清单:")
    for category, items in materials.items():
        if items:
            print(f"\n{category}:")
            for item in items:
                print(f"  {item}")
    print()
    print("=" * 50)


if __name__ == "__main__":
    try:
        test_simple_case()
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("需要安装: pip install shapely")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
