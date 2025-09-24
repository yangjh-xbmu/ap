#!/usr/bin/env python3
"""
AP CLI - 命令行学习工具
帮助用户通过"提问-生成-测验"循环来学习新概念
"""

import os
import re
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

import typer
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 创建 Typer 应用
app = typer.Typer(help="AP CLI - 命令行学习工具")

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
        typer.echo("❌ 错误：未找到 DEEPSEEK_API_KEY 环境变量", err=True)
        typer.echo("请创建 .env 文件并设置您的 DeepSeek API 密钥", err=True)
        raise typer.Exit(1)
    
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

@app.command("e")
def explain(concept: str):
    """
    生成概念的详细解释文档
    
    Args:
        concept: 要解释的概念名称
    """
    try:
        # 规范化概念名称
        concept_slug = slugify(concept)
        
        # 确保 workspace/explanation 目录存在
        explanation_dir = WORKSPACE_DIR / "explanation"
        explanation_dir.mkdir(parents=True, exist_ok=True)
        
        # 构造输出文件路径
        explanation_file = explanation_dir / f"{concept_slug}.md"
        
        # 构建 Prompt
        prompt = create_explanation_prompt(concept)
        
        typer.echo(f"🤔 正在为 \"{concept}\" 生成解释文档...")
        
        # 获取 DeepSeek 客户端
        client = get_deepseek_client()
        
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
        
        # 写入文件
        explanation_file.write_text(explanation_content, encoding="utf-8")
        
        typer.echo(f"✅ 成功为 \"{concept}\" 生成解释文档，已保存至 {explanation_file}")
        
    except Exception as e:
        typer.echo(f"❌ 生成解释文档时发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

@app.command("g")
def generate_quiz(concept: str):
    """
    根据解释文档生成测验题目
    
    Args:
        concept: 要生成测验的概念名称
    """
    try:
        # 规范化概念名称
        concept_slug = slugify(concept)
        
        # 构造输入文件路径
        explanation_file = WORKSPACE_DIR / "explanation" / f"{concept_slug}.md"

        # 检查文件是否存在
        if not explanation_file.exists():
            typer.secho(f"❌ 错误: 未找到 '{concept}' 的解释文档。", err=True)
            typer.secho(f"请先运行 'ap e \"{concept}\"'。", err=True)
            raise typer.Exit(code=1)

        # 读取解释文档内容
        markdown_content = explanation_file.read_text(encoding="utf-8")

        # 构建 Prompt
        prompt = f"""
Based on the following text, please generate 5 multiple-choice questions in YAML format.
Each question must include a 'question' key, an 'options' key (which is a list of 4 strings), and an 'answer' key (which is the exact text of the correct option).

Strictly adhere to the YAML format provided in the example below. Do not include any extra introductory text, explanations, or code block markers (like ```yaml).

---
EXAMPLE:
- question: "What is the 'S' in SOLID?"
  options:
    - "Single Responsibility Principle"
    - "Software Lifecycle"
    - "System Design"
    - "Simple Object"
  answer: "Single Responsibility Principle"
---

Here is the text to base the questions on:

{markdown_content}
"""
        typer.echo(f"🤔 正在为 \"{concept}\" 生成测验题目...")

        # 获取 DeepSeek 客户端
        client = get_deepseek_client()

        # 调用 API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )

        # 获取并清洗生成的内容
        quiz_content = response.choices[0].message.content
        quiz_content = quiz_content.strip().replace("```yaml", "").replace("```", "").strip()

        # 确保 workspace/quizzes 目录存在
        quizzes_dir = WORKSPACE_DIR / "quizzes"
        quizzes_dir.mkdir(parents=True, exist_ok=True)
        
        # 构造输出文件路径
        quiz_file = quizzes_dir / f"{concept_slug}.yml"

        # 写入文件
        quiz_file.write_text(quiz_content, encoding="utf-8")

        typer.echo(f"✅ 成功: '{concept}' 的测验已生成在 {quiz_file}")

    except typer.Exit as e:
        raise e
    except Exception as e:
        typer.echo(f"❌ 生成测验时发生错误: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command("q")
def quiz(concept: str):
    """
    开始交互式测验
    
    Args:
        concept: 要进行测验的概念名称
    """
    try:
        # 规范化概念名称
        concept_slug = slugify(concept)
        
        # 构造输入文件路径
        quiz_file = WORKSPACE_DIR / "quizzes" / f"{concept_slug}.yml"
        
        # 检查文件是否存在
        if not quiz_file.exists():
            typer.secho(f"错误: 未找到 '{concept}' 的测验文件。", err=True)
            typer.secho(f"请先运行 'ap g \"{concept}\"'。", err=True)
            raise typer.Exit(code=1)
        
        # 读取并解析 YAML 文件
        try:
            with open(quiz_file, 'r', encoding='utf-8') as f:
                questions = yaml.safe_load(f)
        except yaml.YAMLError as e:
            typer.secho(f"错误: YAML 文件格式不正确: {str(e)}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
            typer.secho(f"错误: 无法读取测验文件: {str(e)}", err=True)
            raise typer.Exit(code=1)
        
        # 验证文件格式
        if not isinstance(questions, list) or not questions:
            typer.secho("错误: 测验文件格式不正确，应包含问题列表。", err=True)
            raise typer.Exit(code=1)
        
        # 验证每个问题的格式
        for i, q in enumerate(questions):
            if not isinstance(q, dict) or not all(key in q for key in ['question', 'options', 'answer']):
                typer.secho(f"错误: 第 {i+1} 题格式不正确，缺少必要的键。", err=True)
                raise typer.Exit(code=1)
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                typer.secho(f"错误: 第 {i+1} 题应包含4个选项。", err=True)
                raise typer.Exit(code=1)
        
        typer.echo(f"开始 '{concept}' 的测验！共 {len(questions)} 题")
        typer.echo("=" * 50)
        
        # 记录测验结果
        results = []
        correct_count = 0
        
        # 遍历问题进行测验
        for i, question in enumerate(questions, 1):
            typer.echo(f"\n问题 {i}/{len(questions)}: {question['question']}")
            
            # 显示选项
            for j, option in enumerate(question['options'], 1):
                typer.echo(f"  {j}. {option}")
            
            # 获取用户输入
            while True:
                try:
                    user_input = typer.prompt("\n请选择答案 (1-4)")
                    choice = int(user_input)
                    if 1 <= choice <= 4:
                        break
                    else:
                        typer.echo("请输入 1-4 之间的数字")
                except ValueError:
                    typer.echo("请输入有效的数字")
                except typer.Abort:
                    typer.echo("\n测验已取消")
                    raise typer.Exit(0)
            
            # 判断答案
            user_answer = question['options'][choice - 1]
            correct_answer = question['answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                typer.secho("正确！", fg=typer.colors.GREEN)
                correct_count += 1
            else:
                typer.secho(f"错误，正确答案是：{correct_answer}", fg=typer.colors.RED)
            
            # 记录结果
            results.append({
                "question": question['question'],
                "options": question['options'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })
        
        # 计算并显示最终结果
        total_questions = len(questions)
        accuracy = (correct_count / total_questions) * 100
        
        typer.echo("\n" + "=" * 50)
        typer.echo(f"测验完成！你答对了 {correct_count}/{total_questions} 题，正确率 {accuracy:.1f}%")
        
        # 保存结果到 JSON 文件
        results_dir = WORKSPACE_DIR / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_file = results_dir / f"{concept_slug}_{timestamp}.json"
        
        # 创建结果对象
        quiz_result = {
            "concept": concept,
            "concept_slug": concept_slug,
            "quiz_time": datetime.now().isoformat(),
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "questions": results
        }
        
        # 保存到文件
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(quiz_result, f, ensure_ascii=False, indent=2)
        
        typer.echo(f"测验结果已保存到: {result_file}")
        
    except typer.Exit as e:
        raise e
    except Exception as e:
        typer.echo(f"测验过程中发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()