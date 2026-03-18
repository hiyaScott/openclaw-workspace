#!/usr/bin/env python3
"""
OpenViking 国内平台配置脚本
支持：阿里云百炼、火山引擎、硅基流动
"""

import os
import json
import sys

CONFIG_DIR = os.path.expanduser("~/.openviking")
CONFIG_FILE = os.path.join(CONFIG_DIR, "ov.conf")

def setup_aliyun():
    """配置阿里云百炼"""
    print("\n📌 阿里云百炼配置")
    print("-" * 50)
    print("免费额度：100万 tokens/模型（90天有效）")
    print("Embedding模型：text-embedding-v3 (1024维)")
    print("\n获取 API Key:")
    print("  1. 访问 https://bailian.console.aliyun.com/")
    print("  2. 登录阿里云账号")
    print("  3. 点击左侧「API Key」→ 创建 API Key")
    print("  4. 复制生成的 Key")
    print()
    
    api_key = input("粘贴阿里云 API Key: ").strip()
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
    config = {
        "embedding": {
            "dense": {
                "provider": "openai",
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": api_key,
                "model": "text-embedding-v3",
                "dimension": 1024
            }
        },
        "vlm": {
            "provider": "openai",
            "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": api_key,
            "model": "qwen-turbo"
        }
    }
    
    return save_config(config, "阿里云百炼")

def setup_volcengine():
    """配置火山引擎"""
    print("\n📌 火山引擎配置")
    print("-" * 50)
    print("免费额度：50万 tokens/模型")
    print("Embedding模型：doubao-embedding-large (2048维)")
    print("\n获取 API Key:")
    print("  1. 访问 https://console.volcengine.com/ark")
    print("  2. 注册/登录火山引擎账号")
    print("  3. 点击「开通管理」→ 开通 doubao-embedding-large")
    print("  4. 点击「API Key管理」→ 创建 API Key")
    print()
    
    api_key = input("粘贴火山引擎 API Key: ").strip()
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
    config = {
        "embedding": {
            "dense": {
                "provider": "openai",
                "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                "api_key": api_key,
                "model": "doubao-embedding-large-text-250515",
                "dimension": 2048
            }
        },
        "vlm": {
            "provider": "openai",
            "api_base": "https://ark.cn-beijing.volces.com/api/v3",
            "api_key": api_key,
            "model": "deepseek-v3-2-251201"
        }
    }
    
    return save_config(config, "火山引擎")

def setup_siliconflow():
    """配置硅基流动"""
    print("\n📌 硅基流动配置")
    print("-" * 50)
    print("免费额度：新用户14元 + 免费模型无限额")
    print("Embedding模型：BAAI/bge-m3 (免费)")
    print("\n获取 API Key:")
    print("  1. 访问 https://cloud.siliconflow.cn/")
    print("  2. 注册账号")
    print("  3. 点击「API密钥」→ 新建 API Key")
    print()
    
    api_key = input("粘贴硅基流动 API Key: ").strip()
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
    config = {
        "embedding": {
            "dense": {
                "provider": "openai",
                "api_base": "https://api.siliconflow.cn/v1",
                "api_key": api_key,
                "model": "BAAI/bge-m3",
                "dimension": 1024
            }
        },
        "vlm": {
            "provider": "openai",
            "api_base": "https://api.siliconflow.cn/v1",
            "api_key": api_key,
            "model": "Qwen/Qwen2.5-7B-Instruct"
        }
    }
    
    return save_config(config, "硅基流动")

def save_config(config, provider_name):
    """保存配置"""
    try:
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
        
        print(f"\n✅ {provider_name} 配置已保存！")
        print(f"   配置文件: {CONFIG_FILE}")
        return True
        
    except Exception as e:
        print(f"\n❌ 保存失败: {e}")
        return False

def test_connection():
    """测试连接"""
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
        
        print("✅ 连接测试成功！OpenViking 可以正常使用")
        client.close()
        
        # 清理
        import shutil
        if os.path.exists("/tmp/openviking_test"):
            shutil.rmtree("/tmp/openviking_test")
            
        return True
        
    except Exception as e:
        print(f"⚠️ 连接测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("  OpenViking 国内平台配置工具")
    print("=" * 60)
    print("\n📊 各平台免费额度对比:")
    print()
    print("  1. 阿里云百炼  - 100万 tokens/模型 (90天) ⭐推荐")
    print("  2. 火山引擎    - 50万 tokens/模型")
    print("  3. 硅基流动    - 14元 + 免费模型")
    print()
    print("  4. 退出")
    print()
    
    choice = input("请选择平台 (1-4): ").strip()
    
    success = False
    
    if choice == '1':
        success = setup_aliyun()
    elif choice == '2':
        success = setup_volcengine()
    elif choice == '3':
        success = setup_siliconflow()
    elif choice == '4':
        print("已退出")
        return
    else:
        print("❌ 无效选项")
        return
    
    if success:
        input("\n按回车键测试 API 连接...")
        if test_connection():
            print("\n🎉 配置完成！OpenViking 已就绪")
            print("\n快速开始:")
            print("  python3 skills/openviking/viking.py init")
            print("  python3 skills/openviking/viking.py add <文件路径>")
        else:
            print("\n⚠️ 配置已保存，但 API 测试失败")
            print("   请检查 API Key 是否正确，或稍后重试")

if __name__ == "__main__":
    main()
