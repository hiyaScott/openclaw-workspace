"""
MHP 设备服务 - 与冈仁波齐服务端集成
提供设备管理、状态监控、控制指令下发等功能
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging

from .client import MHPClient, Device, ControlNode, DeviceSummary, MHPError

logger = logging.getLogger(__name__)


class MHPDeviceService:
    """
    MHP 设备服务
    
    封装 MHP 客户端，提供更高层的业务接口
    """
    
    def __init__(self, account: str, registid: str):
        self.client = MHPClient(account, registid)
        self._device_cache: Dict[str, Device] = {}
        self._last_update: Optional[datetime] = None
    
    async def get_all_devices(self, force_refresh: bool = False) -> List[Device]:
        """获取所有设备"""
        loop = asyncio.get_event_loop()
        devices, summary = await loop.run_in_executor(
            None, self.client.get_device_list, 0, not force_refresh
        )
        
        # 更新缓存
        for device in devices:
            self._device_cache[device.deviceid] = device
        
        self._last_update = datetime.now()
        return devices
    
    async def get_device_detail(self, deviceid: str) -> Optional[Device]:
        """获取设备详情"""
        try:
            loop = asyncio.get_event_loop()
            device = await loop.run_in_executor(
                None, self.client.get_device_with_controls, deviceid
            )
            self._device_cache[deviceid] = device
            return device
        except MHPError as e:
            logger.error(f"Failed to get device {deviceid}: {e}")
            return None
    
    async def get_valves_by_zone(self, deviceid: str, zone_id: str) -> List[ControlNode]:
        """
        按灌溉区域获取阀门
        
        假设阀门名称包含区域标识，如 "阀门-ZoneA-01"
        """
        device = await self.get_device_detail(deviceid)
        if not device:
            return []
        
        all_valves = device.get_valves()
        zone_valves = [v for v in all_valves if zone_id.lower() in v.name.lower()]
        return zone_valves
    
    async def get_pump_status(self, deviceid: str) -> Dict:
        """获取水泵状态"""
        device = await self.get_device_detail(deviceid)
        if not device:
            return {}
        
        pumps = device.get_pumps()
        return {
            "total": len(pumps),
            "running": sum(1 for p in pumps if p.is_open),
            "stopped": sum(1 for p in pumps if not p.is_open),
            "pumps": [
                {
                    "name": p.name,
                    "address": f"{p.nodeaddr},{p.subaddr}",
                    "status": p.status,
                    "power": p.power,
                    "signal": p.signal
                }
                for p in pumps
            ]
        }
    
    async def get_system_health(self) -> Dict:
        """获取系统健康状态"""
        devices = await self.get_all_devices()
        
        total = len(devices)
        online = sum(1 for d in devices if d.is_online)
        offline = total - online
        
        errors = []
        for device in devices:
            if device.has_error:
                errors.append({
                    "device_id": device.deviceid,
                    "device_name": device.name,
                    "error_count": device.ctrlerrcount,
                    "error_rate": f"{device.error_rate:.1%}"
                })
        
        return {
            "total_devices": total,
            "online_devices": online,
            "offline_devices": offline,
            "online_rate": f"{online/total:.1%}" if total > 0 else "N/A",
            "has_errors": len(errors) > 0,
            "errors": errors,
            "last_update": self._last_update.isoformat() if self._last_update else None
        }
    
    async def get_irrigation_status(self, deviceid: str) -> Dict:
        """
        获取灌溉系统运行状态
        
        用于前端仪表盘展示
        """
        device = await self.get_device_detail(deviceid)
        if not device:
            return {"error": "Device not found"}
        
        valves = device.get_valves()
        pumps = device.get_pumps()
        
        open_valves = [v for v in valves if v.is_open]
        running_pumps = [p for p in pumps if p.is_open]
        
        return {
            "device_id": device.deviceid,
            "device_name": device.name,
            "is_online": device.is_online,
            "irrigation_active": len(open_valves) > 0,
            "active_zones": [
                {
                    "valve_name": v.name,
                    "address": f"{v.nodeaddr},{v.subaddr}",
                    "power": v.power,
                    "signal": v.signal
                }
                for v in open_valves
            ],
            "pump_status": {
                "running": len(running_pumps),
                "total": len(pumps),
                "details": [
                    {"name": p.name, "power": p.power} 
                    for p in running_pumps
                ]
            },
            "statistics": {
                "total_valves": len(valves),
                "open_valves": len(open_valves),
                "total_pumps": len(pumps),
                "running_pumps": len(running_pumps)
            }
        }
    
    def close(self):
        """关闭服务"""
        self.client.close()


class MHPAsyncPoller:
    """
    异步 MHP 设备状态轮询器
    
    用于服务端后台任务
    """
    
    def __init__(self, service: MHPDeviceService, interval: int = 30):
        self.service = service
        self.interval = interval
        self._running = False
        self._task = None
    
    async def start(self):
        """启动轮询"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("MHP Async Poller started")
    
    async def stop(self):
        """停止轮询"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("MHP Async Poller stopped")
    
    async def _poll_loop(self):
        """轮询循环"""
        while self._running:
            try:
                await self.service.get_all_devices(force_refresh=True)
                logger.debug("Device poll completed")
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Poll error: {e}")
                await asyncio.sleep(5)
