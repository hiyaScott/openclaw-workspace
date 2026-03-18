#!/usr/bin/env python3
"""
OpenViking 快速配置 - NVIDIA NIM 版本
需要在环境变量中设置 NVIDIA_API_KEY
"""

import os
import json
import sys

CONFIG_DIR = os.path.expanduser("~/.openviking")
CONFIG_FILE = os.path.join(CONFIG_DIR, "ov.conf")

def main():
    # 从环境变量获取 API Key
    api_key = os.environ.get('NVIDIA_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ 未找到 API Key")
        print("\n请设置环境变量后重试:")
        print("  export NVIDIA_API_KEY='你的NVIDIA API Key'")
        print("  或")
        print("  export OPENAI_API_KEY='你的OpenAI API Key'")
        print("\n获取免费 NVIDIA API Key:")
        print("  1. 访问 https://build.nvidia.com/")
        print("  2. 注册账号")
        print("  3. 点击 API Keys → Generate Key")
        sys.exit(1)
    
    # 判断是 NVIDIA 还是 OpenAI
    if 'NVIDIA' in os.environ and os.environ.get('NVIDIA_API_KEY'):
        # NVIDIA NIM 配置
        config = {
            "embedding": {
                "dense": {
                    "provider": "openai",
                    "api_base": "https://integrate.api.nvidia.com/v1",
                    "api_key": api_key,
                    "model": "nvidia/nv-embed-v1",
                    "dimension": 4096
                }
            },
            "vlm": {
                "provider": "openai",
                "api_base": "https://integrate.api.nvidia.com/v1",
                "api_key": api_key,
                "model": "meta/llama-3.3-70b-instruct"
            }
        }
        provider = "NVIDIA NIM"
    else:
        # OpenAI 配置
        config = {
            "embedding": {
                "dense": {
                    "provider": "openai",
                    "api_base": "https://api.openai.com/v1",
                    "api_key": api_key,
                    "model": "text-embedding-3-small",
                    "dimension": 1536
                }
            },
            "vlm": {
                "provider": "openai",
                "api_base": "https://api.openai.com/v1",
                "api_key": api_key,
                "model": "gpt-4o-mini"
            }
        }
        provider = "OpenAI"
    
    # 保存配置
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # 备份旧配置
    if os.path.exists(CONFIG_FILE):
        backup_file = CONFIG_FILE + ".backup"
        with open(CONFIG_FILE, 'r') as f:
            old_config = f.read()
        with open(backup_file, 'w') as f:
            f.write(old_config)
        print(f"💾 旧配置已备份: {backup_file}")
    
    # 写入新配置
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    os.chmod(CONFIG_FILE, 0o600)
    
    print(f"✅ {provider} 配置已保存到: {CONFIG_FILE}")
    
    # 测试连接
    print("\n🔄 测试 API 连接...")
    try:
        venv_path = "/root/.openclaw/workspace/.venv"
        site_packages = os.path.join(venv_path, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)
        
        import openviking as ov
        os.environ['OPENVIKING_CONFIG_FILE'] = CONFIG_FILE
        
        client = ov.SyncOpenViking(path="/tmp/openviking_test")
        client.initialize()
        
        print("✅ API 连接测试成功！OpenViking 可以正常使用")
        client.close()
        
        # 清理
        import shutil
        if os.path.exists("/tmp/openviking_test"):
            shutil.rmtree("/tmp/openviking_test")
            
    except Exception as e:
        print(f"⚠️ API 测试失败: {e}")
        print("   配置已保存，但 API 可能暂时不可用")

if __name__ == "__main__":
    main()
