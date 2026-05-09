"""
DXF图纸解析器

功能：
1. 解析DXF文件，提取几何实体
2. 识别图层（绿化区、建筑、道路等）
3. 提取块引用（喷头、阀门、设备等）
4. 返回结构化JSON数据供前端渲染
"""

import math
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


@dataclass
class PointData:
    x: float
    y: float
    
    def to_dict(self):
        return {'x': self.x, 'y': self.y}


@dataclass
class LineData:
    start: PointData
    end: PointData
    layer: str
    color: Optional[int] = None
    
    def to_dict(self):
        return {
            'type': 'LINE',
            'start': self.start.to_dict(),
            'end': self.end.to_dict(),
            'layer': self.layer,
            'color': self.color
        }


@dataclass
class PolylineData:
    points: List[PointData]
    layer: str
    closed: bool = False
    color: Optional[int] = None
    
    def to_dict(self):
        return {
            'type': 'LWPOLYLINE',
            'points': [p.to_dict() for p in self.points],
            'layer': self.layer,
            'closed': self.closed,
            'color': self.color
        }


@dataclass
class CircleData:
    center: PointData
    radius: float
    layer: str
    color: Optional[int] = None
    
    def to_dict(self):
        return {
            'type': 'CIRCLE',
            'center': self.center.to_dict(),
            'radius': self.radius,
            'layer': self.layer,
            'color': self.color
        }


@dataclass
class BlockInsertData:
    name: str
    position: PointData
    layer: str
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    
    def to_dict(self):
        return {
            'type': 'INSERT',
            'name': self.name,
            'position': self.position.to_dict(),
            'layer': self.layer,
            'rotation': self.rotation,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y
        }


@dataclass
class TextData:
    text: str
    position: PointData
    layer: str
    height: float = 2.5
    rotation: float = 0.0
    color: Optional[int] = None
    
    def to_dict(self):
        return {
            'type': 'TEXT',
            'text': self.text,
            'position': self.position.to_dict(),
            'layer': self.layer,
            'height': self.height,
            'rotation': self.rotation,
            'color': self.color
        }


