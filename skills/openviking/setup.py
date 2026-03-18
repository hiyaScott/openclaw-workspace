#!/usr/bin/env python3
"""
OpenViking 自动配置脚本
支持 NVIDIA NIM (免费) 和 OpenAI API 两种配置方式
"""

import os
import json
import sys

CONFIG_DIR = os.path.expanduser("~/.openviking")
CONFIG_FILE = os.path.join(CONFIG_DIR, "ov.conf")

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_step(step, text):
    print(f"  [{step}] {text}")

def check_existing_config():
    """检查现有配置"""
    if os.path.exists(CONFIG_FILE):
        print("⚠️  检测到已有配置文件")
        with open(CONFIG_FILE, 'r') as f:
            try:
                config = json.load(f)
                has_embedding_key = bool(config.get('embedding', {}).get('dense', {}).get('api_key'))
                has_vlm_key = bool(config.get('vlm', {}).get('api_key'))
                
                if has_embedding_key and has_vlm_key:
                    print("   配置文件已存在且包含 API Key")
                    response = input("   是否覆盖? (y/n): ").lower()
                    return response == 'y'
                else:
                    print("   配置文件存在但缺少 API Key，将更新配置")
                    return True
            except:
                print("   配置文件格式错误，将重新创建")
                return True
    return True

def setup_nvidia_nim():
    """配置 NVIDIA NIM"""
    print_header("NVIDIA NIM 配置 (免费)")
    
    print("📋 配置步骤:")
    print_step(1, "访问 https://build.nvidia.com/")
    print_step(2, "点击右上角 Sign In，用邮箱或 Google 账号注册")
    print_step(3, "登录后点击右上角用户名 → API Keys")
    print_step(4, "点击 Generate Key，复制生成的 API Key")
    print()
    
    print("粘贴你的 NVIDIA API Key (输入完成后按回车):")
    api_key = input("> ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
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
    
    return save_config(config, "NVIDIA NIM")

def setup_openai():
    """配置 OpenAI"""
    print_header("OpenAI API 配置")
    
    print("📋 配置步骤:")
    print_step(1, "访问 https://platform.openai.com/api-keys")
    print_step(2, "登录 OpenAI 账号")
    print_step(3, "点击 Create new secret key")
    print_step(4, "复制生成的 API Key")
    print()
    
    print("粘贴你的 OpenAI API Key (输入完成后按回车):")
    api_key = input("> ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
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
    
    return save_config(config, "OpenAI")

def setup_custom():
    """自定义配置"""
    print_header("自定义 API 配置")
    
    print("支持的其他 API 提供商:")
    print("  - 火山引擎 (Volcengine)")
    print("  - 阿里云 DashScope")
    print("  - 其他兼容 OpenAI 格式的 API")
    print()
    
    print("请输入 API Base URL (例如: https://api.example.com/v1):")
    api_base = input("> ").strip()
    
    print("请输入 API Key:")
    api_key = input("> ").strip()
    
    print("请输入 Embedding 模型名称:")
    embedding_model = input("> ").strip() or "text-embedding-3-small"
    
    print("请输入 Embedding 维度 (默认 1536):")
    dimension = input("> ").strip() or "1536"
    
    print("请输入 VLM 模型名称:")
    vlm_model = input("> ").strip() or "gpt-4o-mini"
    
    config = {
        "embedding": {
            "dense": {
                "provider": "openai",
                "api_base": api_base,
                "api_key": api_key,
                "model": embedding_model,
                "dimension": int(dimension)
            }
        },
        "vlm": {
            "provider": "openai",
            "api_base": api_base,
            "api_key": api_key,
            "model": vlm_model
        }
    }
    
    return save_config(config, "自定义")

def save_config(config, provider_name):
    """保存配置到文件"""
    try:
        # 创建配置目录
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # 备份旧配置
        if os.path.exists(CONFIG_FILE):
            backup_file = CONFIG_FILE + ".backup"
            with open(CONFIG_FILE, 'r') as f:
                old_config = f.read()
            with open(backup_file, 'w') as f:
                f.write(old_config)
            print(f"💾 旧配置已备份到: {backup_file}")
        
        # 写入新配置
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        # 设置文件权限 (只有所有者可读写)
        os.chmod(CONFIG_FILE, 0o600)
        
        print(f"\n✅ {provider_name} 配置已保存到: {CONFIG_FILE}")
        print(f"   配置文件权限已设置为 600 (仅所有者可访问)")
        return True
        
    except Exception as e:
        print(f"\n❌ 保存配置失败: {e}")
        return False

def test_config():
    """测试配置是否有效"""
    print_header("测试配置")
    
    print("是否现在测试 API 连接? (y/n)")
    response = input("> ").lower()
    
    if response != 'y':
        print("跳过测试")
        return
    
    print("正在测试 API 连接...")
    
    try:
        # 激活虚拟环境
        venv_path = "/root/.openclaw/workspace/.venv"
        site_packages = os.path.join(venv_path, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)
        
        import openviking as ov
        
        # 设置环境变量
        os.environ['OPENVIKING_CONFIG_FILE'] = CONFIG_FILE
        
        # 尝试初始化
        client = ov.SyncOpenViking(path="/tmp/openviking_test")
        client.initialize()
        
        print("✅ API 连接测试成功！")
        print("   OpenViking 可以正常使用")
        
        client.close()
        
        # 清理测试目录
        import shutil
        if os.path.exists("/tmp/openviking_test"):
            shutil.rmtree("/tmp/openviking_test")
            
    except Exception as e:
        print(f"❌ API 连接测试失败: {e}")
        print("\n可能的原因:")
        print("  - API Key 无效或已过期")
        print("  - 网络连接问题")
        print("  - API 服务商限制")
        print("\n建议:")
        print("  1. 检查 API Key 是否正确")
        print("  2. 确认账号有足够的额度")
        print("  3. 稍后重试")

def main():
    print_header("OpenViking 自动配置工具")
    
    print("欢迎使用 OpenViking 配置工具！\n")
    print("OpenViking 需要配置 Embedding 和 VLM API 才能使用完整功能。\n")
    
    # 检查现有配置
    if not check_existing_config():
        print("已取消配置")
        return
    
    # 选择配置方式
    print("\n请选择 API 提供商:")
    print("  1. NVIDIA NIM (免费推荐)")
    print("  2. OpenAI API")
    print("  3. 自定义 API")
    print("  4. 退出")
    print()
    
    choice = input("请输入选项 (1-4): ").strip()
    
    success = False
    
    if choice == '1':
        success = setup_nvidia_nim()
    elif choice == '2':
        success = setup_openai()
    elif choice == '3':
        success = setup_custom()
    elif choice == '4':
        print("已退出配置")
        return
    else:
        print("❌ 无效选项")
        return
    
    if success:
        test_config()
        
        print_header("配置完成")
        print("🎉 OpenViking 配置完成！")
        print("\n你可以使用以下命令开始:")
        print("  python3 /root/.openclaw/workspace/skills/openviking/viking.py init")
        print("  python3 /root/.openclaw/workspace/skills/openviking/viking.py info")
    else:
        print("\n❌ 配置未完成，请重试")

if __name__ == "__main__":
    main()
