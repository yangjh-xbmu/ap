from typing import Optional

import typer

from ap.core.concept_map import ConceptMap, slugify


def display_tree(topic: Optional[str] = typer.Argument(None, help="主题名称（可选）")):
    """显示学习进度树状图"""
    try:
        # 使用多主题ConceptMap
        concept_map = ConceptMap()

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
                concepts = topic_data.get('concepts', {})

                if not concepts and 'children' in topic_data:
                    all_data = concept_map.data
                    concepts = {}
                    for child_id in topic_data.get('children', []):
                        for key, value in all_data.items():
                            if (key != 'topics' and key != 'metadata' and
                                    isinstance(value, dict)):
                                if key == child_id:
                                    concepts[child_id] = value

                stats = calculate_topic_stats_direct(concepts)
                progress_bar = create_progress_bar(stats['progress_percent'])

                topic_name = topic_data.get('name', topic_id)
                if isinstance(topic_name, dict):
                    topic_name = topic_name.get('name', topic_id)

                typer.echo(f"📖 {topic_name}")
                typer.echo(
                    f"   进度: {progress_bar} {stats['progress_percent']:.1f}%"
                )
                typer.echo(
                    f"   概念: {stats['completed_count']}/"
                    f"{stats['total_count']} 已完成"
                )
                typer.echo(f"   掌握度: {stats['avg_mastery']:.1f}%")
                typer.echo()
        except Exception as e:
            typer.echo(f"❌ 获取主题 '{topic_id}' 信息失败: {str(e)}")

    typer.echo("\n💡 使用 'ap t <主题ID>' 查看特定主题的详细信息")


def calculate_topic_stats_direct(concepts: dict) -> dict:
    """直接计算概念统计信息，不依赖topic_data结构"""
    total_count = count_all_concepts(concepts)
    completed_count = count_completed_concepts(concepts)
    total_mastery = sum_all_mastery(concepts)

    if total_count > 0:
        progress_percent = (completed_count / total_count) * 100
        avg_mastery = total_mastery / total_count
    else:
        progress_percent = 0
        avg_mastery = 0

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

    topic_name = topic_data.get('name', topic_id)
    if isinstance(topic_name, dict):
        topic_name = topic_name.get('name', topic_id)

    typer.echo(f"📖 {topic_name}")
    typer.echo("=" * 50)

    concepts = topic_data.get('concepts', {})

    if concepts:
        display_concept_tree(concepts)
    else:
        typer.echo("暂无概念数据")

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
    concepts = topic_data.get('concepts', {})

    if not concepts and 'children' in topic_data:
        concept_map = ConceptMap()
        all_data = concept_map.data

        if 'topics' in all_data and 'default' in all_data['topics']:
            concepts = all_data['topics']['default'].get('concepts', {})
        else:
            concepts = {}
            for child_id in topic_data.get('children', []):
                if child_id in all_data:
                    concepts[child_id] = all_data[child_id]

    total_count = count_all_concepts(concepts)
    completed_count = count_completed_concepts(concepts)
    total_mastery = sum_all_mastery(concepts)

    if total_count > 0:
        progress_percent = (completed_count / total_count) * 100
        avg_mastery = total_mastery / total_count
    else:
        progress_percent = 0
        avg_mastery = 0

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

        status = concept_data.get('status', {})
        mastery = concept_data.get('mastery', {})
        status_icon = get_status_icon(status, mastery)

        score = mastery.get('best_score_percent', -1)
        mastery_text = f" ({score:.0f}%)" if score >= 0 else ""

        typer.echo(
            f"{prefix}{current_prefix}{status_icon} "
            f"{concept_data.get('name', concept_id)}{mastery_text}"
        )

        if concept_data.get('children'):
            display_concept_tree(
                concept_data['children'],
                level + 1,
                prefix + next_prefix
            )
