#!/usr/bin/env python3
"""
AP CLI - 命令行学习工具
帮助用户通过"提问-生成-测验"循环来学习新概念
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import typer
import yaml
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量 - 从当前工作目录查找 .env 文件
load_dotenv(dotenv_path=Path.cwd() / '.env')

# 创建 Typer 应用
app = typer.Typer(help="AP CLI - 命令行学习工具")

# 工作区目录
WORKSPACE_DIR = Path("workspace")

class ConceptMap:
    """概念地图管理类"""
    
    def __init__(self, file_path: str = None):
        if file_path is None:
            file_path = WORKSPACE_DIR / "concept_map.json"
        self.file_path = Path(file_path)
        self.data = self.load()
    
    def load(self) -> dict:
        """加载现有概念地图"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                typer.echo(f"警告：无法读取概念地图文件 {self.file_path}: {e}", err=True)
                return {}
        return {}
    
    def save(self) -> None:
        """保存概念地图到文件"""
        # 确保目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            typer.echo(f"错误：无法保存概念地图文件 {self.file_path}: {e}", err=True)
            raise typer.Exit(1)
    
    def add_concept(self, concept_id: str, concept_data: dict) -> None:
        """添加新概念到地图"""
        self.data[concept_id] = concept_data
    
    def update_status(self, concept_id: str, status_key: str, value) -> None:
        """更新概念状态"""
        if concept_id in self.data:
            if 'status' not in self.data[concept_id]:
                self.data[concept_id]['status'] = {}
            self.data[concept_id]['status'][status_key] = value
    
    def update_mastery(self, concept_id: str, score_percent: float) -> None:
        """更新概念掌握程度"""
        if concept_id in self.data:
            if 'mastery' not in self.data[concept_id]:
                self.data[concept_id]['mastery'] = {}
            current_best = self.data[concept_id]['mastery'].get('best_score_percent', -1)
            if score_percent > current_best:
                self.data[concept_id]['mastery']['best_score_percent'] = score_percent

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
        typer.echo("错误：未找到 DEEPSEEK_API_KEY 环境变量", err=True)
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
        
        # 获取 DeepSeek 客户端
        client = get_deepseek_client()
        
        # 生成解释内容
        typer.echo(f"🤔 正在为 \"{concept}\" 生成解释文档...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": create_explanation_prompt(concept)}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        explanation_content = response.choices[0].message.content.strip()
        
        # 保存到文件
        with open(explanation_file, 'w', encoding='utf-8') as f:
            f.write(explanation_content)
        
        typer.echo(f"成功为 \"{concept}\" 生成解释文档，已保存至 {explanation_file}")
        
    except Exception as e:
        typer.echo(f"生成解释文档时发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

def analyze_document_structure(content: str) -> dict:
    """
    分析文档结构，计算建议的题目数量
    
    Args:
        content: Markdown文档内容
        
    Returns:
        dict: 包含分析结果的字典
    """
    lines = content.split('\n')
    
    # 统计主要章节（## 标题）
    main_sections = []
    has_code_example = False
    has_analogy = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            section_title = line[3:].strip()
            main_sections.append(section_title)
        elif '```' in line:
            has_code_example = True
        elif any(keyword in line.lower() for keyword in ['类比', 'analogy', '比如', '就像']):
            has_analogy = True
    
    # 计算基础题目数：主要章节数 × 1.5，向上取整
    base_questions = max(3, min(12, int(len(main_sections) * 1.5) + (len(main_sections) % 2)))
    
    # 调整规则
    if has_code_example:
        base_questions += 1
    if has_analogy:
        base_questions += 1
    
    # 确保在合理范围内
    recommended_questions = max(3, min(12, base_questions))
    
    return {
        'main_sections': main_sections,
        'section_count': len(main_sections),
        'has_code_example': has_code_example,
        'has_analogy': has_analogy,
        'recommended_questions': recommended_questions
    }

def create_quiz_prompt(concept: str, explanation_content: str, num_questions: int = None) -> str:
    """
    构建生成测验的 Prompt
    
    Args:
        concept: 概念名称
        explanation_content: 解释文档内容
        num_questions: 题目数量，如果为None则使用智能分析
    """
    # 如果未指定题目数量，进行智能分析
    if num_questions is None:
        analysis = analyze_document_structure(explanation_content)
        num_questions = analysis['recommended_questions']
        sections_info = f"\n文档包含 {analysis['section_count']} 个主要知识点：{', '.join(analysis['main_sections'])}"
    else:
        sections_info = ""
    
    return f"""基于以下关于 "{concept}" 的解释文档，生成 {num_questions} 道选择题。{sections_info}

解释文档内容：
{explanation_content}

请严格按照以下 YAML 格式输出，不要包含任何额外的解释或代码块标记：

- question: "第一题的问题内容"
  options:
    - "选项A"
    - "选项B"
    - "选项C"
    - "选项D"
  answer: "正确答案的完整文本"
- question: "第二题的问题内容"
  options:
    - "选项A"
    - "选项B"
    - "选项C"
    - "选项D"
  answer: "正确答案的完整文本"

要求：
1. 每题必须有4个选项
2. 问题应该测试对概念的理解，而不是记忆细节
3. 答案必须是选项中的完整文本
4. 题目难度适中，既不过于简单也不过于困难
5. 涵盖概念的不同方面，确保每个主要知识点都有对应的题目
6. 题目应该平衡分布在各个知识点上，避免某个方面过度集中"""

@app.command("g")
def generate_quiz(
    concept: str,
    num_questions: Optional[int] = typer.Option(None, "--num-questions", "-n", help="指定题目数量 (3-12)，默认为智能计算"),
    mode: str = typer.Option("auto", "--mode", help="生成模式：auto(智能) 或 fixed(固定)")
):
    """
    基于解释文档生成测验题目
    
    Args:
        concept: 要生成测验的概念名称
        num_questions: 题目数量 (可选，3-12范围)
        mode: 生成模式 (auto/fixed)
    """
    try:
        # 规范化概念名称
        concept_slug = slugify(concept)
        
        # 构造解释文档路径
        explanation_file = WORKSPACE_DIR / "explanation" / f"{concept_slug}.md"
        
        # 检查解释文档是否存在
        if not explanation_file.exists():
            typer.secho(f"错误: 未找到 '{concept}' 的解释文档。", err=True)
            typer.secho(f"请先运行 'ap e \"{concept}\"'。", err=True)
            raise typer.Exit(code=1)
        
        # 读取解释文档内容
        with open(explanation_file, 'r', encoding='utf-8') as f:
            explanation_content = f.read()
        
        # 处理题目数量
        if num_questions is not None:
            # 验证题目数量范围
            if num_questions < 3 or num_questions > 12:
                typer.secho(f"警告: 题目数量 {num_questions} 超出建议范围 (3-12)，已自动调整为 {max(3, min(12, num_questions))}。", fg=typer.colors.YELLOW)
                num_questions = max(3, min(12, num_questions))
        
        # 智能模式：分析文档结构
        if mode == "auto" and num_questions is None:
            analysis = analyze_document_structure(explanation_content)
            recommended = analysis['recommended_questions']
            typer.echo(f"📊 文档分析: 发现 {analysis['section_count']} 个主要知识点，建议生成 {recommended} 道题目")
            num_questions = recommended
        
        # 确保 workspace/quizzes 目录存在
        quizzes_dir = WORKSPACE_DIR / "quizzes"
        quizzes_dir.mkdir(parents=True, exist_ok=True)
        
        # 构造输出文件路径
        quiz_file = quizzes_dir / f"{concept_slug}.yml"
        
        # 获取 DeepSeek 客户端
        client = get_deepseek_client()
        
        # 生成测验内容
        typer.echo(f"🤔 正在为 \"{concept}\" 生成 {num_questions} 道测验题目...")
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": create_quiz_prompt(concept, explanation_content, num_questions)}
            ],
            temperature=0.5,
            max_tokens=2000  # 增加token限制以支持更多题目
        )
        
        quiz_content = response.choices[0].message.content.strip()
        
        # 保存到文件
        with open(quiz_file, 'w', encoding='utf-8') as f:
            f.write(quiz_content)
        
        typer.echo(f"成功: '{concept}' 的测验已生成在 {quiz_file}")
        
    except typer.Exit as e:
        raise e
    except Exception as e:
        typer.echo(f"生成测验时发生错误: {str(e)}", err=True)
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

