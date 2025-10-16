#!/usr/bin/env python3
"""
Pre-commit Hook Script for AP CLI
使用LLM判断commit内容，自动更新setup.py中的版本号

使用方法：
1. 将此脚本复制到 .git/hooks/pre-commit
2. 给脚本执行权限：chmod +x .git/hooks/pre-commit
3. 确保.env文件中配置了DEEPSEEK_API_KEY

版本号规则（x.x.x.x格式）：
- 主版本号更新：重大架构变更、破坏性API变更 (1.0.0.0 -> 2.0.0.0)
- 次版本号更新：新增功能、重要功能改进 (1.0.0.0 -> 1.1.0.0)
- 修订版本号更新：Bug修复、小的改进 (1.0.0.0 -> 1.0.1.0)
- 构建号更新：文档更新、注释修改、格式化 (1.0.0.0 -> 1.0.0.1)
- 不更新：仅Git相关文件变更
"""

import re
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径，以便导入ap模块
project_root = Path(__file__).parent.parent if Path(__file__).parent.name == 'hooks' else Path(__file__).parent
sys.path.insert(0, str(project_root))

from ap.core.utils import get_deepseek_client

# 加载环境变量
load_dotenv()


def get_staged_changes():
    """获取暂存区的变更内容"""
    try:
        # 获取暂存的文件列表
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        staged_files = (
            result.stdout.strip().split('\n') if result.stdout.strip() else []
        )

        # 获取暂存的变更内容
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            check=True
        )
        staged_diff = result.stdout

        return staged_files, staged_diff
    except subprocess.CalledProcessError as e:
        print(f"获取Git变更失败: {e}")
        return [], ""


