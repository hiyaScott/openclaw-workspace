"""
AI工具API配置管理模块
用于读取和管理.env中的API密钥
"""
import os
from pathlib import Path

# 尝试加载python-dotenv（如果已安装）
try:
    from dotenv import load_dotenv
    # 加载.env文件
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # 如果没有dotenv，直接读取系统环境变量

class APIConfig:
    """API配置管理类"""
    
    # 即梦AI配置
    @staticmethod
    def get_jimeng_keys():
        """获取即梦AI的AK/SK"""
        ak = os.environ.get('JIMENG_ACCESS_KEY')
        sk = os.environ.get('JIMENG_SECRET_KEY')
        
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
        token = os.environ.get('DMXAPI_TOKEN')
        
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
