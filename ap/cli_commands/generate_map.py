import json
import re

import typer

from ap.core.concept_map import ConceptMap, slugify
from ap.core.utils import call_deepseek_api


def create_concept_map_prompt(topic: str,
                              existing_concepts: list = None) -> str:
    """创建用于生成学习地图的提示词"""
    return f"""请将以下主题拆解为结构化的学习路径。返回一个JSON格式的概念地图，包含主概念和所有子概念。

要求：
1. 主概念应该包含核心子概念
2. 每个子概念应该是独立可学习的知识点
3. 如有必要，请创立孙概念
4. 概念名称要具体明确，避免过于宽泛
5. 按学习的逻辑顺序排列子概念
6. 严格按照以下JSON格式返回，不要包含任何额外的解释文字
7. 尽量使用中文创建概念名称

主题: {topic}

返回格式示例：
{{
  "main_concept": "Python核心概念",
  "children": [
    "变量和数据类型",
    "控制流",
    "函数和作用域",
    "数据结构"
  ]
}}"""


def generate_map(topic: str, model: str = "deepseek-chat"):
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
        # 使用抽象的DeepSeek调用函数
        content = call_deepseek_api(
            messages=create_concept_map_prompt(topic),
            model="deepseek-coder",
            system_message=(
                "You are a helpful assistant that generates concept maps."
            ),
            max_tokens=4096,
            temperature=0.7
        )

        # 尝试解析JSON
        try:
            map_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
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
        children_names = map_data['children']

        # 添加主题到概念地图
        concept_map.add_topic(main_concept_id, main_concept_name)

        # 添加子概念到主题中
        for child_name in children_names:
            child_id = slugify(child_name)
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
