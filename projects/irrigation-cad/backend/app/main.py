"""
花园灌溉CAD设计系统 - FastAPI后端

API端点：
- POST /api/parse-dxf  - 解析DXF文件，返回几何数据
- POST /api/design     - 生成灌溉设计方案
- POST /api/export/dxf - 导出DXF文件
- POST /api/export/pdf - 导出PDF文件
- GET  /api/config     - 获取喷头配置列表
"""

import os
import json
import tempfile
from typing import List
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    DesignRequest, DesignResponse,
    DXFExportRequest, ExportResponse,
    ZoneOutput, SprinklerOutput, PipeOutput,
    ValveGroupOutput, PointSchema
)
from core.sprinkler_layout import (
    Point, Polygon, PlantType, SprinklerType,
    design_irrigation_zone, calculate_valve_groups,
    estimate_materials, SPRINKLER_CONFIGS
)
from core.dxf_writer import export_design_to_dxf, export_to_pdf
from core.dxf_parser import parse_dxf_from_upload, parse_dxf_file

app = FastAPI(
    title="花园灌溉CAD设计系统",
    description="基于CAD图纸自动生成灌溉管路和点位的API服务",
    version="0.1.0"
)

# CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "/tmp/irrigation-cad-outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# API端点
# =============================================================================

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "花园灌溉CAD设计系统",
        "version": "0.1.0"
    }


@app.post("/api/parse-dxf")
async def parse_dxf(file: UploadFile = File(...)):
    """
    解析DXF文件
    
    上传DXF文件，返回解析后的几何数据
    包括：图层、实体、喷头、阀门、绿化区等
    """
    try:
        content = await file.read()
        result = parse_dxf_from_upload(content, file.filename)
        return JSONResponse(content=result.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DXF解析错误: {str(e)}")


@app.get("/api/config")
async def get_config():
    """获取喷头配置列表"""
    configs = {}
    for st, cfg in SPRINKLER_CONFIGS.items():
        configs[st.value] = {
            "name": cfg.name,
            "price": cfg.price,
            "install_fee": cfg.install_fee,
            "flow": cfg.flow,
            "unit": cfg.unit,
            "spray_radius": cfg.spray_radius,
            "spacing": cfg.spacing,
            "coverage_pattern": cfg.coverage_pattern
        }
    return {
        "sprinkler_types": configs,
        "plant_types": ["shrub", "lawn", "flower"],
        "pipe_sizes": [25, 32],
        "water_source_flows": [2.5, 3.0, 3.5]
    }


@app.post("/api/design", response_model=DesignResponse)
async def create_design(request: DesignRequest):
    """
    生成灌溉设计方案
    
    输入：区域边界多边形列表 + 参数
    输出：喷头位置、管道路径、阀门分组、材料估算
    """
    try:
        zones = []
        
        # 水源位置
        source = None
        if request.source_point:
            source = Point(request.source_point.x, request.source_point.y)
        
        for zone_input in request.zones:
            # 转换边界多边形
            points = [Point(p.x, p.y) for p in zone_input.boundary]
            polygon = Polygon(points=points)
            
            # 设计该区域
            zone = design_irrigation_zone(
                zone_id=zone_input.zone_id,
                boundary=polygon,
                plant_type=PlantType(zone_input.plant_type),
                water_source_flow=request.water_source_flow,
                pipe_size=request.pipe_size,
                narrow_preference=request.narrow_preference,
                location=zone_input.location,
                source_point=source
            )
            zones.append(zone)
        
        # 计算阀门分组
        valve_result = calculate_valve_groups(zones, request.water_source_flow)
        
        # 材料估算
        materials = estimate_materials(zones)
        
        # 构建响应
        zone_outputs = []
        for zone in zones:
            sprinklers = [
                SprinklerOutput(
                    x=s.position.x, y=s.position.y,
                    type=s.type.value,
                    valve_group=s.valve_group,
                    spray_radius=SPRINKLER_CONFIGS[s.type].spray_radius
                )
                for s in zone.sprinklers
            ]
            
            pipes = [
                PipeOutput(
                    x1=p.start.x, y1=p.start.y,
                    x2=p.end.x, y2=p.end.y,
                    pipe_type=p.pipe_type,
                    diameter=p.diameter,
                    length=round(p.length(), 2)
                )
                for p in zone.pipes
            ]
            
            zone_outputs.append(ZoneOutput(
                zone_id=zone.zone_id,
                plant_type=zone.plant_type.value,
                sprinkler_count=len(zone.sprinklers),
                valve_count=zone.valve_count,
                total_flow=round(zone.total_flow, 2),
                sprinklers=sprinklers,
                pipes=pipes
            ))
        
        valve_groups = [
            ValveGroupOutput(
                zone_id=g["zone_id"],
                valve_id=g["valve_id"],
                sprinkler_count=g["sprinkler_count"],
                flow=round(g["flow"], 2)
            )
            for g in valve_result["groups"]
        ]
        
        return DesignResponse(
            zones=zone_outputs,
            valve_groups=valve_groups,
            total_valves=valve_result["total_valves"],
            total_flow=round(valve_result["total_flow"], 2),
            max_group_flow=round(valve_result["max_group_flow"], 2),
            material_estimate=materials
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设计计算错误: {str(e)}")


@app.post("/api/export/dxf")
async def export_dxf(request: DesignRequest):
    """
    导出DXF文件
    
    流程：先design → 再export
    """
    try:
        # 1. 执行设计
        design_result = await create_design(request)
        
        # 2. 重建Zone对象用于DXF导出
        zones = _rebuild_zones_from_response(design_result)
        
        # 3. 生成DXF
        filename = f"irrigation_design_{request.zones[0].zone_id}.dxf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        export_design_to_dxf(
            zones=zones,
            output_path=filepath,
            show_coverage=request.show_coverage,
            show_labels=request.show_labels
        )
        
        file_size = os.path.getsize(filepath)
        
        return ExportResponse(
            success=True,
            file_path=filepath,
            file_size=file_size,
            download_url=f"/api/download/{filename}",
            error=None
        )
        
    except Exception as e:
        return ExportResponse(
            success=False,
            error=str(e)
        )


@app.post("/api/export/pdf")
async def export_pdf(request: DesignRequest):
    """导出PDF文件"""
    try:
        design_result = await create_design(request)
        zones = _rebuild_zones_from_response(design_result)
        
        filename = f"irrigation_design_{request.zones[0].zone_id}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        export_to_pdf(
            zones=zones,
            output_path=filepath,
            show_coverage=request.show_coverage,
            show_labels=request.show_labels
        )
        
        file_size = os.path.getsize(filepath)
        
        return ExportResponse(
            success=True,
            file_path=filepath,
            file_size=file_size,
            download_url=f"/api/download/{filename}",
            error=None
        )
        
    except Exception as e:
        return ExportResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载生成的文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    media_type = "application/dxf" if filename.endswith(".dxf") else "application/pdf"
    return FileResponse(filepath, media_type=media_type, filename=filename)