def get_commit_message():
    """获取提交信息"""
    try:
        # 尝试从git commit命令获取提交信息
        result = subprocess.run(
            ["git", "log", "--format=%B", "-n", "1", "HEAD"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # 如果没有提交信息，返回空字符串
        return ""
    except subprocess.CalledProcessError:
        return ""


def analyze_changes_with_llm(client, staged_files, staged_diff, commit_msg=""):
    """使用LLM分析变更内容并判断版本更新类型"""

    # 构建分析提示
    prompt = f"""
请分析以下Git提交的变更内容，判断应该如何更新版本号。

提交信息：{commit_msg if commit_msg else "无"}

变更的文件：
{chr(10).join(staged_files) if staged_files else "无文件变更"}

变更内容：
{staged_diff[:2000] if staged_diff else "无内容变更"}...

请根据以下规则判断版本更新类型：

1. **MAJOR** (主版本号 x.0.0.0)：
   - 重大架构变更
   - 破坏性API变更
   - 完全重写核心功能

2. **MINOR** (次版本号 x.y.0.0)：
   - 新增功能
   - 新增命令或选项
   - 重要功能改进

3. **PATCH** (修订版本号 x.y.z.0)：
   - Bug修复
   - 小的改进
   - 性能优化

4. **BUILD** (构建号 x.y.z.w)：
   - 文档更新（README、注释等）
   - 代码格式化
   - 测试文件更新
   - 配置文件调整

5. **NONE** (不更新版本)：
   - 仅Git相关文件变更（.gitignore等）
   - 临时文件或缓存文件

请只回答以下五个选项之一：MAJOR、MINOR、PATCH、BUILD、NONE
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": "你是一个专业的软件版本管理助手，能够准确判断代码变更对版本号的影响。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.1
        )

        result = response.choices[0].message.content.strip().upper()

        # 验证返回结果
        if result in ["MAJOR", "MINOR", "PATCH", "BUILD", "NONE"]:
            return result
        else:
            print(f"LLM返回了意外的结果: {result}")
            return "NONE"

    except Exception as e:
        print(f"LLM分析失败: {e}")
        return "NONE"


def get_current_version():
    """从setup.py获取当前版本号"""
    setup_path = Path("setup.py")
    if not setup_path.exists():
        print("错误：找不到setup.py文件")
        return None

    content = setup_path.read_text(encoding="utf-8")

    # 匹配版本号
    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)

    print("错误：在setup.py中找不到版本号")
    return None


def increment_version(current_version, update_type):
    """
    根据更新类型递增版本号
    
    版本号格式：x.x.x.x（主版本号.次版本号.修订号.构建号）
    
    更新规则：
    - MAJOR: 主版本号+1，其他归零
    - MINOR: 次版本号+1，修订号和构建号归零
    - PATCH: 修订号+1，构建号归零
    - BUILD: 仅构建号+1（用于文档更新、注释变化等）
    - NONE: 不更新版本号
    """
    if update_type == "NONE":
        return current_version

    try:
        # 解析版本号 - 支持三位和四位格式
        parts = current_version.split(".")
        if len(parts) == 3:
            # 兼容旧的三位格式，自动添加构建号
            major, minor, patch = map(int, parts)
            build = 0
        elif len(parts) == 4:
            # 新的四位格式
            major, minor, patch, build = map(int, parts)
        else:
            print(f"错误：版本号格式不正确: {current_version}")
            return current_version

        if update_type == "MAJOR":
            major += 1
            minor = 0
            patch = 0
            build = 0
        elif update_type == "MINOR":
            minor += 1
            patch = 0
            build = 0
        elif update_type == "PATCH":
            patch += 1
            build = 0
        elif update_type == "BUILD":
            build += 1

        return f"{major}.{minor}.{patch}.{build}"

    except ValueError as e:
        print(f"错误：解析版本号失败: {e}")
        return current_version


def update_setup_py_version(new_version):
    """更新setup.py中的版本号"""
    setup_path = Path("setup.py")
    content = setup_path.read_text(encoding="utf-8")

    # 替换版本号
    new_content = re.sub(
        r'(version\s*=\s*["\'])([^"\']+)(["\'])',
        f'\\g<1>{new_version}\\g<3>',
        content
    )

    if new_content != content:
        setup_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def stage_setup_py():
    """将更新后的setup.py添加到暂存区"""
    try:
        subprocess.run(["git", "add", "setup.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"添加setup.py到暂存区失败: {e}")
        return False


def main():
    """
    Pre-commit Hook 主函数
    
    功能说明：
    1. 获取Git暂存区的变更内容
    2. 使用DeepSeek AI分析变更类型
    3. 根据分析结果自动更新版本号
    4. 支持四位版本号格式 (x.y.z.w)
    5. 智能识别BUILD类型变更（文档、注释等）
    
    版本更新逻辑：
    - MAJOR: 重大架构变更 → x.0.0.0
    - MINOR: 新增功能 → x.y.0.0  
    - PATCH: Bug修复 → x.y.z.0
    - BUILD: 文档更新 → x.y.z.w
    - NONE: 不更新版本号
    """
    print("[INFO] 运行pre-commit hook...")

    # 获取暂存区变更
    staged_files, staged_diff = get_staged_changes()
    if not staged_files and not staged_diff:
        print("[SUCCESS] 没有检测到暂存区变更，跳过版本更新")
        return

    # 获取提交信息
    commit_msg = get_commit_message()

    # 获取DeepSeek客户端
    try:
        client = get_deepseek_client()
    except Exception as e:
        print(f"[WARNING] 无法连接到DeepSeek API: {e}")
        print("跳过版本更新，继续提交...")
        return

    # 使用LLM分析变更
    print("[AI] 使用AI分析变更内容...")
    update_type = analyze_changes_with_llm(client, staged_files, staged_diff, commit_msg)
    print(f"[ANALYSIS] 分析结果：{update_type}")

    if update_type == "NONE":
        print("[SUCCESS] 无需更新版本号")
        return

    # 获取当前版本并更新
    current_version = get_current_version()
    if not current_version:
        return

    new_version = increment_version(current_version, update_type)
    if new_version == current_version:
        print("[SUCCESS] 版本号无变化")
        return

    print(f"[UPDATE] 版本更新：{current_version} -> {new_version}")

    # 更新setup.py并添加到暂存区
    if update_setup_py_version(new_version):
        print("[SUCCESS] setup.py版本号已更新")
        if stage_setup_py():
            print("[SUCCESS] setup.py已添加到暂存区")
        else:
            print("[WARNING] 添加setup.py到暂存区失败")
    else:
        print("[WARNING] 更新setup.py版本号失败")

    print("[COMPLETE] Pre-commit hook执行完成")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Pre-commit hook执行失败: {e}")
        sys.exit(1)
