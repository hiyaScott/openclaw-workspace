"""
AI工具API配置管理模块
用于读取和管理.env中的API密钥

使用方法:
    from api_config import get_dmxapi_token, get_jimeng_keys
    
    # 获取DMXAPI Token
    token = get_dmxapi_token()
    
    # 获取即梦AI密钥
    ak, sk = get_jimeng_keys()
"""
import os
import sys
from pathlib import Path


def find_workspace_root():
    """查找工作区根目录（包含.env的目录）"""
    # 从当前文件位置开始向上查找
    current = Path(__file__).resolve()
    
    # 向上查找最多5层
    for _ in range(5):
        parent = current.parent
        if (parent / '.env').exists():
            return parent
        current = parent
    
    # 如果找不到，返回工作区默认路径
    return Path('/root/.openclaw/workspace')


def load_env_file():
    """手动加载.env文件到环境变量"""
    # 检查当前环境变量是否已设置（且不为空）
    jimeng_ak = os.environ.get('JIMENG_ACCESS_KEY', '').strip()
    jimeng_sk = os.environ.get('JIMENG_SECRET_KEY', '').strip()
    dmxapi = os.environ.get('DMXAPI_TOKEN', '').strip()
    
    if jimeng_ak and jimeng_sk and dmxapi:
        return True
    
    # 查找.env文件
    workspace = find_workspace_root()
    env_path = workspace / '.env'
    
    if not env_path.exists():
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            # 解析KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # 设置环境变量（如果当前为空或未设置）
                if key:
                    current = os.environ.get(key, '').strip()
                    if not current:  # 只有当当前为空时才设置
                        os.environ[key] = value
    
    return True


class APIConfig:
    """API配置管理类"""
    
    # 即梦AI配置
    @staticmethod
    def get_jimeng_keys():
        """获取即梦AI的AK/SK"""
        load_env_file()  # 确保已加载
        ak = os.environ.get('JIMENG_ACCESS_KEY', '').strip()
        sk = os.environ.get('JIMENG_SECRET_KEY', '').strip()
        
        if not ak or not sk:
            raise ValueError(
                "即梦AI密钥未配置。请在.env文件中设置:\n"
                "JIMENG_ACCESS_KEY=your_access_key\n"
                "JIMENG_SECRET_KEY=your_secret_key"
            )
        return ak, sk
    
    # DMXAPI配置
    @staticmethod
    def get_dmxapi_token():
        """获取DMXAPI的Token"""
        load_env_file()  # 确保已加载
        token = os.environ.get('DMXAPI_TOKEN', '').strip()
        
        if not token:
            raise ValueError(
                "DMXAPI Token未配置。请在.env文件中设置:\n"
                "DMXAPI_TOKEN=your_token"
            )
        return token
    
    # 通用检查
    @staticmethod
    def check_all_configs():
        """检查所有API配置是否就绪"""
        results = {
            'jimeng': {'configured': False, 'error': None},
            'dmxapi': {'configured': False, 'error': None}
        }
        
        try:
            APIConfig.get_jimeng_keys()
            results['jimeng']['configured'] = True
        except ValueError as e:
            results['jimeng']['error'] = str(e)
        
        try:
            APIConfig.get_dmxapi_token()
            results['dmxapi']['configured'] = True
        except ValueError as e:
            results['dmxapi']['error'] = str(e)
        
        return results
    
    @staticmethod
    def print_status():
        """打印所有API配置状态"""
        results = APIConfig.check_all_configs()
        
        print("=" * 50)
        print("API配置状态检查")
        print("=" * 50)
        
        for name, status in results.items():
            if status['configured']:
                print(f"✅ {name.upper()}: 已配置")
            else:
                print(f"❌ {name.upper()}: 未配置")
                print(f"   错误: {status['error']}")
        
        print("=" * 50)


# 便捷函数
def get_jimeng_keys():
    """便捷函数：获取即梦AI密钥"""
    return APIConfig.get_jimeng_keys()

def get_dmxapi_token():
    """便捷函数：获取DMXAPI Token"""
    return APIConfig.get_dmxapi_token()


if __name__ == "__main__":
    # 运行状态检查
    APIConfig.print_status()
