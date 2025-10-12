import json
import re

import typer

from ap.core.concept_map import ConceptMap, slugify
from ap.core.utils import call_deepseek_api


def create_concept_map_prompt(topic: str,
                              existing_concepts: list = None) -> str:
    """创建用于生成学习地图的提示词"""
    existing_concepts_text = ""
    if existing_concepts:
        existing_concepts_text = f"\n\n已存在的概念（请避免重复）：\n{', '.join(existing_concepts)}"
    
    return f"""请为以下主题设计一个符合认知规律的层次化学习结构。

认知规律原则：
1. 🧠 认知负荷理论：将复杂主题分解为3-5个主要学习模块，每个模块包含2-4个核心概念
2. 🔗 知识建构理论：概念之间要有清晰的逻辑递进关系，从基础到应用
3. 📚 布鲁姆分类法：按照记忆→理解→应用→分析的认知层次组织概念
4. 🎯 同类聚合原则：相关概念归为一组，便于形成知识网络

层次化结构要求：
- 第一层：3-5个学习模块（主要知识领域）
- 第二层：每个模块下2-4个核心概念
- 概念粒度：每个概念学习时间30-60分钟
- 命名规范：简洁明确，避免复合词汇

主题: {topic}{existing_concepts_text}

请返回以下JSON格式：
{{
  "main_concept": "主题名称",
  "learning_modules": [
    {{
      "module_name": "模块1名称",
      "description": "模块简要说明",
      "concepts": [
        "概念1",
        "概念2",
        "概念3"
      ]
    }},
    {{
      "module_name": "模块2名称", 
      "description": "模块简要说明",
      "concepts": [
        "概念1",
        "概念2"
      ]
    }}
  ]
}}

示例（Python基础编程）：
{{
  "main_concept": "Python基础编程",
  "learning_modules": [
    {{
      "module_name": "环境与语法基础",
      "description": "建立Python编程的基础环境和语法认知",
      "concepts": [
        "Python环境搭建",
        "变量与数据类型",
        "运算符使用"
      ]
    }},
    {{
      "module_name": "程序控制结构",
      "description": "掌握程序流程控制的核心机制",
      "concepts": [
        "条件判断语句",
        "循环控制语句",
        "异常处理机制"
      ]
    }},
    {{
      "module_name": "函数与模块化",
      "description": "学习代码组织和复用的方法",
      "concepts": [
        "函数定义与调用",
        "模块导入与使用"
      ]
    }}
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
        if 'main_concept' not in map_data or 'learning_modules' not in map_data:
            typer.echo("错误：AI返回的数据结构不完整", err=True)
            raise typer.Exit(1)

        # 展示层次化结构
        typer.echo("📚 生成的层次化学习结构:")
        typer.echo(f"主题: {map_data['main_concept']}")
        
        all_concepts = []
        for module in map_data['learning_modules']:
            typer.echo(f"  📂 {module['module_name']} ({len(module['concepts'])}个概念)")
            typer.echo(f"     {module['description']}")
            for concept in module['concepts']:
                typer.echo(f"     • {concept}")
                all_concepts.append(concept)
            typer.echo("")

        # 处理主概念
        main_concept_name = map_data['main_concept']
        main_concept_id = slugify(main_concept_name)

        # 创建概念地图管理器
        concept_map = ConceptMap()

        # 添加主题到概念地图
        concept_map.add_topic(main_concept_id, main_concept_name)

        # 添加学习模块和概念（层次化存储）
        for module in map_data['learning_modules']:
            module_id = slugify(module['module_name'])
            module_data = {
                "name": module['module_name'],
                "description": module['description'],
                "concepts": {}
            }
            
            # 添加模块
            concept_map.add_module(main_concept_id, module_id, module_data)
            
            # 添加模块内的概念
            for concept_name in module['concepts']:
                concept_id = slugify(concept_name)
                concept_data = {
                    "name": concept_name,
                    "children": [],
                    "status": {
                        "explained": False,
                        "quiz_generated": False
                    },
                    "mastery": {
                        "best_score_percent": -1
                    }
                }
                concept_map.add_concept_to_module(main_concept_id, module_id, concept_id, concept_data)

        # 同时保持扁平化存储（向后兼容）
        for concept_name in all_concepts:
            concept_id = slugify(concept_name)
            concept_data = {
                "name": concept_name,
                "children": [],
                "status": {
                    "explained": False,
                    "quiz_generated": False
                },
                "mastery": {
                    "best_score_percent": -1
                }
            }
            concept_map.add_concept(main_concept_id, concept_id, concept_data)

        # 保存概念地图
        concept_map.save()

        # 显示成功信息
        typer.echo("🗺️  学习地图生成成功！")
        typer.echo("")
        typer.echo(f"主题: {main_concept_name}")
        typer.echo(f"└── 包含 {len(map_data['learning_modules'])} 个学习模块，共 {len(all_concepts)} 个概念:")
        typer.echo("")

        # 按模块层次化显示
        for i, module in enumerate(map_data['learning_modules']):
            is_last_module = i == len(map_data['learning_modules']) - 1
            module_prefix = "└──" if is_last_module else "├──"
            typer.echo(f"    {module_prefix} 📂 {module['module_name']} ({len(module['concepts'])}个概念)")
            typer.echo(f"    {'    ' if is_last_module else '│   '}   {module['description']}")
            
            # 显示模块内的概念
            for j, concept in enumerate(module['concepts']):
                is_last_concept = j == len(module['concepts']) - 1
                concept_prefix = "└──" if is_last_concept else "├──"
                indent = "        " if is_last_module else "│       "
                typer.echo(f"    {indent}{concept_prefix} {concept}")
            
            if not is_last_module:
                typer.echo("    │")

        typer.echo("")
        typer.echo(f"💾 概念地图已保存到: {concept_map.file_path}")
        typer.echo("💡 使用 'ap t' 查看完整学习仪表盘")

    except Exception as e:
        typer.echo(f"错误：生成学习地图时发生异常: {e}", err=True)
        raise typer.Exit(1)
