from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# =============================================================================
# 请求模型
# =============================================================================

class PointSchema(BaseModel):
    """二维坐标点"""
    x: float = Field(..., description="X坐标（米）")
    y: float = Field(..., description="Y坐标（米）")


class ZoneInput(BaseModel):
    """单个灌溉区输入"""
    zone_id: int = Field(..., description="区域编号")
    boundary: List[PointSchema] = Field(..., description="区域边界顶点列表（闭合多边形）")
    plant_type: Literal["shrub", "lawn", "flower"] = Field(..., description="植物类型")
    location: Literal["edge", "center"] = Field("edge", description="喷头布置位置")


class DesignRequest(BaseModel):
    """灌溉设计请求"""
    zones: List[ZoneInput] = Field(..., min_length=1, description="灌溉区域列表")
    water_source_flow: float = Field(2.5, description="水源流量（m³/h）")
    pipe_size: int = Field(25, description="主管管径（mm）")
    narrow_preference: Literal["drip", "micro_stake"] = Field("drip", description="窄带偏好")
    source_point: Optional[PointSchema] = Field(None, description="水源位置（默认自动计算）")
    show_coverage: bool = Field(True, description="输出中是否显示覆盖范围")
    show_labels: bool = Field(True, description="输出中是否显示标注")


class DXFExportRequest(BaseModel):
    """DXF导出请求"""
    design_result: dict = Field(..., description="设计结果JSON")
    output_filename: str = Field("irrigation_design.dxf", description="输出文件名")


# =============================================================================
# 响应模型
# =============================================================================

class SprinklerOutput(BaseModel):
    """喷头输出"""
    x: float
    y: float
    type: str
    valve_group: int
    spray_radius: float


class PipeOutput(BaseModel):
    """管路输出"""
    x1: float
    y1: float
    x2: float
    y2: float
    pipe_type: str
    diameter: float
    length: float


class ZoneOutput(BaseModel):
    """区域设计结果"""
    zone_id: int
    plant_type: str
    sprinkler_count: int
    valve_count: int
    total_flow: float
    sprinklers: List[SprinklerOutput]
    pipes: List[PipeOutput]


class ValveGroupOutput(BaseModel):
    """阀门组信息"""
    zone_id: int
    valve_id: int
    sprinkler_count: int
    flow: float


class DesignResponse(BaseModel):
    """设计响应"""
    zones: List[ZoneOutput]
    valve_groups: List[ValveGroupOutput]
    total_valves: int
    total_flow: float
    max_group_flow: float
    material_estimate: dict


class ExportResponse(BaseModel):
    """导出响应"""
    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