# =============================================================================
# 辅助函数
# =============================================================================

def _rebuild_zones_from_response(design_result: DesignResponse):
    """从API响应重建Zone对象，用于导出"""
    from core.sprinkler_layout import (
        IrrigationZone, Polygon, Sprinkler,
        PipeSegment, PlantType, SprinklerType
    )
    
    zones = []
    for z in design_result.zones:
        # 重建边界（简化：用 sprinklers 的包围盒近似）
        if z.sprinklers:
            xs = [s.x for s in z.sprinklers]
            ys = [s.y for s in z.sprinklers]
            margin = 2.0
            boundary_points = [
                Point(min(xs) - margin, min(ys) - margin),
                Point(max(xs) + margin, min(ys) - margin),
                Point(max(xs) + margin, max(ys) + margin),
                Point(min(xs) - margin, max(ys) + margin),
            ]
        else:
            boundary_points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
        
        sprinklers = [
            Sprinkler(
                position=Point(s.x, s.y),
                type=SprinklerType(s.type),
                valve_group=s.valve_group
            )
            for s in z.sprinklers
        ]
        
        pipes = [
            PipeSegment(
                start=Point(p.x1, p.y1),
                end=Point(p.x2, p.y2),
                pipe_type=p.pipe_type,
                diameter=p.diameter
            )
            for p in z.pipes
        ]
        
        zones.append(IrrigationZone(
            zone_id=z.zone_id,
            boundary=Polygon(boundary_points),
            plant_type=PlantType(z.plant_type),
            sprinklers=sprinklers,
            pipes=pipes,
            valve_count=z.valve_count,
            total_flow=z.total_flow
        ))
    
    return zones


# =============================================================================
# 启动
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
