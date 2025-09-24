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
    将文本转换为适合文件名的格式
    
    Args:
        text: 输入文本
        
    Returns:
        转换后的文件名格式字符串
    """
    # 移除或替换特殊字符
    text = re.sub(r'[^\w\s-]', '', text.strip())
    # 将空格替换为连字符
    text = re.sub(r'[-\s]+', '-', text)
    return text.lower()

def get_deepseek_client() -> OpenAI:
    """
    获取 DeepSeek API 客户端
    
    Returns:
        配置好的 OpenAI 客户端实例
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        typer.echo("错误: 未找到 DEEPSEEK_API_KEY 环境变量", err=True)
        typer.echo("请在 .env 文件中设置您的 DeepSeek API 密钥", err=True)
        raise typer.Exit(1)
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def create_explanation_prompt(concept: str) -> str:
    """
    构建生成解释的 Prompt
    """
    return f"""请为概念 "{concept}" 生成一个详细的解释文档。

请按照以下结构组织内容：

## 简明定义
用1-2句话简洁地定义这个概念。

## 核心思想/原理
详细解释概念的核心思想、工作原理或基本机制。

## 举例说明
提供2-3个具体的例子来说明这个概念的应用。

## 优点
列出使用这个概念的主要优势。

## 缺点
列出可能的局限性或缺点。

## 类比
用一个生活中的类比来帮助理解这个概念。

请确保内容准确、易懂，适合学习者理解。"""

@app.command("e")
def explain(concept: str):
    """
    为指定概念生成解释文档
    
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
        output_file = explanation_dir / f"{concept_slug}.md"
        
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
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(explanation_content)
        
        typer.echo(f"成功为 \"{concept}\" 生成解释文档，已保存至 {output_file}")
        
    except Exception as e:
        typer.echo(f"生成解释时发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

def analyze_document_structure(content: str) -> dict:
    """
    分析Markdown文档结构，计算建议的题目数量
    
    Args:
        content: 文档内容
        
    Returns:
        包含分析结果的字典
    """
    lines = content.split('\n')
    
    # 统计主要章节（## 开头的标题）
    main_sections = []
    code_examples = 0
    has_analogy = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            section_name = line[3:].strip()
            main_sections.append(section_name)
        elif '```' in line or line.startswith('    ') and len(line) > 4:
            code_examples += 1
        elif '类比' in line or '比如' in line or '就像' in line:
            has_analogy = True
    
    # 计算建议题目数量
    base_questions = len(main_sections)  # 每个主要章节至少1题
    
    # 根据内容复杂度调整
    if code_examples > 0:
        base_questions += min(code_examples, 3)  # 代码示例最多加3题
    
    if has_analogy:
        base_questions += 1  # 类比加1题
    
    # 确保在合理范围内
    recommended_questions = max(3, min(12, base_questions))
    
    return {
        'main_sections': main_sections,
        'section_count': len(main_sections),
        'code_examples': code_examples,
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
        
        # 构造测验文件路径
        quiz_file = WORKSPACE_DIR / "quizzes" / f"{concept_slug}.yml"
        
        # 检查测验文件是否存在
        if not quiz_file.exists():
            typer.secho(f"错误: 未找到 '{concept}' 的测验文件。", err=True)
            typer.secho(f"请先运行 'ap g \"{concept}\"'。", err=True)
            raise typer.Exit(code=1)
        
        # 读取测验内容
        with open(quiz_file, 'r', encoding='utf-8') as f:
            quiz_data = yaml.safe_load(f)
        
        if not quiz_data:
            typer.secho("错误: 测验文件格式不正确。", err=True)
            raise typer.Exit(code=1)
        
        # 开始测验
        typer.echo(f"\n🎯 开始 '{concept}' 测验！")
        typer.echo("=" * 50)
        
        correct_count = 0
        total_questions = len(quiz_data)
        
        for i, question_data in enumerate(quiz_data, 1):
            typer.echo(f"\n问题 {i}/{total_questions}:")
            typer.echo(f"📝 {question_data['question']}")
            typer.echo()
            
            # 显示选项
            options = question_data['options']
            option_labels = ['A', 'B', 'C', 'D']
            
            for j, option in enumerate(options):
                typer.echo(f"  {option_labels[j]}. {option}")
            
            # 获取用户答案
            while True:
                user_answer = typer.prompt("\n请选择答案 (A/B/C/D)").upper().strip()
                if user_answer in option_labels:
                    break
                typer.echo("请输入有效的选项 (A/B/C/D)")
            
            # 检查答案
            selected_option = options[option_labels.index(user_answer)]
            correct_answer = question_data['answer']
            
            if selected_option == correct_answer:
                typer.secho("✅ 正确！", fg=typer.colors.GREEN)
                correct_count += 1
            else:
                typer.secho(f"❌ 错误。正确答案是: {correct_answer}", fg=typer.colors.RED)
        
        # 显示最终结果
        typer.echo("\n" + "=" * 50)
        score_percentage = (correct_count / total_questions) * 100
        typer.echo(f"🎉 测验完成！")
        typer.echo(f"📊 得分: {correct_count}/{total_questions} ({score_percentage:.1f}%)")
        
        if score_percentage >= 80:
            typer.secho("🌟 优秀！你对这个概念掌握得很好！", fg=typer.colors.GREEN)
        elif score_percentage >= 60:
            typer.secho("👍 不错！继续加油！", fg=typer.colors.YELLOW)
        else:
            typer.secho("📚 建议复习一下相关内容。", fg=typer.colors.RED)
        
        # 保存测验记录
        save_quiz_record(concept, correct_count, total_questions, score_percentage)
        
    except Exception as e:
        typer.echo(f"进行测验时发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

def save_quiz_record(concept: str, correct: int, total: int, percentage: float):
    """保存测验记录到文件"""
    # 确保结果目录存在
    results_dir = WORKSPACE_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{slugify(concept)}_{timestamp}.json"
    filepath = results_dir / filename
    
    # 准备记录数据
    record = {
        "concept": concept,
        "timestamp": datetime.now().isoformat(),
        "correct_answers": correct,
        "total_questions": total,
        "percentage": percentage
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        typer.echo(f"📊 测验记录已保存到: {filepath}")
    except IOError as e:
        typer.echo(f"警告：无法保存测验记录: {e}", err=True)

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

@app.command("s")
def study(concept: str):
    """
    完整的学习流程：解释 -> 生成测验 -> 开始测验
    
    Args:
        concept: 要学习的概念名称
    """
    try:
        typer.echo(f"🚀 开始学习 '{concept}'...")
        
        # 步骤1: 生成解释
        typer.echo("\n📖 步骤1: 生成解释文档")
        explain(concept)
        
        # 步骤2: 生成测验
        typer.echo("\n📝 步骤2: 生成测验题目")
        generate_quiz(concept, num_questions=None, mode="auto")
        
        # 询问是否立即开始测验
        if typer.confirm("\n🎯 是否立即开始测验？"):
            quiz(concept)
        else:
            typer.echo(f"💡 你可以稍后运行 'ap q \"{concept}\"' 来开始测验。")
            
    except Exception as e:
        typer.echo(f"学习过程中发生错误: {str(e)}", err=True)
        raise typer.Exit(1)

def main():
    """主函数"""
    app()

if __name__ == "__main__":
    main()
