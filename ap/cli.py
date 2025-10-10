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
            current_best = self.data[concept_id]['mastery'].get(
                'best_score_percent', -1)
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


def get_concept_topic(concept: str) -> str:
    """
    根据概念名称获取其所属的主题

    Args:
        concept: 概念名称，可能包含主题前缀（如 "主题/概念"）

    Returns:
        主题名称，如果包含主题前缀则直接返回主题部分
    """
    try:
        # 检查是否包含主题前缀（格式：主题/概念）
        if '/' in concept:
            topic_part, concept_part = concept.split('/', 1)
            # 直接返回主题部分，不需要验证是否存在于concept_map中
            return topic_part

        # 如果没有主题前缀，尝试从concept_map中查找
        concept_map = ConceptMap()
        concept_slug = slugify(concept)

        # 检查是否有topics结构
        if 'topics' in concept_map.data:
            # 遍历所有主题，查找包含该概念的主题
            for topic_id, topic_data in concept_map.data['topics'].items():
                if isinstance(topic_data, dict) and 'concepts' in topic_data:
                    # 检查概念名称的各种匹配方式
                    for concept_id, concept_data in topic_data['concepts'].items():
                        if (concept_slug == concept_id or
                            concept_slug == slugify(concept_data.get('name', '')) or
                                concept == concept_data.get('name', '')):
                            return topic_data.get('name', topic_id)

        # 如果找不到，返回默认主题
        return "default"
    except Exception:
        return "default"


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
        # 获取概念所属的主题
        topic = get_concept_topic(concept)
        topic_slug = slugify(topic)

        # 处理概念名称：如果包含主题前缀，只使用概念部分作为文件名
        if '/' in concept:
            _, concept_part = concept.split('/', 1)
            concept_slug = slugify(concept_part)
        else:
            concept_slug = slugify(concept)

        # 构造输出文件路径 - 按主题组织
        explanation_dir = WORKSPACE_DIR / topic_slug / "explanation"
        explanation_dir.mkdir(parents=True, exist_ok=True)

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
    base_questions = max(
        3, min(12, int(len(main_sections) * 1.5) + (len(main_sections) % 2)))

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

请严格按照以下 YAML 格式输出，不要包含任何额外的解释或代码块标记。

