"""
MHP 灌溉控制器 HTTP API 客户端
MH Device HTTP API Client for Irrigation Control

协议版本: v1.3
作者: 黄华东
对接项目: 冈仁波齐天山灌溉系统
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """设备在线状态"""
    ONLINE = "在线"
    OFFLINE = "离线"


class ControlStatus(Enum):
    """控制对象开关状态"""
    OPEN = "打开"
    CLOSE = "关闭"


class SignalStrength:
    """信号强度等级"""
    EXCELLENT = (-50, -70, "极强/强")
    GOOD = (-70, -85, "中等")
    FAIR = (-85, -100, "弱")
    POOR = (-100, float('-inf'), "极弱")
    
    @classmethod
    def get_level(cls, signal_dbm: int) -> Tuple[str, str]:
        """
        获取信号强度等级
        
        Args:
            signal_dbm: 信号强度值 (dBm)
            
        Returns:
            (等级描述, 建议)
        """
        if signal_dbm >= -70:
            return cls.EXCELLENT[2], "通信质量良好"
        elif signal_dbm >= -85:
            return cls.GOOD[2], "可正常使用"
        elif signal_dbm >= -100:
            return cls.FAIR[2], "注意信号稳定性"
        else:
            return cls.POOR[2], "建议检查设备位置"


@dataclass
class ControlNode:
    """控制对象节点（水泵/阀门）"""
    nodeaddr: int
    subaddr: int
    name: str
    type: str
    status: str
    lan: str = ""
    power: str = "N/A"
    signal: str = "N/A"
    children: List['ControlNode'] = field(default_factory=list)
    parent: Optional['ControlNode'] = None
    
    @property
    def unique_id(self) -> Tuple[int, int]:
        """唯一标识符 (nodeaddr, subaddr)"""
        return (self.nodeaddr, self.subaddr)
    
    @property
    def is_pump(self) -> bool:
        """是否为水泵"""
        return "水泵" in self.type
    
    @property
    def is_valve(self) -> bool:
        """是否为阀门"""
        return "阀门" in self.type
    
    @property
    def is_open(self) -> bool:
        """是否打开"""
        return self.status == ControlStatus.OPEN.value
    
    @property
    def signal_dbm(self) -> Optional[int]:
        """解析信号强度数值"""
        try:
            # 格式: "-89dbm(强)"
            signal_str = self.signal.split("dbm")[0]
            return int(signal_str)
        except (ValueError, IndexError):
            return None
    
    @property
    def power_percent(self) -> Optional[int]:
        """解析电量百分比"""
        try:
            return int(self.power.replace("%", ""))
        except ValueError:
            return None
    
    def __repr__(self):
        return f"<{self.type} {self.name} ({self.nodeaddr},{self.subaddr}) {self.status}>"


@dataclass
class Device:
    """灌溉设备"""
    deviceid: str
    name: str
    status: str
    city: str = ""
    biosversion: str = ""
    appversion: str = ""
    ctrlcount: int = 0
    ctrlopencount: int = 0
    ctrlclosecount: int = 0
    ctrlerrcount: int = 0
    motcount: int = 0
    control_nodes: List[ControlNode] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)
    
    @property
    def is_online(self) -> bool:
        """是否在线"""
        return self.status == DeviceStatus.ONLINE.value
    
    @property
    def has_error(self) -> bool:
        """是否存在故障"""
        return self.ctrlerrcount > 0
    
    @property
    def error_rate(self) -> float:
        """故障率"""
        if self.ctrlcount == 0:
            return 0.0
        return self.ctrlerrcount / self.ctrlcount
    
    def get_valves(self) -> List[ControlNode]:
        """获取所有阀门"""
        return [n for n in self.control_nodes if n.is_valve]
    
    def get_pumps(self) -> List[ControlNode]:
        """获取所有水泵"""
        return [n for n in self.control_nodes if n.is_pump]
    
    def find_node(self, nodeaddr: int, subaddr: int) -> Optional[ControlNode]:
        """根据地址查找节点"""
        def search(nodes: List[ControlNode]) -> Optional[ControlNode]:
            for node in nodes:
                if node.nodeaddr == nodeaddr and node.subaddr == subaddr:
                    return node
                found = search(node.children)
                if found:
                    return found
            return None
        return search(self.control_nodes)


@dataclass
class DeviceSummary:
    """设备统计汇总"""
    total_devices: int = 0
    online_devices: int = 0
    offline_devices: int = 0
    total_controls: int = 0
    open_controls: int = 0
    close_controls: int = 0
    error_controls: int = 0
    total_sensors: int = 0


class MHPError(Exception):
    """MHP 客户端异常"""
    pass


class MHPAuthError(MHPError):
    """认证失败"""
    pass


class MHPConnectionError(MHPError):
    """连接错误"""
    pass


class MHPClient:
    """
    MHP 灌溉控制器 HTTP 客户端
    
    使用示例:
        client = MHPClient("88888888888", "2119992778")
        devices = client.get_devices()
        for device in devices:
            print(f"{device.name}: {device.status}")
    """
    
    BASE_URL = "http://mhelectr.top:13600"
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, account: str, registid: str, timeout: int = DEFAULT_TIMEOUT):
        """
        初始化 MHP 客户端
        
        Args:
            account: 帐号
            registid: 灌溉服务器设备 ID
            timeout: 请求超时时间（秒）
        """
        self.account = account
        self.registid = registid
        self.timeout = timeout
        self.session = requests.Session()
        self._summary: Optional[DeviceSummary] = None
        self._devices_cache: List[Device] = []
        self._cache_time: Optional[datetime] = None
        
        logger.info(f"MHP Client initialized for account: {account}")
    
    def _request(self, method: str, endpoint: str, params: Dict = None) -> Dict:
        """
        发送 HTTP 请求
        
        Args:
            method: 请求方法 (GET/POST)
            endpoint: API 端点
            params: 请求参数
            
        Returns:
            JSON 响应数据
            
        Raises:
            MHPConnectionError: 网络连接失败
            MHPAuthError: 认证失败
            MHPError: 其他 API 错误
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout)
            else:
                response = self.session.post(url, data=params, timeout=self.timeout)
            
            response.raise_for_status()
            data = response.json()
            
            # 检查业务状态码
            code = data.get("code", 200)
            if code == 401:
                raise MHPAuthError(f"认证失败: {data.get('msg', 'Invalid credentials')}")
            elif code != 200:
                raise MHPError(f"API 错误 ({code}): {data.get('msg', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.Timeout:
            raise MHPConnectionError(f"请求超时 ({self.timeout}s)")
        except requests.exceptions.ConnectionError:
            raise MHPConnectionError(f"无法连接到 {self.BASE_URL}")
        except requests.exceptions.RequestException as e:
            raise MHPConnectionError(f"请求异常: {str(e)}")
    
    def get_device_list(self, page: int = 0, use_cache: bool = False) -> Tuple[List[Device], DeviceSummary]:
        """
        获取设备列表
        
        Args:
            page: 页码 (0-30)
            use_cache: 是否使用缓存
            
        Returns:
            (设备列表, 统计汇总)
        """
        if use_cache and self._devices_cache and self._cache_time:
            cache_age = (datetime.now() - self._cache_time).total_seconds()
            if cache_age < 30:  # 缓存 30 秒
                logger.debug("Using cached device list")
                return self._devices_cache, self._summary
        
        params = {"acctount": self.account, "page": page}
        data = self._request("GET", "/api/devicelist/get", params)
        
        # 解析统计汇总
        summation = data.get("summation", {})
        summary = DeviceSummary(
            total_devices=summation.get("device", 0),
            online_devices=summation.get("online", 0),
            offline_devices=summation.get("offline", 0),
            total_controls=summation.get("ctrlcount", 0),
            open_controls=summation.get("ctrlopencount", 0),
            close_controls=summation.get("ctrlclosecount", 0),
            error_controls=summation.get("ctrlerrcount", 0),
            total_sensors=summation.get("motcount", 0)
        )
        self._summary = summary
        
        # 解析设备列表
        devices = []
        for device_data in data.get("list", []):
            device = Device(
                deviceid=device_data.get("deviceid", ""),
                name=device_data.get("name", "未知设备"),
                status=device_data.get("status", "离线"),
                city=device_data.get("city", ""),
                biosversion=device_data.get("biosversion", ""),
                appversion=device_data.get("appversion", ""),
                ctrlcount=device_data.get("ctrlcount", 0),
                ctrlopencount=device_data.get("ctrlopencount", 0),
                ctrlclosecount=device_data.get("ctrlclosecount", 0),
                ctrlerrcount=device_data.get("ctrlerrcount", 0),
                motcount=device_data.get("motcount", 0),
                last_update=datetime.now()
            )
            devices.append(device)
        
        self._devices_cache = devices
        self._cache_time = datetime.now()
        
        logger.info(f"Retrieved {len(devices)} devices, {summary.online_devices} online")
        return devices, summary
    
    def get_registtab(self, deviceid: Optional[str] = None) -> Dict:
        """
        获取设备注册表
        
        Args:
            deviceid: 指定设备 ID，默认使用初始化时的 registid
            
        Returns:
            原始注册表数据
        """
        registid = deviceid or self.registid
        params = {"acctount": self.account, "registid": registid}
        data = self._request("GET", "/api/registtab/get", params)
        return data
    
    def parse_control_tree(self, registtab_data: Dict) -> List[ControlNode]:
        """
        解析控制对象树
        
        Args:
            registtab_data: 注册表原始数据
            
        Returns:
            控制节点树根列表
        """
        pumps_data = registtab_data.get("pumptab", {}).get("list", [])
        roots = []
        
        for pump_data in pumps_data:
            root = self._parse_node_recursive(pump_data, parent=None)
            roots.append(root)
        
        return roots
    
    def _parse_node_recursive(self, data: Dict, parent: Optional[ControlNode] = None) -> ControlNode:
        """递归解析节点"""
        node = ControlNode(
            nodeaddr=data.get("nodeaddr", 0),
            subaddr=data.get("subaddr", 0),
            name=data.get("name", ""),
            type=data.get("type", ""),
            status=data.get("status", ""),
            lan=data.get("lan", ""),
            power=data.get("power", "N/A"),
            signal=data.get("signal", "N/A"),
            parent=parent
        )
        
        # 递归解析子节点
        for child_data in data.get("list", []):
            child = self._parse_node_recursive(child_data, parent=node)
            node.children.append(child)
        
        return node
    
    def get_device_with_controls(self, deviceid: Optional[str] = None) -> Device:
        """
        获取完整设备信息（包含控制对象树）
        
        Args:
            deviceid: 设备 ID，默认使用 registid
            
        Returns:
            包含控制对象的完整设备信息
        """
        target_id = deviceid or self.registid
        
        # 获取设备基本信息
        devices, _ = self.get_device_list()
        device = next((d for d in devices if d.deviceid == target_id), None)
        
        if not device:
            raise MHPError(f"Device {target_id} not found in device list")
        
        # 获取注册表
        registtab = self.get_registtab(target_id)
        
        # 解析控制树
        device.control_nodes = self.parse_control_tree(registtab)
        
        logger.info(f"Retrieved full device info for {device.name} with {len(device.control_nodes)} root nodes")
        return device
    
    def find_node_by_address(self, nodeaddr: int, subaddr: int, 
                             deviceid: Optional[str] = None) -> Optional[ControlNode]:
        """
        根据地址查找控制节点
        
        Args:
            nodeaddr: 结点地址
            subaddr: 子地址
            deviceid: 设备 ID
            
        Returns:
            控制节点或 None
        """
        device = self.get_device_with_controls(deviceid)
        return device.find_node(nodeaddr, subaddr)
    
    def get_all_valves(self, deviceid: Optional[str] = None) -> List[ControlNode]:
        """获取所有阀门"""
        device = self.get_device_with_controls(deviceid)
        return device.get_valves()
    
    def get_all_pumps(self, deviceid: Optional[str] = None) -> List[ControlNode]:
        """获取所有水泵"""
        device = self.get_device_with_controls(deviceid)
        return device.get_pumps()
    
    def check_errors(self) -> List[Dict]:
        """
        检查所有设备故障
        
        Returns:
            故障信息列表
        """
        devices, summary = self.get_device_list()
        errors = []
        
        for device in devices:
            if device.has_error:
                # 获取详细控制信息
                try:
                    full_device = self.get_device_with_controls(device.deviceid)
                    error_nodes = []
                    
                    def find_error_nodes(nodes: List[ControlNode]):
                        for node in nodes:
                            # 检查信号和电量
                            signal = node.signal_dbm
                            power = node.power_percent
                            
                            if signal is not None and signal < -100:
                                error_nodes.append({
                                    "node": node,
                                    "error": "信号极弱",
                                    "detail": f"{signal}dBm"
                                })
                            
                            if power is not None and power < 20:
                                error_nodes.append({
                                    "node": node,
                                    "error": "电量低",
                                    "detail": f"{power}%"
                                })
                            
                            find_error_nodes(node.children)
                    
                    find_error_nodes(full_device.control_nodes)
                    
                    errors.append({
                        "device": device,
                        "error_count": device.ctrlerrcount,
                        "error_nodes": error_nodes
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to get details for device {device.deviceid}: {e}")
                    errors.append({
                        "device": device,
                        "error_count": device.ctrlerrcount,
                        "error_nodes": [],
                        "detail_error": str(e)
                    })
        
        return errors
    
    def close(self):
        """关闭客户端"""
        self.session.close()
        logger.info("MHP Client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MHPPoller:
    """
    MHP 设备状态轮询器
    
    自动定期轮询设备状态，支持回调函数
    """
    
    def __init__(self, client: MHPClient, 
                 device_interval: int = 30,
                 registtab_interval: int = 300):
        """
        初始化轮询器
        
        Args:
            client: MHP 客户端实例
            device_interval: 设备列表轮询间隔（秒）
            registtab_interval: 注册表轮询间隔（秒）
        """
        self.client = client
        self.device_interval = device_interval
        self.registtab_interval = registtab_interval
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # 回调函数
        self.on_device_update: Optional[Callable[[List[Device], DeviceSummary], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_status_change: Optional[Callable[[Device, str, str], None]] = None
        
        self._last_devices: Dict[str, Device] = {}
        self._last_control_states: Dict[Tuple[int, int], str] = {}
    
    def start(self):
        """启动轮询"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("MHP Poller started")
    
    def stop(self):
        """停止轮询"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("MHP Poller stopped")
    
    def _poll_loop(self):
        """轮询主循环"""
        last_device_poll = 0
        last_registtab_poll = 0
        
        while self._running:
            try:
                current_time = time.time()
                
                # 轮询设备列表
                if current_time - last_device_poll >= self.device_interval:
                    self._poll_devices()
                    last_device_poll = current_time
                
                # 轮询注册表（可以按需扩展）
                if current_time - last_registtab_poll >= self.registtab_interval:
                    # 这里可以实现注册表的定期更新
                    last_registtab_poll = current_time
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Poll error: {e}")
                if self.on_error:
                    self.on_error(e)
                time.sleep(5)
    
    def _poll_devices(self):
        """轮询设备列表"""
        devices, summary = self.client.get_device_list(use_cache=False)
        
        # 检测状态变化
        for device in devices:
            if device.deviceid in self._last_devices:
                last_device = self._last_devices[device.deviceid]
                if last_device.status != device.status:
                    logger.info(f"Device {device.name} status changed: {last_device.status} -> {device.status}")
                    if self.on_status_change:
                        self.on_status_change(device, last_device.status, device.status)
        
        # 更新缓存
        self._last_devices = {d.deviceid: d for d in devices}
        
        # 触发回调
        if self.on_device_update:
            self.on_device_update(devices, summary)


# 便捷函数
def create_client(account: str = "88888888888", registid: str = "2119992778") -> MHPClient:
    """
    创建 MHP 客户端（使用测试账号）
    
    Args:
        account: 帐号
        registid: 灌溉服务器 ID
        
    Returns:
        MHPClient 实例
    """
    return MHPClient(account, registid)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("MHP 灌溉控制器客户端测试")
    print("=" * 60)
    
    with create_client() as client:
        # 获取设备列表
        print("\n[1] 获取设备列表:")
        devices, summary = client.get_device_list()
        print(f"  总计设备: {summary.total_devices}")
        print(f"  在线设备: {summary.online_devices}")
        print(f"  故障控制: {summary.error_controls}")
        
        for device in devices:
            status_icon = "🟢" if device.is_online else "🔴"
            error_icon = "⚠️" if device.has_error else "✅"
            print(f"  {status_icon} {device.name} ({device.deviceid}) {error_icon}")
        
        # 获取完整设备信息
        if devices:
            print("\n[2] 获取设备注册表:")
            device = client.get_device_with_controls()
            
            def print_tree(nodes: List[ControlNode], indent: int = 0):
                for node in nodes:
                    icon = "💧" if node.is_pump else "🔧"
                    status_icon = "🟢" if node.is_open else "⚪"
                    signal_info = f" | 信号: {node.signal}" if node.signal != "N/A" else ""
                    power_info = f" | 电量: {node.power}" if node.power != "N/A" else ""
                    print(f"  {'  ' * indent}{icon} {status_icon} {node.name} ({node.nodeaddr},{node.subaddr}){signal_info}{power_info}")
                    print_tree(node.children, indent + 1)
            
            print_tree(device.control_nodes)
            
            # 检查故障
            print("\n[3] 故障检查:")
            errors = client.check_errors()
            if errors:
                for error in errors:
                    print(f"  ⚠️ {error['device'].name}: {error['error_count']} 个故障")
                    for node_error in error['error_nodes']:
                        print(f"    - {node_error['node'].name}: {node_error['error']} ({node_error['detail']})")
            else:
                print("  ✅ 所有设备正常")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
