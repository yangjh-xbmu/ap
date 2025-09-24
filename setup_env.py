#!/usr/bin/env python3
"""
AP CLI 自动化初始化脚本
用于环境配置和验证
"""

import os
import sys
from pathlib import Path
import subprocess

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 10):
        print("❌ 错误：需要Python 3.10或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_virtual_environment():
    """检查虚拟环境"""
    print("🔍 检查虚拟环境...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 虚拟环境已激活")
        return True
    else:
        print("❌ 警告：未检测到虚拟环境")
        return False

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    required_packages = [
        ('typer', 'typer'),
        ('openai', 'openai'), 
        ('python-dotenv', 'dotenv'),
        ('PyYAML', 'yaml')
    ]
    
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {display_name} 已安装")
        except ImportError:
            print(f"❌ {display_name} 未安装")
            return False
    return True

def create_env_file():
    """创建.env文件（如果不存在）"""
    print("🔍 检查环境变量配置...")
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 创建.env文件...")
            env_file.write_text(env_example.read_text(encoding='utf-8'), encoding='utf-8')
            print("✅ .env文件已创建，请编辑并填入您的DeepSeek API密钥")
        else:
            print("❌ 未找到.env.example文件")
            return False
    else:
        print("✅ .env文件已存在")
    
    # 检查API密钥是否配置
    env_content = env_file.read_text(encoding='utf-8')
    if 'your_deepseek_api_key_here' in env_content:
        print("⚠️  警告：请在.env文件中配置您的实际DeepSeek API密钥")
        return False
    
    return True

def create_workspace_directory():
    """创建工作区目录"""
    print("🔍 创建工作区目录...")
    workspace_dir = Path('workspace')
    workspace_dir.mkdir(exist_ok=True)
    print("✅ 工作区目录已创建")
    return True

def test_cli_command():
    """测试CLI命令"""
    print("🔍 测试CLI命令...")
    try:
        result = subprocess.run([sys.executable, 'main.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI命令测试通过")
            return True
        else:
            print(f"❌ CLI命令测试失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI命令测试异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始AP CLI环境初始化和验证...")
    print("=" * 50)
    
    checks = [
        ("Python版本检查", check_python_version),
        ("虚拟环境检查", check_virtual_environment),
        ("依赖包检查", check_dependencies),
        ("环境变量配置", create_env_file),
        ("工作区目录创建", create_workspace_directory),
        ("CLI命令测试", test_cli_command),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name}失败")
    
    print("\n" + "=" * 50)
    print(f"📊 初始化结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 环境初始化完成！您可以开始使用AP CLI了")
        print("\n使用示例:")
        print("  python main.py e \"SOLID Principles\"")
        return True
    else:
        print("⚠️  部分检查未通过，请根据上述提示进行修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
