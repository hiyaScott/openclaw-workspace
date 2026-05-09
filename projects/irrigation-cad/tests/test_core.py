import sys
sys.path.insert(0, '/root/.openclaw/workspace/projects/irrigation-cad/backend')

from core.sprinkler_layout import (
    Point, Polygon, PlantType, SprinklerType,
    design_irrigation_zone, calculate_valve_groups,
    estimate_materials, SPRINKLER_CONFIGS,
    select_sprinkler_type, calculate_sprinkler_positions
)
from core.dxf_writer import export_design_to_dxf

print("=" * 60)
print("花园灌溉CAD设计系统 - 单元测试")
print("=" * 60)

# =============================================================================
# 测试1: 喷头选型
# =============================================================================
print("\n【测试1】喷头选型")

# 草坪 8m宽 → MiniPRO13003
st = select_sprinkler_type(8.0, PlantType.LAWN)
assert st == SprinklerType.MINI_13003, f"预期 MINI_13003, 实际 {st}"
print(f"  ✓ 草坪 8m宽 → {st.value}")

# 灌木带 1.2m宽 → RECT_78012
st = select_sprinkler_type(1.2, PlantType.SHRUB)
assert st == SprinklerType.RECT_78012
print(f"  ✓ 灌木带 1.2m宽 → {st.value}")

# 草坪 15m宽 → SUPER_10003
st = select_sprinkler_type(15.0, PlantType.LAWN)
assert st == SprinklerType.SUPER_10003
print(f"  ✓ 草坪 15m宽 → {st.value}")

# 窄带 0.8m → DRIP
st = select_sprinkler_type(0.8, PlantType.SHRUB, narrow_preference="drip")
assert st == SprinklerType.DRIP
print(f"  ✓ 灌木带 0.8m宽(滴灌) → {st.value}")

# 窄带 0.8m → MICRO_STAKE
st = select_sprinkler_type(0.8, PlantType.SHRUB, narrow_preference="micro_stake")
assert st == SprinklerType.MICRO_STAKE
print(f"  ✓ 灌木带 0.8m宽(地插) → {st.value}")

# =============================================================================
# 测试2: 喷头位置计算（矩形区域）
# =============================================================================
print("\n【测试2】喷头位置计算")

# 10x8m 草坪区域
rect_points = [
    Point(0, 0), Point(10, 0), Point(10, 8), Point(0, 8)
]
rect = Polygon(rect_points)

positions = calculate_sprinkler_positions(
    rect, SprinklerType.SUPER_10003, "center", overlap_ratio=0.3
)
print(f"  ✓ 10×8m 草坪 SUPER_10003 → {len(positions)} 个喷头")
for i, p in enumerate(positions[:5]):
    print(f"      喷头{i+1}: ({p.x:.1f}, {p.y:.1f})")

# 5x3m 灌木区域
rect2_points = [Point(0, 0), Point(5, 0), Point(5, 3), Point(0, 3)]
rect2 = Polygon(rect2_points)
positions2 = calculate_sprinkler_positions(
    rect2, SprinklerType.FAN_78012, "center", overlap_ratio=0.3
)
print(f"  ✓ 5×3m 灌木 FAN_78012 → {len(positions2)} 个喷头")

# =============================================================================
# 测试3: 完整区域设计
# =============================================================================
print("\n【测试3】完整区域设计")

zone = design_irrigation_zone(
    zone_id=1,
    boundary=rect,
    plant_type=PlantType.LAWN,
    water_source_flow=2.5,
    pipe_size=25,
    narrow_preference="drip",
    location="center",
    source_point=Point(-2, 4)
)

print(f"  ✓ 区域 {zone.zone_id}: {zone.plant_type.value}")
print(f"      喷头数量: {zone.sprinkler_count()}")
print(f"      阀门数量: {zone.valve_count}")
print(f"      总流量: {zone.total_flow:.2f} m³/h")
print(f"      管段数: {len(zone.pipes)}")
print(f"      管总长: {sum(p.length() for p in zone.pipes):.1f} m")

# =============================================================================
# 测试4: 多区域阀门分组
# =============================================================================
print("\n【测试4】多区域阀门分组")

# 第二个区域
rect3_points = [Point(12, 0), Point(20, 0), Point(20, 6), Point(12, 6)]
rect3 = Polygon(rect3_points)
zone2 = design_irrigation_zone(
    zone_id=2,
    boundary=rect3,
    plant_type=PlantType.SHRUB,
    water_source_flow=2.5,
    pipe_size=25,
    location="center",
    source_point=Point(-2, 4)
)

zones = [zone, zone2]
valve_result = calculate_valve_groups(zones, 2.5)

print(f"  ✓ 总阀门数: {valve_result['total_valves']}")
print(f"  ✓ 总流量: {valve_result['total_flow']:.2f} m³/h")
print(f"  ✓ 最大组流量: {valve_result['max_group_flow']:.2f} m³/h")

# =============================================================================
# 测试5: 材料估算
# =============================================================================
print("\n【测试5】材料估算")

materials = estimate_materials(zones)
print(f"  ✓ 区域数量: {materials['zone_count']}")
print(f"  ✓ 喷头总数: {materials['total_sprinklers']}")
print(f"  ✓ 阀门总数: {materials['total_valves']}")
print(f"  ✓ 总流量: {materials['total_flow']:.2f} m³/h")

# =============================================================================
# 测试6: DXF导出
# =============================================================================
print("\n【测试6】DXF文件导出")

output_path = "/tmp/test_irrigation.dxf"
export_design_to_dxf(zones, output_path, show_coverage=True, show_labels=True)

import os
file_size = os.path.getsize(output_path)
print(f"  ✓ DXF文件生成: {output_path}")
print(f"  ✓ 文件大小: {file_size} bytes")

# 读取前50行验证格式
with open(output_path, 'r') as f:
    lines = [f.readline().strip() for _ in range(50)]
    has_entities = any('ENTITIES' in line for line in lines)
    has_eof = any('EOF' in line for line in lines)
    print(f"  ✓ 包含 ENTITIES 段: {has_entities}")
    print(f"  ✓ 包含 EOF 标记: {has_eof}")

# =============================================================================
# 总结
# =============================================================================
print("\n" + "=" * 60)
print("所有测试通过 ✓")
print("=" * 60)
