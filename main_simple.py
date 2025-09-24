#!/usr/bin/env python3
"""
AP CLI - 命令行学习工具
帮助用户通过"提问-生成-测验"循环来学习新概念
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 工作区目录
WORKSPACE_DIR = Path("workspace")

def slugify(text: str) -> str:
    """
    将概念名称转换为文件系统友好的格式
    例如: "SOLID Principles" -> "solid-principles"
    """
    # 转为小写
    text = text.lower()
    # 替换空格和特殊字符为连字符
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    # 去除首尾连字符
    return text.strip('-')

def get_deepseek_client() -> OpenAI:
    """
    获取 DeepSeek API 客户端
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量")
        print("请创建 .env 文件并设置您的 DeepSeek API 密钥")
        sys.exit(1)
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def create_explanation_prompt(concept: str) -> str:
    """
    构建生成解释的 Prompt
    """
    return f"""请为概念 "{concept}" 生成一份详细的 Markdown 格式解释文档。

请严格按照以下结构输出，不要包含任何额外的解释或代码块标记：

# {concept}

## 简明定义 (Core Definition)
[提供概念的核心定义，简洁明了]

## 核心思想/原理 (Core Principles)
[详细解释概念的核心思想和基本原理]

## 举例说明 (Example)
[提供具体的例子来说明概念的应用]

## 优点 (Pros)
[列出使用该概念的优势和好处]

## 缺点 (Cons)
[列出可能的缺点或限制]

## 一个简单的类比 (Analogy)
[用简单易懂的类比来帮助理解概念]

请确保内容准确、全面且易于理解。"""

def explain_concept(concept: str):
    """
    生成概念的详细解释文档
    """
    try:
        # 规范化概念名称
        concept_slug = slugify(concept)
        
        # 创建工作区目录
        WORKSPACE_DIR.mkdir(exist_ok=True)
        
        # 创建概念专用目录
        concept_dir = WORKSPACE_DIR / concept_slug
        concept_dir.mkdir(exist_ok=True)
        
        # 获取 DeepSeek 客户端
        client = get_deepseek_client()
        
        # 构建 Prompt
        prompt = create_explanation_prompt(concept)
        
        print(f"🤔 正在为 \"{concept}\" 生成解释文档...")
        
        # 调用 API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 获取生成的内容
        explanation_content = response.choices[0].message.content
        
        # 保存到文件
        explanation_file = concept_dir / "explanation.md"
        explanation_file.write_text(explanation_content, encoding="utf-8")
        
        print(f"✅ 成功为 \"{concept}\" 生成解释文档，已保存至 {explanation_file}")
        
    except Exception as e:
        print(f"❌ 生成解释文档时发生错误: {str(e)}")
        sys.exit(1)

def show_help():
    """显示帮助信息"""
    print("""
AP CLI - 命令行学习工具

用法:
  python main_simple.py <命令> <概念名称>

命令:
  e, explain    生成概念的详细解释文档
  g, generate   根据解释文档生成测验题目 (开发中)
  q, quiz       开始交互式测验 (开发中)
  h, help       显示此帮助信息

示例:
  python main_simple.py e "SOLID Principles"
  python main_simple.py explain "设计模式"
""")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command in ['h', 'help', '--help', '-h']:
        show_help()
        return
    
    if command in ['e', 'explain']:
        if len(sys.argv) < 3:
            print("❌ 错误：请提供要解释的概念名称")
            print("用法: python main_simple.py e \"概念名称\"")
            return
        
        concept = ' '.join(sys.argv[2:])
        explain_concept(concept)
        return
    
    if command in ['g', 'generate']:
        print("🚧 generate 命令尚未实现")
        return
    
    if command in ['q', 'quiz']:
        print("🚧 quiz 命令尚未实现")
        return
    
    print(f"❌ 未知命令: {command}")
    show_help()

if __name__ == "__main__":
    main()