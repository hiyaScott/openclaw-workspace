"""
喷头布局算法 - 将灌溉计算器的逻辑转换为空间几何算法

核心思路：
1. 给定一个多边形区域（灌溉区），根据喷头类型和参数，计算最优喷头位置
2. 喷头位置用坐标表示，可在CAD中绘制为圆点
3. 同时生成管路路径（主管、支管）
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import math


class SprinklerType(str, Enum):
    """喷头类型 - 对应灌溉计算器中的配置"""
    DRIP = "drip"                    # K-rain花园专用滴灌管
    MICRO_STAKE = "micro_stake"      # 地插微喷头
    RECT_78012 = "rect78012"         # PRO-s-78012-矩形
    RECT_78004 = "rect78004"         # PRO-s-78004-矩形
    FAN_78012 = "fan78012"           # PRO-s-78012-扇形
    FAN_78004 = "fan78004"           # PRO-s-78004-扇形
    MINI_13012 = "mini13012"         # MiniPRO13012
    MINI_13003 = "mini13003"         # MiniPRO13003
    SUPER_10003 = "super10003"       # SuperPRO10003


class PlantType(str, Enum):
    SHRUB = "shrub"
    LAWN = "lawn"
    FLOWER = "flower"


@dataclass
class Point:
    """二维坐标点"""
    x: float
    y: float
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)
    
    def distance_to(self, other) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class SprinklerConfig:
    """喷头配置参数"""
    name: str
    price: float
    install_fee: float
    flow: float              # m³/h
    unit: str
    spray_radius: float      # 射程（米）
    spacing: float           # 推荐间距（米）
    coverage_pattern: str    # "rect"矩形, "fan"扇形, "circle"圆形, "drip"滴灌, "stake"地插


# 喷头参数配置表（从灌溉计算器提取）
SPRINKLER_CONFIGS = {
    SprinklerType.DRIP: SprinklerConfig(
        name="K-rain花园专用滴灌管",
        price=7, install_fee=2, flow=0.01, unit="米",
        spray_radius=0.3, spacing=0.3, coverage_pattern="drip"
    ),
    SprinklerType.MICRO_STAKE: SprinklerConfig(
        name="地插微喷头",
        price=3.5, install_fee=2, flow=0.2, unit="个",
        spray_radius=1.5, spacing=0.6, coverage_pattern="stake"
    ),
    SprinklerType.RECT_78012: SprinklerConfig(
        name="PRO-s-78012-矩形",
        price=90, install_fee=20, flow=0.2, unit="个",
        spray_radius=3.0, spacing=3.0, coverage_pattern="rect"
    ),
    SprinklerType.RECT_78004: SprinklerConfig(
        name="PRO-s-78004-矩形",
        price=30, install_fee=20, flow=0.2, unit="个",
        spray_radius=3.0, spacing=3.0, coverage_pattern="rect"
    ),
    SprinklerType.FAN_78012: SprinklerConfig(
        name="PRO-s-78012-扇形",
        price=90, install_fee=20, flow=0.5, unit="个",
        spray_radius=4.0, spacing=4.0, coverage_pattern="fan"
    ),
    SprinklerType.FAN_78004: SprinklerConfig(
        name="PRO-s-78004-扇形",
        price=30, install_fee=20, flow=0.5, unit="个",
        spray_radius=4.0, spacing=4.0, coverage_pattern="fan"
    ),
    SprinklerType.MINI_13012: SprinklerConfig(
        name="MiniPRO13012",
        price=260, install_fee=20, flow=0.4, unit="个",
        spray_radius=6.5, spacing=6.5, coverage_pattern="circle"
    ),
    SprinklerType.MINI_13003: SprinklerConfig(
        name="MiniPRO13003",
        price=120, install_fee=20, flow=0.4, unit="个",
        spray_radius=6.5, spacing=6.5, coverage_pattern="circle"
    ),
    SprinklerType.SUPER_10003: SprinklerConfig(
        name="SuperPRO10003",
        price=150, install_fee=30, flow=0.8, unit="个",
        spray_radius=10.0, spacing=10.0, coverage_pattern="circle"
    ),
}


@dataclass
class Polygon:
    """多边形区域 - 灌溉区边界"""
    points: List[Point]
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """返回 (min_x, min_y, max_x, max_y)"""
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
    
    def width(self) -> float:
        """区域宽度"""
        min_x, _, max_x, _ = self.bounding_box()
        return max_x - min_x
    
    def height(self) -> float:
        """区域高度"""
        _, min_y, _, max_y = self.bounding_box()
        return max_y - min_y
    
    def area(self) -> float:
        """多边形面积（鞋带公式）"""
        n = len(self.points)
        if n < 3:
            return 0.0
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self.points[i].x * self.points[j].y
            area -= self.points[j].x * self.points[i].y
        return abs(area) / 2.0
    
    def center(self) -> Point:
        """几何中心"""
        min_x, min_y, max_x, max_y = self.bounding_box()
        return Point((min_x + max_x) / 2, (min_y + max_y) / 2)
    
    def to_tuples(self) -> List[Tuple[float, float]]:
        return [p.to_tuple() for p in self.points]


@dataclass
class Sprinkler:
    """单个喷头实例"""
    position: Point
    type: SprinklerType
    rotation: float = 0.0      # 朝向角度（度）
    valve_group: int = 0       # 所属阀门组
    
    def config(self) -> SprinklerConfig:
        return SPRINKLER_CONFIGS[self.type]


@dataclass
class PipeSegment:
    """管路线段"""
    start: Point
    end: Point
    pipe_type: str             # "main"主管, "branch"支管, "lateral"毛管
    diameter: float            # 管径 mm
    
    def length(self) -> float:
        return self.start.distance_to(self.end)


@dataclass
class IrrigationZone:
    """灌溉区完整设计结果"""
    zone_id: int
    boundary: Polygon
    plant_type: PlantType
    sprinklers: List[Sprinkler]
    pipes: List[PipeSegment]
    valve_count: int
    total_flow: float          # m³/h
    
    def sprinkler_count(self) -> int:
        return len(self.sprinklers)


# =============================================================================
# 核心算法
# =============================================================================

def select_sprinkler_type(width: float, plant_type: PlantType, 
                          narrow_preference: str = "drip") -> Optional[SprinklerType]:
    """
    根据区域宽度和植物类型选择喷头类型
    
    完全复用灌溉计算器逻辑：
    - width < 1m: 滴灌管/地插微喷头
    - 1-1.5m: 矩形喷头
    - 1.5-5m: 扇形喷头
    - 5-9m: MiniPRO
    - 9-30m草坪: SuperPRO
    """
    if width < 1.0:
        if plant_type in (PlantType.SHRUB, PlantType.FLOWER):
            return SprinklerType.MICRO_STAKE if narrow_preference == "micro_stake" else SprinklerType.DRIP
    
    if 1.0 <= width <= 1.5:
        if plant_type in (PlantType.SHRUB, PlantType.FLOWER):
            return SprinklerType.RECT_78012
        if plant_type == PlantType.LAWN:
            return SprinklerType.RECT_78004
    
    if 1.5 < width <= 5.0:
        if plant_type in (PlantType.SHRUB, PlantType.FLOWER):
            return SprinklerType.FAN_78012
        if plant_type == PlantType.LAWN:
            return SprinklerType.FAN_78004
    
    if 5.0 <= width < 9.0:
        if plant_type in (PlantType.SHRUB, PlantType.FLOWER):
            return SprinklerType.MINI_13012
        if plant_type == PlantType.LAWN:
            return SprinklerType.MINI_13003
    
    if 9.0 <= width <= 30.0 and plant_type == PlantType.LAWN:
        return SprinklerType.SUPER_10003
    
    return None


def calculate_sprinkler_positions(
    polygon: Polygon,
    sprinkler_type: SprinklerType,
    location: str = "edge",
    overlap_ratio: float = 0.3
) -> List[Point]:
    """
    计算喷头在区域内的最优位置
    
    算法：
    1. 获取区域边界框
    2. 根据喷头类型和间距，计算网格/行布局
    3. 对边界框内每个候选点，检查是否在多边形内
    4. 返回所有在多边形内的喷头位置
    
    Args:
        polygon: 灌溉区多边形
        sprinkler_type: 喷头类型
        location: "edge"边上(1排), "center"中间(2排)
        overlap_ratio: 重叠率（默认30%）
    
    Returns:
        喷头位置列表（Point列表）
    """
    config = SPRINKLER_CONFIGS[sprinkler_type]
    bbox = polygon.bounding_box()
    min_x, min_y, max_x, max_y = bbox
    
    positions = []
    
    # --- 滴灌管：行距0.3m，沿长边铺设 ---
    if sprinkler_type == SprinklerType.DRIP:
        row_spacing = 0.3  # 行距
        # 沿Y方向（假设宽度方向）铺设行
        rows = int((max_y - min_y) / row_spacing) + 1
        for row in range(rows):
            y = min_y + row * row_spacing + row_spacing / 2
            if y > max_y:
                continue
            # 沿X方向（长边）取多个采样点，检查是否在多边形内
            step = 0.5
            x = min_x + step / 2
            while x < max_x:
                pt = Point(x, y)
                if _point_in_polygon(pt, polygon):
                    positions.append(pt)
                x += step
        return positions
    
    # --- 地插微喷头：间距0.6m ---
    if sprinkler_type == SprinklerType.MICRO_STAKE:
        spacing = 0.6
        # 沿区域长方向（假设X）均匀分布
        # 简化：沿中线均匀分布
        center_y = (min_y + max_y) / 2
        count = int((max_x - min_x) / spacing) + 1
        for i in range(count):
            x = min_x + spacing / 2 + i * spacing
            if x > max_x:
                continue
            pt = Point(x, center_y)
            if _point_in_polygon(pt, polygon):
                positions.append(pt)
        return positions
    
    # --- 矩形喷头：间距3m，单行 ---
    if sprinkler_type in (SprinklerType.RECT_78012, SprinklerType.RECT_78004):
        spacing = 3.0
        # 沿区域长方向（假设X）均匀分布，居中一行
        center_y = (min_y + max_y) / 2
        count = int((max_x - min_x) / spacing) + 1
        for i in range(count):
            x = min_x + spacing / 2 + i * spacing
            if x > max_x:
                continue
            pt = Point(x, center_y)
            if _point_in_polygon(pt, polygon):
                positions.append(pt)
        return positions
    
    # --- 扇形喷头 ---
    if sprinkler_type in (SprinklerType.FAN_78012, SprinklerType.FAN_78004):
        spacing = config.spray_radius * (1 - overlap_ratio)  # 考虑重叠
        
        rows = 1
        if polygon.height() > 3.0:
            rows = 2 if location == "center" else 1
        if polygon.height() >= 6.0 and polygon.height() <= 9.0:
            rows = 2
        
        for row in range(rows):
            if rows == 1:
                y = (min_y + max_y) / 2
            else:
                margin = spacing * 0.5
                y = min_y + margin + row * (max_y - min_y - 2 * margin) / max(1, rows - 1)
            
            count = int((max_x - min_x) / spacing) + 1
            for i in range(count):
                x = min_x + spacing / 2 + i * spacing
                if x > max_x:
                    continue
                pt = Point(x, y)
                if _point_in_polygon(pt, polygon):
                    positions.append(pt)
        return positions
    
    # --- MiniPRO / SuperPRO：圆形覆盖，网格布局 ---
    if sprinkler_type in (SprinklerType.MINI_13012, SprinklerType.MINI_13003, 
                           SprinklerType.SUPER_10003):
        spacing = config.spray_radius * (1 - overlap_ratio)
        
        # 六边形密铺（偏移网格）
        y_step = spacing * math.sqrt(3) / 2  # 垂直间距
        
        row = 0
        y = min_y + spacing / 2
        while y < max_y:
            x_offset = (spacing / 2) if (row % 2 == 1) else 0
            x = min_x + spacing / 2 + x_offset
            while x < max_x:
                pt = Point(x, y)
                if _point_in_polygon(pt, polygon):
                    positions.append(pt)
                x += spacing
            y += y_step
            row += 1
        
        return positions
    
    return positions


def generate_pipe_network(
    sprinklers: List[Sprinkler],
    source_point: Point,
    polygon: Polygon,
    pipe_size: int = 25
) -> List[PipeSegment]:
    """
    生成管路网络
    
    策略：
    1. 主管从水源点沿区域边界铺设到最近点
    2. 支管连接同排/同组的喷头
    3. 毛管连接支管到单个喷头
    
    简化版本V1：
    - 主管：水源 → 区域中心
    - 支管：沿喷头排布方向的主干线
    - 毛管：支管 → 各喷头
    """
    pipes = []
    
    if not sprinklers:
        return pipes
    
    # 找到离水源最近的喷头
    nearest = min(sprinklers, key=lambda s: s.position.distance_to(source_point))
    
    # 主管：水源 → 最近喷头
    pipes.append(PipeSegment(
        start=source_point,
        end=nearest.position,
        pipe_type="main",
        diameter=pipe_size
    ))
    
    # 按Y坐标分组（排）
    # 简化：将喷头按Y坐标聚类为排
    rows = _cluster_by_y(sprinklers)
    
    for row_sprinklers in rows:
        if len(row_sprinklers) <= 1:
            continue
        
        # 按X排序
        row_sprinklers.sort(key=lambda s: s.position.x)
        
        # 支管：连接同一排的喷头
        for i in range(len(row_sprinklers) - 1):
            pipes.append(PipeSegment(
                start=row_sprinklers[i].position,
                end=row_sprinklers[i + 1].position,
                pipe_type="branch",
                diameter=25
            ))
    
    # 主管连接到每一排的第一个喷头（如果还没连）
    for row_sprinklers in rows:
        if not row_sprinklers:
            continue
        first = row_sprinklers[0]
        # 检查是否已连接到主管网
        connected = any(p.end == first.position for p in pipes)
        if not connected and first != nearest:
            # 找这一排离主管网最近的点
            pipes.append(PipeSegment(
                start=nearest.position,
                end=first.position,
                pipe_type="branch",
                diameter=25
            ))
    
    return pipes


def _cluster_by_y(sprinklers: List[Sprinkler], tolerance: float = 1.0) -> List[List[Sprinkler]]:
    """按Y坐标将喷头分组为排"""
    if not sprinklers:
        return []
    
    sorted_sprinklers = sorted(sprinklers, key=lambda s: s.position.y)
    
    rows = []
    current_row = [sorted_sprinklers[0]]
    
    for s in sorted_sprinklers[1:]:
        if abs(s.position.y - current_row[0].position.y) <= tolerance:
            current_row.append(s)
        else:
            rows.append(current_row)
            current_row = [s]
    
    if current_row:
        rows.append(current_row)
    
    return rows


def _point_in_polygon(point: Point, polygon: Polygon) -> bool:
    """
    射线法判断点是否在多边形内
    """
    n = len(polygon.points)
    if n < 3:
        return False
    
    inside = False
    j = n - 1
    
    for i in range(n):
        xi, yi = polygon.points[i].x, polygon.points[i].y
        xj, yj = polygon.points[j].x, polygon.points[j].y
        
        # 检查边是否与水平射线相交
        if ((yi > point.y) != (yj > point.y)) and \
           (point.x < (xj - xi) * (point.y - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
        
        j = i
    
    return inside


def design_irrigation_zone(
    zone_id: int,
    boundary: Polygon,
    plant_type: PlantType,
    water_source_flow: float = 2.5,
    pipe_size: int = 25,
    narrow_preference: str = "drip",
    location: str = "edge",
    source_point: Optional[Point] = None
) -> IrrigationZone:
    """
    为单个区域设计完整的灌溉方案
    
    这是核心入口函数，将灌溉计算器的逻辑与几何计算结合
    
    Args:
        zone_id: 区域编号
        boundary: 区域边界多边形（用户在CAD上画的多边形）
        plant_type: 植物类型
        water_source_flow: 水源流量 m³/h
        pipe_size: 主管管径 mm
        narrow_preference: 窄带偏好 "drip"或"micro_stake"
        location: "edge"边上, "center"中间
        source_point: 水源位置（默认为区域几何中心）
    
    Returns:
        完整的 IrrigationZone 设计方案
    """
    # 1. 计算区域特征尺寸
    width = boundary.width()
    
    # 2. 选择喷头类型
    sprinkler_type = select_sprinkler_type(width, plant_type, narrow_preference)
    
    if sprinkler_type is None:
        return IrrigationZone(
            zone_id=zone_id,
            boundary=boundary,
            plant_type=plant_type,
            sprinklers=[],
            pipes=[],
            valve_count=0,
            total_flow=0.0
        )
    
    # 3. 计算喷头位置
    positions = calculate_sprinkler_positions(
        boundary, sprinkler_type, location, overlap_ratio=0.3
    )
    
    # 4. 创建喷头实例
    sprinklers = [
        Sprinkler(position=pos, type=sprinkler_type, rotation=0.0)
        for pos in positions
    ]
    
    # 5. 计算总流量和阀门数
    config = SPRINKLER_CONFIGS[sprinkler_type]
    total_flow = len(sprinklers) * config.flow
    valve_count = max(1, math.ceil(total_flow / water_source_flow))
    
    # 6. 分配阀门组
    # 简化：将喷头均匀分配到各阀门组
    for i, sprinkler in enumerate(sprinklers):
        sprinkler.valve_group = (i % valve_count) + 1
    
    # 7. 生成管路
    if source_point is None:
        source_point = polygon.center()
    
    pipes = generate_pipe_network(sprinklers, source_point, boundary, pipe_size)
    
    return IrrigationZone(
        zone_id=zone_id,
        boundary=boundary,
        plant_type=plant_type,
        sprinklers=sprinklers,
        pipes=pipes,
        valve_count=valve_count,
        total_flow=total_flow
    )


def calculate_valve_groups(zones: List[IrrigationZone], water_source_flow: float) -> Dict:
    """
    跨区域的阀门分组优化
    
    将流量分配到不同阀门组，确保每组不超过水源流量
    """
    # 简化：每个区域独立分组，后续可优化为跨区域的轮灌优化
    all_groups = []
    
    for zone in zones:
        for v in range(1, zone.valve_count + 1):
            zone_sprinklers = [s for s in zone.sprinklers if s.valve_group == v]
            flow = sum(SPRINKLER_CONFIGS[s.type].flow for s in zone_sprinklers)
            all_groups.append({
                "zone_id": zone.zone_id,
                "valve_id": v,
                "sprinkler_count": len(zone_sprinklers),
                "flow": flow,
                "sprinklers": zone_sprinklers
            })
    
    return {
        "groups": all_groups,
        "total_valves": len(all_groups),
        "total_flow": sum(g["flow"] for g in all_groups),
        "max_group_flow": max(g["flow"] for g in all_groups) if all_groups else 0
    }


# =============================================================================
# 工具函数
# =============================================================================

def estimate_materials(zones: List[IrrigationZone], garden_perimeter: float = 0) -> Dict:
    """
    估算材料清单 - 复用灌溉计算器的报价逻辑
    
    返回与灌溉计算器兼容的材料清单格式
    """
    results = []
    total_cost = 0
    
    for zone in zones:
        zone_materials = {
            "zone_id": zone.zone_id,
            "sprinklers": [],
            "valves": zone.valve_count,
            "pipes": [],
            "total_flow": zone.total_flow,
        }
        
        # 喷头统计
        sprinkler_types = {}
        for s in zone.sprinklers:
            st = s.type
            if st not in sprinkler_types:
                sprinkler_types[st] = 0
            sprinkler_types[st] += 1
        
        for st, count in sprinkler_types.items():
            cfg = SPRINKLER_CONFIGS[st]
            zone_materials["sprinklers"].append({
                "type": st,
                "name": cfg.name,
                "count": count,
                "unit_price": cfg.price,
                "install_fee": cfg.install_fee,
                "total": count * (cfg.price + cfg.install_fee)
            })
        
        # 管路统计
        total_pipe_length = sum(p.length() for p in zone.pipes)
        zone_materials["pipes"].append({
            "length": total_pipe_length,
            "type": "综合",
            "note": "含主管、支管、毛管"
        })
        
        results.append(zone_materials)
    
    return {
        "zones": results,
        "zone_count": len(zones),
        "total_sprinklers": sum(len(z.sprinklers) for z in zones),
        "total_valves": sum(z.valve_count for z in zones),
        "total_flow": sum(z.total_flow for z in zones),
    }
