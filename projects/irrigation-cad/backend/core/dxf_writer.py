"""
DXF 文件生成器 - 纯文本实现，不依赖 ezdxf

DXF是AutoCAD的开放交换格式，本质上是结构化的文本文件。
本模块直接生成ASCII格式的DXF内容，兼容性最好。
"""

from typing import List, Tuple
from dataclasses import dataclass


class DXFWriter:
    """DXF文件写入器"""
    
    def __init__(self):
        self.entities = []
        self.layers = {
            "0": {"color": 7, "linetype": "Continuous"},
            "BOUNDARY": {"color": 5, "linetype": "Continuous"},    # 蓝色 - 区域边界
            "SPRINKLERS": {"color": 1, "linetype": "Continuous"},  # 红色 - 喷头
            "MAIN_PIPE": {"color": 3, "linetype": "Continuous"},  # 绿色 - 主管
            "BRANCH_PIPE": {"color": 2, "linetype": "Continuous"}, # 黄色 - 支管
            "VALVES": {"color": 4, "linetype": "Continuous"},    # 青色 - 阀门
            "TEXT": {"color": 7, "linetype": "Continuous"},        # 白色 - 标注
        }
    
    def add_layer(self, name: str, color: int = 7, linetype: str = "Continuous"):
        """添加图层"""
        self.layers[name] = {"color": color, "linetype": linetype}
    
    def add_line(self, x1: float, y1: float, x2: float, y2: float, 
                 layer: str = "0", color: int = None):
        """添加线段（LINE实体）"""
        self.entities.append({
            "type": "LINE",
            "layer": layer,
            "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            "color": color
        })
    
    def add_circle(self, x: float, y: float, radius: float,
                   layer: str = "0", color: int = None):
        """添加圆（CIRCLE实体）- 用于表示喷头"""
        self.entities.append({
            "type": "CIRCLE",
            "layer": layer,
            "x": x, "y": y, "radius": radius,
            "color": color
        })
    
    def add_lwpolyline(self, points: List[Tuple[float, float]], 
                       closed: bool = True, layer: str = "0", color: int = None):
        """添加轻量多段线（LWPOLYLINE）- 用于区域边界"""
        self.entities.append({
            "type": "LWPOLYLINE",
            "layer": layer,
            "points": points,
            "closed": closed,
            "color": color
        })
    
    def add_text(self, x: float, y: float, text: str, height: float = 0.5,
                 layer: str = "TEXT", color: int = None, rotation: float = 0):
        """添加文字标注"""
        self.entities.append({
            "type": "TEXT",
            "layer": layer,
            "x": x, "y": y,
            "text": text,
            "height": height,
            "color": color,
            "rotation": rotation
        })
    
    def add_spray_radius(self, x: float, y: float, radius: float,
                         layer: str = "SPRINKLERS", color: int = 6):
        """添加喷头射程覆盖圈（虚线圆）"""
        self.entities.append({
            "type": "CIRCLE",
            "layer": layer,
            "x": x, "y": y, "radius": radius,
            "color": color,
            "linetype": "DASHED"
        })
    
    def generate(self) -> str:
        """
        生成完整的DXF文件内容（ASCII格式）
        
        DXF文件结构：
        HEADER → CLASSES → TABLES → BLOCKS → ENTITIES → OBJECTS
        """
        lines = []
        
        # === HEADER Section ===
        lines.extend(self._header_section())
        
        # === TABLES Section ===
        lines.extend(self._tables_section())
        
        # === ENTITIES Section ===
        lines.extend(self._entities_section())
        
        # === EOF ===
        lines.append("0")
        lines.append("EOF")
        
        return "\n".join(lines)
    
    def _header_section(self) -> List[str]:
        """HEADER段 - 文件元数据"""
        return [
            "0", "SECTION",
            "2", "HEADER",
            "9", "$ACADVER",
            "1", "AC1015",  # AutoCAD 2000格式
            "9", "$INSUNITS",
            "70", "6",     # 插入单位：米
            "0", "ENDSEC"
        ]
    
    def _tables_section(self) -> List[str]:
        """TABLES段 - 图层、线型等定义"""
        lines = [
            "0", "SECTION",
            "2", "TABLES",
        ]
        
        # LAYER Table
        lines.extend([
            "0", "TABLE",
            "2", "LAYER",
            "5", "5",
            "100", "AcDbSymbolTable",
            "70", str(len(self.layers)),
        ])
        
        for name, props in self.layers.items():
            lines.extend([
                "0", "LAYER",
                "5", "10",
                "100", "AcDbSymbolTableRecord",
                "100", "AcDbLayerTableRecord",
                "2", name,
                "70", "0",
                "62", str(props["color"]),
                "6", props["linetype"],
            ])
        
        lines.extend([
            "0", "ENDTAB",
            "0", "ENDSEC"
        ])
        
        return lines
    
    def _entities_section(self) -> List[str]:
        """ENTITIES段 - 所有图形实体"""
        lines = [
            "0", "SECTION",
            "2", "ENTITIES",
        ]
        
        for entity in self.entities:
            e_type = entity["type"]
            
            if e_type == "LINE":
                lines.extend(self._format_line(entity))
            elif e_type == "CIRCLE":
                lines.extend(self._format_circle(entity))
            elif e_type == "LWPOLYLINE":
                lines.extend(self._format_lwpolyline(entity))
            elif e_type == "TEXT":
                lines.extend(self._format_text(entity))
        
        lines.extend([
            "0", "ENDSEC"
        ])
        
        return lines
    
    def _format_line(self, e: dict) -> List[str]:
        """格式化LINE实体"""
        color = e.get("color", "")
        color_str = str(color) if color is not None else "256"
        return [
            "0", "LINE",
            "8", e.get("layer", "0"),
            "62", color_str,
            "10", str(e["x1"]),
            "20", str(e["y1"]),
            "11", str(e["x2"]),
            "21", str(e["y2"]),
        ]
    
    def _format_circle(self, e: dict) -> List[str]:
        """格式化CIRCLE实体"""
        color = e.get("color", "")
        color_str = str(color) if color is not None else "256"
        return [
            "0", "CIRCLE",
            "8", e.get("layer", "0"),
            "62", color_str,
            "10", str(e["x"]),
            "20", str(e["y"]),
            "40", str(e["radius"]),
        ]
    
    def _format_lwpolyline(self, e: dict) -> List[str]:
        """格式化LWPOLYLINE实体"""
        color = e.get("color", "")
        color_str = str(color) if color is not None else "256"
        points = e["points"]
        
        lines = [
            "0", "LWPOLYLINE",
            "8", e.get("layer", "0"),
            "62", color_str,
            "100", "AcDbEntity",
            "100", "AcDbPolyline",
            "90", str(len(points)),
            "70", "1" if e.get("closed", True) else "0",
        ]
        
        for pt in points:
            lines.extend([
                "10", str(pt[0]),
                "20", str(pt[1]),
            ])
        
        return lines
    
    def _format_text(self, e: dict) -> List[str]:
        """格式化TEXT实体"""
        color = e.get("color", "")
        color_str = str(color) if color is not None else "256"
        return [
            "0", "TEXT",
            "8", e.get("layer", "TEXT"),
            "62", color_str,
            "10", str(e["x"]),
            "20", str(e["y"]),
            "40", str(e.get("height", 0.5)),
            "1", e.get("text", ""),
            "50", str(e.get("rotation", 0)),
        ]
    
    def write_to_file(self, filepath: str):
        """写入DXF文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate())


# =============================================================================
# 灌溉设计专用导出器
# =============================================================================

def export_design_to_dxf(
    zones: List,
    output_path: str,
    show_coverage: bool = True,
    show_labels: bool = True
) -> str:
    """
    将灌溉设计方案导出为DXF文件
    
    Args:
        zones: IrrigationZone列表
        output_path: 输出文件路径
        show_coverage: 是否显示喷头覆盖范围（虚线圆）
        show_labels: 是否显示标注文字
    
    Returns:
        输出文件路径
    """
    from .sprinkler_layout import SPRINKLER_CONFIGS
    
    dxf = DXFWriter()
    
    for zone in zones:
        # 1. 绘制区域边界
        boundary_points = zone.boundary.to_tuples()
        dxf.add_lwpolyline(
            points=boundary_points,
            closed=True,
            layer="BOUNDARY",
            color=5  # 蓝色
        )
        
        # 2. 绘制喷头
        for i, sprinkler in enumerate(zone.sprinklers):
            pos = sprinkler.position
            
            # 喷头本体（实心圆点）
            dxf.add_circle(
                x=pos.x, y=pos.y, radius=0.15,
                layer="SPRINKLERS", color=1  # 红色
            )
            
            # 覆盖范围（虚线圆）
            if show_coverage:
                config = SPRINKLER_CONFIGS.get(sprinkler.type)
                if config:
                    dxf.add_spray_radius(
                        x=pos.x, y=pos.y, radius=config.spray_radius,
                        layer="SPRINKLERS", color=6  # 品红色虚线
                    )
            
            # 标注阀门组
            if show_labels:
                dxf.add_text(
                    x=pos.x + 0.2, y=pos.y + 0.2,
                    text=f"V{sprinkler.valve_group}",
                    height=0.25, layer="TEXT", color=7
                )
        
        # 3. 绘制管路
        for pipe in zone.pipes:
            layer = "MAIN_PIPE" if pipe.pipe_type == "main" else "BRANCH_PIPE"
            color = 3 if pipe.pipe_type == "main" else 2
            
            dxf.add_line(
                x1=pipe.start.x, y1=pipe.start.y,
                x2=pipe.end.x, y2=pipe.end.y,
                layer=layer, color=color
            )
        
        # 4. 区域标注
        center = zone.boundary.center()
        if show_labels:
            dxf.add_text(
                x=center.x, y=center.y + 0.5,
                text=f"区域{zone.zone_id} {zone.plant_type.value} ({zone.sprinkler_count()}喷头)",
                height=0.4, layer="TEXT", color=7
            )
    
    # 写入文件
    dxf.write_to_file(output_path)
    return output_path


def export_to_pdf(
    zones: List,
    output_path: str,
    show_coverage: bool = True,
    show_labels: bool = True
) -> str:
    """
    使用 matplotlib 生成 PDF 输出
    
    注意：此函数需要 matplotlib 已安装
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MplPolygon, Circle
        from matplotlib.collections import PatchCollection
        from .sprinkler_layout import SPRINKLER_CONFIGS
    except ImportError:
        raise ImportError("matplotlib未安装，请先安装: pip install matplotlib")
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    for zone in zones:
        # 绘制边界
        boundary = zone.boundary.to_tuples()
        poly = MplPolygon(boundary, closed=True, fill=False,
                          edgecolor='blue', linewidth=2, alpha=0.8)
        ax.add_patch(poly)
        
        # 绘制喷头
        for sprinkler in zone.sprinklers:
            pos = sprinkler.position
            
            # 喷头标记
            circle = Circle((pos.x, pos.y), 0.15, fill=True,
                           color='red', alpha=0.9)
            ax.add_patch(circle)
            
            # 覆盖范围
            if show_coverage:
                config = SPRINKLER_CONFIGS.get(sprinkler.type)
                if config:
                    range_circle = Circle((pos.x, pos.y), config.spray_radius,
                                         fill=False, edgecolor='magenta',
                                         linestyle='--', linewidth=0.8, alpha=0.5)
                    ax.add_patch(range_circle)
            
            # 标注
            if show_labels:
                ax.text(pos.x + 0.2, pos.y + 0.2, f"V{sprinkler.valve_group}",
                       fontsize=6, color='gray')
        
        # 绘制管路
        for pipe in zone.pipes:
            color = 'green' if pipe.pipe_type == "main" else 'orange'
            linewidth = 2.5 if pipe.pipe_type == "main" else 1.5
            ax.plot([pipe.start.x, pipe.end.x], [pipe.start.y, pipe.end.y],
                   color=color, linewidth=linewidth, alpha=0.7)
        
        # 区域标注
        center = zone.boundary.center()
        if show_labels:
            ax.text(center.x, center.y + 0.5,
                   f"区域{zone.zone_id} ({zone.sprinkler_count()}喷头)",
                   fontsize=9, ha='center', fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_aspect('equal')
    ax.set_xlabel('X (米)', fontsize=10)
    ax.set_ylabel('Y (米)', fontsize=10)
    ax.set_title('花园灌溉设计图', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
               markersize=8, label='喷头'),
        Line2D([0], [0], color='green', linewidth=2.5, label='主管'),
        Line2D([0], [0], color='orange', linewidth=1.5, label='支管'),
        Line2D([0], [0], color='blue', linewidth=2, label='区域边界'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path, format='pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path
