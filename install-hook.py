#!/usr/bin/env python3
"""
Pre-commit Hook 安装脚本
自动安装和配置pre-commit hook

使用方法：
python install-hook.py
"""

import os
import shutil
import stat
from pathlib import Path

def install_pre_commit_hook():
    """安装pre-commit hook"""
    
    # 检查是否在Git仓库中
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ 错误：当前目录不是Git仓库")
        print("请在Git仓库根目录下运行此脚本")
        return False
    
    # 创建hooks目录（如果不存在）
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # 源文件和目标文件路径
    source_file = Path("pre-commit-hook.py")
    target_file = hooks_dir / "pre-commit"
    
    # 检查源文件是否存在
    if not source_file.exists():
        print("❌ 错误：找不到pre-commit-hook.py文件")
        return False
    
    try:
        # 复制文件
        shutil.copy2(source_file, target_file)
        print(f"✅ 已复制 {source_file} 到 {target_file}")
        
        # 给hook脚本执行权限
        current_permissions = target_file.stat().st_mode
        target_file.chmod(current_permissions | stat.S_IEXEC)
        print("✅ 已设置执行权限")
        
        # 检查环境变量配置
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text(encoding="utf-8")
            if "DEEPSEEK_API_KEY" in content:
                print("✅ 检测到.env文件中的DEEPSEEK_API_KEY配置")
            else:
                print("⚠️  警告：.env文件中未找到DEEPSEEK_API_KEY")
                print("请确保配置了DeepSeek API密钥")
        else:
            print("⚠️  警告：未找到.env文件")
            print("请创建.env文件并配置DEEPSEEK_API_KEY")
        
        print("\n🎉 Pre-commit hook安装成功！")
        print("\n📋 使用说明：")
        print("1. 现在每次提交时，hook会自动分析变更内容")
        print("2. 根据变更类型自动更新setup.py中的版本号")
        print("3. 如果需要禁用hook，可以使用：git commit --no-verify")
        print("\n🔧 版本更新规则：")
        print("- 主版本号：重大架构变更、破坏性API变更")
        print("- 次版本号：新增功能、重要功能改进")
        print("- 修订版本号：Bug修复、小的改进")
        print("- 不更新：仅文档更新、注释修改")
        
        return True
        
    except Exception as e:
        print(f"❌ 安装失败：{e}")
        return False

def uninstall_pre_commit_hook():
    """卸载pre-commit hook"""
    hooks_dir = Path(".git/hooks")
    target_file = hooks_dir / "pre-commit"
    
    if target_file.exists():
        try:
            target_file.unlink()
            print("✅ Pre-commit hook已卸载")
            return True
        except Exception as e:
            print(f"❌ 卸载失败：{e}")
            return False
    else:
        print("ℹ️  Pre-commit hook未安装")
        return True

def main():
    """主函数"""
    print("🔧 Pre-commit Hook 管理工具")
    print("=" * 40)
    
    while True:
        print("\n请选择操作：")
        print("1. 安装 pre-commit hook")
        print("2. 卸载 pre-commit hook")
        print("3. 退出")
        
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 开始安装pre-commit hook...")
            install_pre_commit_hook()
        elif choice == "2":
            print("\n🗑️  开始卸载pre-commit hook...")
            uninstall_pre_commit_hook()
        elif choice == "3":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()
