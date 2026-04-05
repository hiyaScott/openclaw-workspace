"""
FastAPI 路由 - MHP 设备管理 API
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

from ..mhp_client import MHPDeviceService, MHPError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mhp", tags=["MHP 灌溉控制器"])

# 全局服务实例
_device_service: Optional[MHPDeviceService] = None


def init_mhp_service(account: str, registid: str):
    """初始化 MHP 服务"""
    global _device_service
    _device_service = MHPDeviceService(account, registid)


def get_service() -> MHPDeviceService:
    """获取服务实例"""
    if _device_service is None:
        raise HTTPException(status_code=503, detail="MHP service not initialized")
    return _device_service


# Pydantic 模型
class DeviceBasicInfo(BaseModel):
    device_id: str
    name: str
    status: str
    city: str
    version: str


class DeviceStatusResponse(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    devices: List[Dict]


class ValveInfo(BaseModel):
    name: str
    address: str
    status: str
    power: str
    signal: str
    parent_pump: Optional[str]


class IrrigationStatus(BaseModel):
    device_id: str
    device_name: str
    is_online: bool
    irrigation_active: bool
    active_zones: List[Dict]
    pump_status: Dict
    statistics: Dict


class SystemHealth(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    online_rate: str
    has_errors: bool
    errors: List[Dict]
    last_update: Optional[str]


# API 路由
@router.get("/devices", response_model=DeviceStatusResponse)
async def get_devices(force_refresh: bool = False, service: MHPDeviceService = Depends(get_service)):
    """
    获取所有设备列表
    
    Args:
        force_refresh: 是否强制刷新缓存
    """
    try:
        devices = await service.get_all_devices(force_refresh)
        return {
            "total_devices": len(devices),
            "online_devices": sum(1 for d in devices if d.is_online),
            "offline_devices": sum(1 for d in devices if not d.is_online),
            "devices": [
                {
                    "device_id": d.deviceid,
                    "name": d.name,
                    "status": d.status,
                    "city": d.city,
                    "version": f"{d.biosversion}/{d.appversion}",
                    "ctrl_count": d.ctrlcount,
                    "error_count": d.ctrlerrcount,
                    "is_online": d.is_online
                }
                for d in devices
            ]
        }
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/devices/{device_id}")
async def get_device_detail(device_id: str, service: MHPDeviceService = Depends(get_service)):
    """获取设备详情（包含控制对象树）"""
    try:
        device = await service.get_device_detail(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        def node_to_dict(node, parent_name=None):
            return {
                "name": node.name,
                "type": node.type,
                "address": f"{node.nodeaddr},{node.subaddr}",
                "status": node.status,
                "lan": node.lan,
                "power": node.power,
                "signal": node.signal,
                "is_open": node.is_open,
                "is_pump": node.is_pump,
                "is_valve": node.is_valve,
                "parent": parent_name,
                "children": [node_to_dict(child, node.name) for child in node.children]
            }
        
        return {
            "device_id": device.deviceid,
            "name": device.name,
            "status": device.status,
            "city": device.city,
            "version": {
                "bios": device.biosversion,
                "app": device.appversion
            },
            "control_tree": [node_to_dict(node) for node in device.control_nodes],
            "statistics": {
                "ctrl_count": device.ctrlcount,
                "open_count": device.ctrlopencount,
                "close_count": device.ctrlclosecount,
                "error_count": device.ctrlerrcount
            }
        }
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/devices/{device_id}/irrigation", response_model=IrrigationStatus)
async def get_irrigation_status(device_id: str, service: MHPDeviceService = Depends(get_service)):
    """获取灌溉系统运行状态"""
    try:
        status = await service.get_irrigation_status(device_id)
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        return status
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/devices/{device_id}/pumps")
async def get_pump_status(device_id: str, service: MHPDeviceService = Depends(get_service)):
    """获取水泵状态"""
    try:
        status = await service.get_pump_status(device_id)
        return status
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/devices/{device_id}/valves")
async def get_valves(device_id: str, zone_id: Optional[str] = None, 
                     service: MHPDeviceService = Depends(get_service)):
    """
    获取阀门列表
    
    Args:
        zone_id: 可选，按区域过滤
    """
    try:
        if zone_id:
            valves = await service.get_valves_by_zone(device_id, zone_id)
        else:
            device = await service.get_device_detail(device_id)
            valves = device.get_valves() if device else []
        
        return {
            "device_id": device_id,
            "zone_filter": zone_id,
            "total": len(valves),
            "open_count": sum(1 for v in valves if v.is_open),
            "valves": [
                {
                    "name": v.name,
                    "address": f"{v.nodeaddr},{v.subaddr}",
                    "status": v.status,
                    "power": v.power,
                    "signal": v.signal
                }
                for v in valves
            ]
        }
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/health", response_model=SystemHealth)
async def get_system_health(service: MHPDeviceService = Depends(get_service)):
    """获取系统健康状态"""
    try:
        health = await service.get_system_health()
        return health
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/summary")
async def get_dashboard_summary(service: MHPDeviceService = Depends(get_service)):
    """
    仪表盘汇总数据
    
    用于前端仪表盘展示的关键指标
    """
    try:
        devices = await service.get_all_devices()
        
        # 计算总体统计
        total = len(devices)
        online = sum(1 for d in devices if d.is_online)
        
        # 获取第一个在线设备的灌溉状态（示例）
        irrigation_status = None
        for device in devices:
            if device.is_online:
                irrigation_status = await service.get_irrigation_status(device.deviceid)
                break
        
        return {
            "system": {
                "total_devices": total,
                "online_devices": online,
                "offline_devices": total - online,
                "health_status": "healthy" if online == total else "warning" if online > 0 else "critical"
            },
            "irrigation": irrigation_status,
            "alerts": [
                {
                    "type": "warning" if d.has_error else "info",
                    "device": d.name,
                    "message": f"{d.ctrlerrcount} 个控制对象故障"
                }
                for d in devices if d.has_error
            ]
        }
    except MHPError as e:
        raise HTTPException(status_code=502, detail=str(e))