@dataclass
class ParsedDXF:
    """解析后的DXF数据结构"""
    version: str
    filename: str
    layers: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    
    # 统计信息
    entity_count: int
    layer_count: int
    block_count: int
    
    # 灌溉相关数据
    sprinklers: List[Dict[str, Any]]
    valves: List[Dict[str, Any]]
    pipes: List[Dict[str, Any]]
    green_zones: List[Dict[str, Any]]
    
    # 边界框
    bounds: Dict[str, float]
    
    def to_dict(self):
        """递归转换所有值为JSON可序列化类型"""
        def convert(obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj
        
        return {
            'version': self.version,
            'filename': self.filename,
            'layers': convert(self.layers),
            'entities': convert(self.entities),
            'entity_count': self.entity_count,
            'layer_count': self.layer_count,
            'block_count': self.block_count,
            'sprinklers': convert(self.sprinklers),
            'valves': convert(self.valves),
            'pipes': convert(self.pipes),
            'green_zones': convert(self.green_zones),
            'bounds': convert(self.bounds)
        }


def _convert_value(val):
    """转换numpy类型为Python原生类型"""
    import numpy as np
    if isinstance(val, np.integer):
        return int(val)
    elif isinstance(val, np.floating):
        return float(val)
    elif isinstance(val, np.ndarray):
        return val.tolist()
    return val


def parse_dxf_file(filepath: str) -> ParsedDXF:
    """
    解析DXF文件，返回结构化数据
    
    Args:
        filepath: DXF文件路径
        
    Returns:
        ParsedDXF对象
    """
    if not HAS_EZDXF:
        raise ImportError("ezdxf未安装，无法解析DXF文件")
    
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    
    layers = []
    for layer in doc.layers:
        layers.append({
            'name': layer.dxf.name,
            'color': _convert_value(layer.dxf.color),
            'linetype': layer.dxf.linetype,
            'is_on': bool(layer.is_on) if callable(layer.is_on) else bool(layer.is_on)
        })
    
    # 实体列表
    entities = []
    
    # 灌溉相关统计
    sprinklers = []
    valves = []
    pipes = []
    green_zones = []
    
    # 边界框计算
    all_x = []
    all_y = []
    
    for entity in msp:
        try:
            entity_type = entity.dxftype()
            
            if entity_type == 'LINE':
                start = PointData(entity.dxf.start.x, entity.dxf.start.y)
                end = PointData(entity.dxf.end.x, entity.dxf.end.y)
                layer = entity.dxf.layer
                
                all_x.extend([start.x, end.x])
                all_y.extend([start.y, end.y])
                
                entities.append({
                    'type': 'LINE',
                    'start': start.to_dict(),
                    'end': end.to_dict(),
                    'layer': layer
                })
                
                # 检查是否是管道
                if 'GG-DE' in layer or '管' in layer:
                    pipes.append({
                        'type': 'LINE',
                        'start': start.to_dict(),
                        'end': end.to_dict(),
                        'layer': layer
                    })
                    
            elif entity_type == 'LWPOLYLINE':
                points = []
                for pt in entity.get_points():
                    points.append(PointData(pt[0], pt[1]))
                    all_x.append(pt[0])
                    all_y.append(pt[1])
                
                layer = entity.dxf.layer
                closed = entity.closed if hasattr(entity, 'closed') else False
                
                entities.append({
                    'type': 'LWPOLYLINE',
                    'points': [p.to_dict() for p in points],
                    'layer': layer,
                    'closed': closed
                })
                
                # 检查是否是绿化区域
                if any(keyword in layer for keyword in ['绿化', 'XS', 'LWPOLYLINE']):
                    if len(points) >= 3:
                        green_zones.append({
                            'points': [p.to_dict() for p in points],
                            'layer': layer,
                            'closed': closed
                        })
                        
            elif entity_type == 'CIRCLE':
                center = PointData(entity.dxf.center.x, entity.dxf.center.y)
                radius = entity.dxf.radius
                layer = entity.dxf.layer
                
                all_x.append(center.x + radius)
                all_x.append(center.x - radius)
                all_y.append(center.y + radius)
                all_y.append(center.y - radius)
                
                entities.append({
                    'type': 'CIRCLE',
                    'center': center.to_dict(),
                    'radius': radius,
                    'layer': layer
                })
                
            elif entity_type == 'INSERT':
                name = entity.dxf.name
                position = PointData(entity.dxf.insert.x, entity.dxf.insert.y)
                layer = entity.dxf.layer
                rotation = entity.dxf.rotation
                
                all_x.append(position.x)
                all_y.append(position.y)
                
                entities.append({
                    'type': 'INSERT',
                    'name': name,
                    'position': position.to_dict(),
                    'layer': layer,
                    'rotation': rotation
                })
                
                # 检查是否是喷头
                if name.startswith('K') and '电磁阀' not in name:
                    sprinklers.append({
                        'name': name,
                        'position': position.to_dict(),
                        'layer': layer,
                        'type': _get_sprinkler_type(name)
                    })
                # 检查是否是阀门
                elif '电磁阀' in name or name in ['阀门', 'VALVE']:
                    valves.append({
                        'name': name,
                        'position': position.to_dict(),
                        'layer': layer
                    })
                    
            elif entity_type == 'TEXT' or entity_type == 'MTEXT':
                if entity_type == 'TEXT':
                    text = entity.dxf.text
                    position = PointData(entity.dxf.insert.x, entity.dxf.insert.y)
                else:  # MTEXT
                    text = entity.text
                    position = PointData(entity.dxf.insert.x, entity.dxf.insert.y)
                
                layer = entity.dxf.layer
                height = entity.dxf.height if hasattr(entity.dxf, 'height') else 2.5
                
                entities.append({
                    'type': 'TEXT',
                    'text': text,
                    'position': position.to_dict(),
                    'layer': layer,
                    'height': height
                })
                
        except Exception as e:
            # 跳过解析失败的实体
            continue
    
    # 计算边界框
    if all_x and all_y:
        bounds = {
            'min_x': float(min(all_x)),
            'max_x': float(max(all_x)),
            'min_y': float(min(all_y)),
            'max_y': float(max(all_y)),
            'width': float(max(all_x) - min(all_x)),
            'height': float(max(all_y) - min(all_y))
        }
    else:
        bounds = {'min_x': 0, 'max_x': 100, 'min_y': 0, 'max_y': 100, 'width': 100, 'height': 100}
    
    return ParsedDXF(
        version=doc.dxfversion,
        filename=Path(filepath).name,
        layers=layers,
        entities=entities,
        entity_count=len(entities),
        layer_count=len(layers),
        block_count=len(doc.blocks),
        sprinklers=sprinklers,
        valves=valves,
        pipes=pipes,
        green_zones=green_zones,
        bounds=bounds
    )


def _get_sprinkler_type(block_name: str) -> Dict[str, Any]:
    """根据块名推断喷头类型和参数"""
    
    # 科雨喷头型号映射（从DXF图纸提取）
    type_map = {
        'KXF-8': {'radius': 2.7, 'flow': 0.54, 'name': 'KXF-8 散射喷头'},
        'KVF-10': {'radius': 3.4, 'flow': 0.56, 'name': 'KVF-10 地埋式散射喷头'},
        'KVF-12': {'radius': 3.7, 'flow': 0.66, 'name': 'KVF-12 地埋式散射喷头'},
        'KVF-15': {'radius': 5.0, 'flow': 0.69, 'name': 'KVF-15 地埋式散射喷头'},
        'KVF-17': {'radius': 5.5, 'flow': 0.71, 'name': 'KVF-17 地埋式散射喷头'},
    }
    
    for key, info in type_map.items():
        if key in block_name.upper():
            return info
    
    return {'radius': 3.0, 'flow': 0.6, 'name': block_name}


def parse_dxf_from_upload(file_content: bytes, filename: str) -> ParsedDXF:
    """
    从上传的文件内容解析DXF
    
    Args:
        file_content: 文件二进制内容
        filename: 原始文件名
        
    Returns:
        ParsedDXF对象
    """
    # 保存到临时文件
    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(file_content)
        temp_path = f.name
    
    try:
        result = parse_dxf_file(temp_path)
        return result
    finally:
        # 清理临时文件
        Path(temp_path).unlink(missing_ok=True)


# ============== 测试 ==============

if __name__ == "__main__":
    import sys
    import json
    
    # 自定义JSON编码器处理numpy类型
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"解析: {filepath}")
        result = parse_dxf_file(filepath)
        print(f"版本: {result.version}")
        print(f"图层: {result.layer_count}")
        print(f"实体: {result.entity_count}")
        print(f"喷头: {len(result.sprinklers)}")
        print(f"阀门: {len(result.valves)}")
        print(f"绿化区: {len(result.green_zones)}")
        print(f"边界: {result.bounds}")
        
        # 输出JSON
        print("\n=== JSON输出 ===")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False, cls=NumpyEncoder)[:2000])
    else:
        print("用法: python dxf_parser.py <filepath>")