@app.command("s")
def study(concept: str):
    """
    一键完成学习流程：生成解释文档 -> 创建测验题目 -> 运行交互式测验
    
    Args:
        concept: 要学习的概念名称
    """
    typer.echo(f"开始学习 '{concept}' 的完整流程...")
    typer.echo("=" * 50)
    
    try:
        # 步骤1: 生成解释文档
        typer.echo("步骤 1/3: 生成概念解释文档...")
        explain(concept)
        typer.echo("步骤 1/3: 完成")
        typer.echo()
        
        # 步骤2: 生成测验题目
        typer.echo("步骤 2/3: 生成测验题目...")
        generate_quiz(concept, num_questions=None, mode="auto")
        typer.echo("步骤 2/3: 完成")
        typer.echo()
        
        # 步骤3: 运行交互式测验
        typer.echo("步骤 3/3: 开始交互式测验...")
        typer.echo("=" * 50)
        quiz(concept)
        
        typer.echo()
        typer.echo("=" * 50)
        typer.echo(f"学习流程完成！'{concept}' 的完整学习已结束。")
        
    except typer.Exit as e:
        typer.echo()
        typer.echo("=" * 50)
        typer.echo(f"学习流程中断：在处理 '{concept}' 时发生错误。", err=True)
        raise e
    except Exception as e:
        typer.echo()
        typer.echo("=" * 50)
        typer.echo(f"学习流程失败：{str(e)}", err=True)
        raise typer.Exit(1)

