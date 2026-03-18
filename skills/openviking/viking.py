#!/usr/bin/env python3
"""
OpenViking CLI Wrapper for OpenClaw
提供简单的命令行接口来操作 OpenViking 上下文数据库
"""

import sys
import os
import json

# 激活虚拟环境
VENV_PATH = "/root/.openclaw/workspace/.venv"
activate_script = os.path.join(VENV_PATH, "bin", "activate_this.py")

if os.path.exists(activate_script):
    exec(open(activate_script).read(), {'__file__': activate_script})
else:
    # 手动添加虚拟环境路径
    site_packages = os.path.join(VENV_PATH, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
    if site_packages not in sys.path:
        sys.path.insert(0, site_packages)

try:
    import openviking as ov
except ImportError:
    print("Error: openviking not found. Please run: pip install openviking")
    sys.exit(1)

# 默认数据目录
DEFAULT_DATA_DIR = "/root/.openclaw/workspace/openviking_data"

def get_client():
    """获取 OpenViking 客户端实例"""
    if not os.path.exists(DEFAULT_DATA_DIR):
        os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
    return ov.SyncOpenViking(path=DEFAULT_DATA_DIR)

def cmd_init():
    """初始化 OpenViking 数据库"""
    client = get_client()
    try:
        client.initialize()
        print("✅ OpenViking 数据库初始化成功！")
        print(f"数据目录: {DEFAULT_DATA_DIR}")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_add(file_path):
    """添加文件到索引"""
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    
    client = get_client()
    try:
        result = client.add_resource(path=file_path)
        print(f"✅ 已添加文件: {result}")
        print("正在处理中...")
        client.wait_processed()
        print("✅ 处理完成！")
    except Exception as e:
        print(f"❌ 添加失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_add_dir(dir_path):
    """批量添加目录中的文件"""
    if not os.path.exists(dir_path):
        print(f"❌ 目录不存在: {dir_path}")
        sys.exit(1)
    
    client = get_client()
    count = 0
    try:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    result = client.add_resource(path=file_path)
                    print(f"  📄 {result}")
                    count += 1
                except Exception as e:
                    print(f"  ⚠️ 跳过 {file}: {e}")
        
        if count > 0:
            print(f"\n已添加 {count} 个文件，正在处理...")
            client.wait_processed()
            print("✅ 批量处理完成！")
        else:
            print("没有可索引的文件")
    except Exception as e:
        print(f"❌ 批量添加失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_search(query, limit=5):
    """语义搜索"""
    client = get_client()
    try:
        results = client.find(query, limit=limit)
        if results.resources:
            print(f"\n🔍 搜索: '{query}'\n")
            for i, r in enumerate(results.resources, 1):
                print(f"  {i}. {r.uri}")
                print(f"     相关度: {r.score:.4f}")
                if hasattr(r, 'abstract') and r.abstract:
                    print(f"     摘要: {r.abstract[:100]}...")
                print()
        else:
            print("未找到相关结果")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_ls(uri=None):
    """列出资源"""
    client = get_client()
    try:
        if uri:
            # 列出特定 URI 的子项
            print(f"\n📁 {uri}\n")
            # 这里需要根据 OpenViking API 实现
            print("子资源列表功能待实现")
        else:
            # 列出根目录
            print("\n📚 资源列表\n")
            # 这里需要根据 OpenViking API 实现
            print("请使用 search 命令查找资源")
    except Exception as e:
        print(f"❌ 列出失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_abstract(uri):
    """获取资源摘要"""
    client = get_client()
    try:
        abstract = client.get_abstract(uri)
        print(f"\n📝 {uri}\n")
        print(abstract)
    except Exception as e:
        print(f"❌ 获取摘要失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_read(uri):
    """读取资源全文"""
    client = get_client()
    try:
        content = client.read_resource(uri)
        print(content)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        sys.exit(1)
    finally:
        client.close()

def cmd_info():
    """显示配置信息"""
    print("\nℹ️  OpenViking 信息\n")
    print(f"数据目录: {DEFAULT_DATA_DIR}")
    print(f"Python版本: {sys.version}")
    print(f"OpenViking版本: {ov.__version__ if hasattr(ov, '__version__') else 'unknown'}")
    
    # 检查配置文件
    config_file = os.path.expanduser("~/.openviking/ov.conf")
    if os.path.exists(config_file):
        print(f"配置文件: {config_file} (已存在)")
    else:
        print(f"配置文件: {config_file} (未创建)")
        print("\n提示: 如需使用 embedding 和 VLM 功能，请创建配置文件")

def main():
    if len(sys.argv) < 2:
        print("""
OpenViking CLI for OpenClaw

用法:
  viking.py init                    - 初始化数据库
  viking.py add <file>              - 添加文件到索引
  viking.py add-dir <directory>     - 批量添加目录
  viking.py search <query> [limit]  - 语义搜索
  viking.py ls [uri]                - 列出资源
  viking.py abstract <uri>          - 获取摘要
  viking.py read <uri>              - 读取全文
  viking.py info                    - 显示信息
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "init":
        cmd_init()
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ 请指定文件路径")
            sys.exit(1)
        cmd_add(sys.argv[2])
    elif command == "add-dir":
        if len(sys.argv) < 3:
            print("❌ 请指定目录路径")
            sys.exit(1)
        cmd_add_dir(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ 请指定搜索关键词")
            sys.exit(1)
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        cmd_search(sys.argv[2], limit)
    elif command == "ls":
        uri = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_ls(uri)
    elif command == "abstract":
        if len(sys.argv) < 3:
            print("❌ 请指定资源 URI")
            sys.exit(1)
        cmd_abstract(sys.argv[2])
    elif command == "read":
        if len(sys.argv) < 3:
            print("❌ 请指定资源 URI")
            sys.exit(1)
        cmd_read(sys.argv[2])
    elif command == "info":
        cmd_info()
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'viking.py' 查看帮助")
        sys.exit(1)

if __name__ == "__main__":
    main()