重要：为确保答案分布均匀，请在生成题目时自动随机化正确答案的位置。不要让正确答案总是出现在第一个或固定位置。

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
6. 题目应该平衡分布在各个知识点上，避免某个方面过度集中
7. 正确答案应该随机分布在不同位置（A、B、C、D），避免集中在某个选项
8. 每道题的正确答案位置应该是随机的，整体分布应该接近均匀（约25%在每个位置）"""


@app.command("g")
def generate_quiz(
    concept: str,
    num_questions: Optional[int] = typer.Option(
        None, "--num-questions", "-n", help="指定题目数量 (3-12)，默认为智能计算"),
    mode: str = typer.Option(
        "auto", "--mode", help="生成模式：auto(智能) 或 fixed(固定)")
):
    """
    基于解释文档生成测验题目

    Args:
        concept: 要生成测验的概念名称
        num_questions: 题目数量 (可选，3-12范围)
        mode: 生成模式 (auto/fixed)
    """
    try:
        # 获取概念所属的主题（与 explain 函数保持一致）
        topic = get_concept_topic(concept)
        topic_slug = slugify(topic)

        # 处理概念名称：如果包含主题前缀，只使用概念部分作为文件名（与 explain 函数保持一致）
        if '/' in concept:
            _, concept_part = concept.split('/', 1)
            concept_slug = slugify(concept_part)
        else:
            concept_slug = slugify(concept)

        # 构造解释文档路径 - 按主题组织
        explanation_file = WORKSPACE_DIR / topic_slug / \
            "explanation" / f"{concept_slug}.md"

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
                typer.secho(
                    f"警告: 题目数量 {num_questions} 超出建议范围 (3-12)，已自动调整为 {max(3, min(12, num_questions))}。", fg=typer.colors.YELLOW)
                num_questions = max(3, min(12, num_questions))

        # 智能模式：分析文档结构
        if mode == "auto" and num_questions is None:
            analysis = analyze_document_structure(explanation_content)
            recommended = analysis['recommended_questions']
            typer.echo(
                f"📊 文档分析: 发现 {analysis['section_count']} 个主要知识点，建议生成 {recommended} 道题目")
            num_questions = recommended

        # 确保按主题组织的 quizzes 目录存在
        quizzes_dir = WORKSPACE_DIR / topic_slug / "quizzes"
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
                {"role": "user", "content": create_quiz_prompt(
                    concept, explanation_content, num_questions)}
            ],
            temperature=0.5,
            max_tokens=2000  # 增加token限制以支持更多题目
        )

        quiz_content = response.choices[0].message.content.strip()

        # 解析生成的YAML内容进行质量检查
        was_improved = False
        try:
            quiz_data = yaml.safe_load(quiz_content)
            if not isinstance(quiz_data, list):
                raise ValueError("测验数据格式不正确")
            
            # 导入质量检查器
            from ap.core.quiz_quality_checker import QuizQualityChecker
            from ap.core.quality_monitor import QualityMonitor
            quality_checker = QuizQualityChecker()
            
            # 分析答案分布
            analysis_result = quality_checker.analyze_answer_distribution(quiz_data)
            
            if "error" not in analysis_result:
                quality_score = analysis_result.get('quality_score', 0)
                
                # 如果质量分数低于80，进行静默答案随机化
                if quality_score < 80:
                    shuffled_quiz, shuffle_stats = quality_checker.shuffle_quiz_answers(quiz_data)
                    
                    # 重新分析随机化后的分布
                    new_analysis = quality_checker.analyze_answer_distribution(shuffled_quiz)
                    
                    # 使用随机化后的数据
                    quiz_data = shuffled_quiz
                    analysis_result = new_analysis
                    was_improved = True
                
                # 记录到质量监控系统（静默）
                try:
                    monitor = QualityMonitor(WORKSPACE_DIR)
                    # 准备质量数据，包含改进状态和答案分布信息
                    quality_data_with_improvement = {
                        'total_questions': analysis_result.get('total_questions', 0),
                        'quality_score': analysis_result.get('quality_score', 0),
                        'answer_distribution': analysis_result.get('position_probabilities', {}),
                        'improved': was_improved,
                        'improvement_details': analysis_result.get('uniform_distribution_check', {})
                    }
                    monitor.record_quiz_quality(concept, quality_data_with_improvement)
                except Exception:
                    pass  # 静默处理监控错误
                
                # 将处理后的数据转换回YAML格式
                quiz_content = yaml.dump(quiz_data, default_flow_style=False, 
                                       allow_unicode=True, sort_keys=False)
            
        except Exception:
            pass  # 静默处理质量检查错误

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
        # 解析概念名称，提取主题和概念部分
        if '/' in concept:
            topic_part, concept_part = concept.split('/', 1)
            # 获取主题
            topic = get_concept_topic(concept)
            # 使用概念部分作为文件名
            concept_slug = slugify(concept_part)
        else:
            # 获取概念所属的主题
            topic = get_concept_topic(concept)
            # 规范化概念名称
            concept_slug = slugify(concept)

        topic_slug = slugify(topic)

        # 构造输入文件路径 - 按主题组织
        quiz_file = WORKSPACE_DIR / topic_slug / \
            "quizzes" / f"{concept_slug}.yml"

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
        typer.echo(
            f"测验完成！你答对了 {correct_count}/{total_questions} 题，正确率 {accuracy:.1f}%")

        # 保存结果到 JSON 文件 - 按主题组织
        results_dir = WORKSPACE_DIR / topic_slug / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        result_file = results_dir / f"{concept_slug}_{timestamp}.json"

        # 创建结果对象
        quiz_result = {
            "concept": concept,
            "concept_slug": concept_slug,
            "topic": topic,
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

        # 使用新的多主题ConceptMap
        from ap.core.concept_map import ConceptMap as MultiTopicConceptMap
        concept_map = MultiTopicConceptMap()

        # 获取概念所属的主题
        topic = get_concept_topic(concept)
        topic_slug = slugify(topic)

        # 处理概念名称：如果包含主题前缀，只使用概念部分作为概念ID
        if '/' in concept:
            _, concept_part = concept.split('/', 1)
            concept_id = slugify(concept_part)
        else:
            concept_id = slugify(concept)

        # 确保主题存在
        if not concept_map.topic_exists(topic_slug):
            concept_map.add_topic(topic_slug, topic)

        # 确保概念存在于主题中
        existing_concept = concept_map.get_concept(topic_slug, concept_id)
        if not existing_concept:
            concept_map.add_concept(topic_slug, concept_id, {
                "name": concept_part if '/' in concept else concept,
                "children": [],
                "status": {},
                "mastery": {}
            })

        # 更新测验状态
        concept_map.update_status(topic_slug, concept_id, "quiz_taken", True)
        concept_map.update_status(
            topic_slug, concept_id, "last_quiz_time", datetime.now().isoformat())

        # 更新掌握程度
        concept_map.update_mastery(topic_slug, concept_id, accuracy)

        # 保存概念地图
        concept_map.save()

        typer.echo(f"学习进度已更新：{concept} - 掌握程度 {accuracy:.1f}%")

    except typer.Exit as e:
        raise e
    except Exception as e:
        typer.echo(f"测验过程中发生错误: {str(e)}", err=True)
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
        from ap.core.concept_map import ConceptMap, slugify as concept_slugify
        concept_map = ConceptMap()

        # 处理主概念
        main_concept_name = map_data['main_concept']
        main_concept_id = concept_slugify(main_concept_name)
        children_names = map_data['children']

        # 添加主题到概念地图
        concept_map.add_topic(main_concept_id, main_concept_name)

        # 添加子概念到主题中
        for child_name in children_names:
            child_id = concept_slugify(child_name)
            concept_data = {
                "name": child_name,
                "children": [],
                "status": {
                    "explained": False,
                    "quiz_generated": False
                },
                "mastery": {
                    "best_score_percent": -1
                }
            }
            concept_map.add_concept(main_concept_id, child_id, concept_data)

        # 保存概念地图
        concept_map.save()

        # 显示成功信息
        typer.echo("🗺️  学习地图生成成功！")
        typer.echo("")
        typer.echo(f"主题: {main_concept_name}")
        typer.echo(f"└── 包含 {len(children_names)} 个子概念:")

        for i, child in enumerate(children_names):
            prefix = "├──" if i < len(children_names) - 1 else "└──"
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


@app.command("t")
def display_tree(topic: Optional[str] = typer.Argument(None, help="主题名称（可选）")):
    """显示学习进度树状图"""
    try:
        # 导入多主题ConceptMap
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from ap.core.concept_map import ConceptMap as MultiTopicConceptMap

        concept_map = MultiTopicConceptMap()

        if topic is None:
            # 显示全局概览
            display_global_overview(concept_map)
        else:
            # 显示单主题详情
            topic_id = slugify(topic)

            # 检查主题是否存在
            if not concept_map.topic_exists(topic_id):
                typer.echo(f"❌ 主题 '{topic}' 不存在")
                suggest_available_topics(concept_map)
                raise typer.Exit(1)

            display_topic_details(concept_map, topic_id)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ 显示失败: {str(e)}")
        raise typer.Exit(1)


def display_global_overview(concept_map):
    """显示全局概览"""
    typer.echo("📊 学习进度概览")
    typer.echo("=" * 50)

    topics = concept_map.list_topics()
    if not topics:
        typer.echo("暂无学习主题，请使用 'ap m <主题名称>' 创建学习地图")
        return

    for topic_id in topics:
        try:
            topic_data = concept_map.get_topic(topic_id)
            if topic_data:
                # 对于新格式的多主题数据，直接使用topic_data中的concepts
                # 对于迁移的数据，需要从全局数据中获取概念信息
                concepts = topic_data.get('concepts', {})

                # 如果concepts为空但有children，说明是旧格式数据，需要从全局获取
                if not concepts and 'children' in topic_data:
                    # 从全局数据中获取子概念的详细信息
                    all_data = concept_map.data
                    concepts = {}
                    for child_id in topic_data.get('children', []):
                        # 在topics之外查找概念数据（旧格式迁移后的结构）
                        for key, value in all_data.items():
                            if key != 'topics' and key != 'metadata' and isinstance(value, dict):
                                if key == child_id:
                                    concepts[child_id] = value

                stats = calculate_topic_stats_direct(concepts)
                progress_bar = create_progress_bar(stats['progress_percent'])

                # 获取主题名称，处理嵌套的name结构
                topic_name = topic_data.get('name', topic_id)
                if isinstance(topic_name, dict):
                    topic_name = topic_name.get('name', topic_id)

                typer.echo(f"📖 {topic_name}")
                typer.echo(
                    f"   进度: {progress_bar} {stats['progress_percent']:.1f}%")
                typer.echo(
                    f"   概念: {stats['completed_count']}/{stats['total_count']} 已完成")
                typer.echo(f"   掌握度: {stats['avg_mastery']:.1f}%")
                typer.echo()
        except Exception as e:
            typer.echo(f"❌ 获取主题 '{topic_id}' 信息失败: {str(e)}")

    typer.echo(f"\n💡 使用 'ap t <主题ID>' 查看特定主题的详细信息")


def calculate_topic_stats_direct(concepts: dict) -> dict:
    """直接计算概念统计信息，不依赖topic_data结构"""
    total_count = count_all_concepts(concepts)
    completed_count = count_completed_concepts(concepts)
    total_mastery = sum_all_mastery(concepts)

    progress_percent = (completed_count / total_count *
                        100) if total_count > 0 else 0
    avg_mastery = (total_mastery / total_count) if total_count > 0 else 0

    return {
        'total_count': total_count,
        'completed_count': completed_count,
        'progress_percent': progress_percent,
        'avg_mastery': avg_mastery
    }


def display_topic_details(concept_map, topic_id):
    """显示单主题详情"""
    topic_data = concept_map.get_topic(topic_id)
    if not topic_data:
        typer.echo(f"❌ 主题 '{topic_id}' 不存在")
        return

    # 获取主题名称，处理嵌套的name结构
    topic_name = topic_data.get('name', topic_id)
    if isinstance(topic_name, dict):
        topic_name = topic_name.get('name', topic_id)

    typer.echo(f"📖 {topic_name}")
    typer.echo("=" * 50)

    # 获取概念数据
    concepts = topic_data.get('concepts', {})

    # 显示概念树
    if concepts:
        display_concept_tree(concepts)
    else:
        typer.echo("暂无概念数据")

    # 显示统计信息
    stats = calculate_topic_stats_direct(concepts)
    typer.echo("\n📊 学习统计:")
    typer.echo(f"   总概念数: {stats['total_count']}")
    typer.echo(f"   已完成: {stats['completed_count']}")
    typer.echo(f"   完成率: {stats['progress_percent']:.1f}%")
    typer.echo(f"   平均掌握度: {stats['avg_mastery']:.1f}%")


def suggest_available_topics(concept_map):
    """建议可用主题"""
    topics = concept_map.list_topics()
    if topics:
        topic_list = ', '.join(topics)
        typer.echo(f"可用主题: {topic_list}")
    else:
        typer.echo("暂无可用主题，请使用 'ap m <主题名称>' 创建学习地图")


def get_status_icon(status: dict, mastery: dict) -> str:
    """根据学习状态和掌握程度返回对应的状态图标"""
    if not status.get('explained', False):
        return "⚪"  # 未开始
    elif status.get('quiz_taken', False):
        score = mastery.get('best_score_percent', -1)
        if score >= 80:
            return "🟢"  # 已掌握
        elif score >= 60:
            return "🟡"  # 学习中
        else:
            return "🔴"  # 需复习
    elif status.get('quiz_generated', False):
        return "🟡"  # 学习中
    else:
        return "🟡"  # 学习中


def create_progress_bar(percentage: float, width: int = 20) -> str:
    """创建进度条"""
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}]"


def count_all_concepts(concepts: dict) -> int:
    """递归计算所有概念数量"""
    count = 0
    for concept_data in concepts.values():
        count += 1
        if concept_data.get('children'):
            count += count_all_concepts(concept_data['children'])
    return count


def count_completed_concepts(concepts: dict) -> int:
    """递归计算已完成概念数量"""
    count = 0
    for concept_data in concepts.values():
        status = concept_data.get('status', {})
        if status.get('quiz_taken', False):
            count += 1
        if concept_data.get('children'):
            count += count_completed_concepts(concept_data['children'])
    return count


def sum_all_mastery(concepts: dict) -> float:
    """递归计算所有概念的掌握度总和"""
    total = 0.0
    for concept_data in concepts.values():
        mastery = concept_data.get('mastery', {})
        score = mastery.get('best_score_percent', 0)
        if score > 0:
            total += score
        if concept_data.get('children'):
            total += sum_all_mastery(concept_data['children'])
    return total


def calculate_topic_stats(topic_data: dict) -> dict:
    """计算主题统计信息"""
    # 获取概念数据，支持新旧格式
    concepts = topic_data.get('concepts', {})

    # 如果concepts是空的，尝试从children构建概念字典
    if not concepts and 'children' in topic_data:
        # 从当前概念地图中获取所有概念
        from ap.core.concept_map import ConceptMap as MultiTopicConceptMap
        concept_map = MultiTopicConceptMap()
        all_data = concept_map.data

        # 如果是旧格式迁移的数据，直接使用topics下的数据
        if 'topics' in all_data and 'default' in all_data['topics']:
            concepts = all_data['topics']['default'].get('concepts', {})
        else:
            # 构建概念字典
            concepts = {}
            for child_id in topic_data.get('children', []):
                if child_id in all_data:
                    concepts[child_id] = all_data[child_id]

    total_count = count_all_concepts(concepts)
    completed_count = count_completed_concepts(concepts)
    total_mastery = sum_all_mastery(concepts)

    progress_percent = (completed_count / total_count *
                        100) if total_count > 0 else 0
    avg_mastery = (total_mastery / total_count) if total_count > 0 else 0

    return {
        'total_count': total_count,
        'completed_count': completed_count,
        'progress_percent': progress_percent,
        'avg_mastery': avg_mastery
    }


def display_concept_tree(concepts: dict, level: int = 0, prefix: str = "") -> None:
    """递归显示概念树"""
    concept_items = list(concepts.items())
    for i, (concept_id, concept_data) in enumerate(concept_items):
        is_last = i == len(concept_items) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "

        # 状态图标
        status = concept_data.get('status', {})
        mastery = concept_data.get('mastery', {})
        status_icon = get_status_icon(status, mastery)

        # 掌握度显示
        score = mastery.get('best_score_percent', -1)
        mastery_text = f" ({score:.0f}%)" if score >= 0 else ""

        typer.echo(
            f"{prefix}{current_prefix}{status_icon} {concept_data.get('name', concept_id)}{mastery_text}")

        # 递归显示子概念
        if concept_data.get('children'):
            display_concept_tree(
                concept_data['children'],
                level + 1,
                prefix + next_prefix
            )


def main():
    """主函数"""
    app()


if __name__ == "__main__":
    app()