def create_map_prompt(topic: str) -> str:
    """
    创建用于生成学习地图的提示词
    """
    return f"""请将以下主题拆解为结构化的学习路径。返回一个JSON格式的概念地图，包含主概念和所有子概念。

要求：
1. 主概念应该包含核心子概念
2. 每个子概念应该是独立可学习的知识点
3. 如有必要，请创立孙概念
4. 概念名称要具体明确，避免过于宽泛
5. 按学习的逻辑顺序排列子概念
6. 严格按照以下JSON格式返回，不要包含任何额外的解释文字

主题: {topic}

返回格式示例：
{{
  "main_concept": "Python Core Syntax",
  "children": [
    "Variables and Data Types",
    "Control Flow",
    "Functions and Scope",
    "Data Structures"
  ]
}}"""

@app.command("m")
@app.command("map")
def generate_map(topic: str):
    """
    生成学习地图 - 将宏观主题拆解为结构化学习路径
    
    Args:
        topic: 要学习的主题名称，例如 "Python Core Syntax"
    """
    if not topic.strip():
        typer.echo("错误：请提供要学习的主题名称", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"🗺️  正在为主题 '{topic}' 生成学习地图...")
    
    try:
        # 获取 DeepSeek 客户端
        client = get_deepseek_client()
        
        # 创建提示词
        prompt = create_map_prompt(topic)
        
        # 调用 API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 解析响应
        content = response.choices[0].message.content.strip()
        
        # 尝试解析JSON
        try:
            map_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                map_data = json.loads(json_match.group())
            else:
                typer.echo("错误：AI返回的内容不是有效的JSON格式", err=True)
                typer.echo(f"AI返回内容：{content}", err=True)
                raise typer.Exit(1)
        
        # 验证数据结构
        if 'main_concept' not in map_data or 'children' not in map_data:
            typer.echo("错误：AI返回的数据结构不完整", err=True)
            raise typer.Exit(1)
        
        # 创建概念地图管理器
        concept_map = ConceptMap()
        
        # 处理主概念
        main_concept_name = map_data['main_concept']
        main_concept_id = slugify(main_concept_name)
        children_ids = [slugify(child) for child in map_data['children']]
        
        # 添加主概念
        concept_map.add_concept(main_concept_id, {
            "name": main_concept_name,
            "children": children_ids,
            "status": {
                "explained": False,
                "quiz_generated": False
            },
            "mastery": {
                "best_score_percent": -1
            }
        })
        
        # 添加子概念
        for child_name in map_data['children']:
            child_id = slugify(child_name)
            concept_map.add_concept(child_id, {
                "name": child_name,
                "children": [],
                "status": {
                    "explained": False,
                    "quiz_generated": False
                },
                "mastery": {
                    "best_score_percent": -1
                }
            })
        
        # 保存概念地图
        concept_map.save()
        
        # 显示成功信息
        typer.echo("🗺️  学习地图生成成功！")
        typer.echo("")
        typer.echo(f"主题: {main_concept_name}")
        typer.echo(f"└── 包含 {len(map_data['children'])} 个子概念:")
        
        for i, child in enumerate(map_data['children']):
            prefix = "├──" if i < len(map_data['children']) - 1 else "└──"
            typer.echo(f"    {prefix} {child}")
        
        typer.echo("")
        typer.echo(f"💾 概念地图已保存到: {concept_map.file_path}")
        typer.echo("💡 使用 'ap t' 查看完整学习仪表盘")
        
    except Exception as e:
        typer.echo(f"错误：生成学习地图时发生异常: {e}", err=True)
        raise typer.Exit(1)

def main():
    """主入口函数"""
    app()

if __name__ == "__main__":
    main()
