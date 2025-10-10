from pathlib import Path
import typer
from ..core.quality_monitor import QualityMonitor

# 直接定义WORKSPACE_DIR，避免导入问题
WORKSPACE_DIR = Path("workspace")


def monitor_quality():
    """显示测验质量监控报告"""
    monitor = QualityMonitor(WORKSPACE_DIR)
    
    # 获取总体统计
    stats = monitor.get_overall_stats()
    
    print("📊 测验质量监控报告")
    print("=" * 60)
    print("📈 总体统计")
    print("  • 总测验数: {}".format(stats['total_quizzes']))
    print("  • 总题目数: {}".format(stats['total_questions']))
    print("  • 平均质量分数: {:.1f}/100".format(stats['avg_quality_score']))
    print("  • 改进次数: {}".format(stats['improvement_count']))
    print("  • 改进率: {:.1f}%".format(stats['improvement_rate']))
    
    # 获取30天趋势
    trends = monitor.get_quality_trends(30)
    print("\n📈 30天质量趋势")
    print("  • 记录数: {}".format(len(trends)))
    if trends:
        avg_score = sum(t['quality_score'] for t in trends) / len(trends)
        print("  • 平均分数: {:.1f}/100".format(avg_score))
        
        # 显示最近5条记录
        print("  • 最近记录:")
        for trend in trends[-5:]:
            date = trend['date']
            score = trend['quality_score']
            improved = "✅" if trend.get('improved', False) else "⭕"
            print("    - {}: {:.1f}/100 {}".format(date, score, improved))
    
    # 获取答案分布分析
    distribution = monitor.get_answer_distribution_analysis()
    print("\n🎯 答案位置分布分析")
    print("  • 总记录数: {}".format(distribution['total_records']))
    expected_prob = distribution['expected_probability']
    print("  • 期望概率: {:.1f}%".format(expected_prob))
    is_uniform = '是' if distribution['is_uniform'] else '否'
    print("  • 符合均匀分布: {}".format(is_uniform))
    print("  • 最大偏差: {:.3f}".format(distribution['max_deviation']))
    
    print("  • 各位置分布:")
    for pos, data in distribution['position_stats'].items():
        print("    - 位置{}: {:.1f}% (偏差: {:+.3f})".format(
            pos, data['probability'], data['deviation']))
    
    # 特别关注选项2
    option2_prob = distribution['position_stats'].get('2', {}).get(
        'probability', 0)
    if option2_prob > 30:  # 如果超过30%则提醒
        print("\n⚠️  选项2概率较高: {:.1f}%".format(option2_prob))
    else:
        print("\n✅ 选项2概率正常: {:.1f}%".format(option2_prob))
    
    print("\n" + "=" * 60)


def show_quality_trends(days: int = 30):
    """显示质量趋势分析"""
    try:
        monitor = QualityMonitor(WORKSPACE_DIR)
        
        # 获取指定天数的趋势数据
        trends = monitor.get_quality_trends(days)
        
        if not trends:
            typer.echo("📈 暂无质量趋势数据")
            return
        
        typer.echo("📈 质量趋势分析 (最近{}天)".format(days))
        typer.echo("=" * 60)
        
        # 显示总体统计
        avg_score = sum(t['quality_score'] for t in trends) / len(trends)
        improved_count = sum(1 for t in trends if t.get('improved', False))
        rate = (improved_count / len(trends)) * 100 if trends else 0
        
        typer.echo("📊 趋势统计")
        typer.echo("  • 总记录数: {}".format(len(trends)))
        typer.echo("  • 平均质量分数: {:.1f}/100".format(avg_score))
        typer.echo("  • 改进记录数: {}".format(improved_count))
        typer.echo("  • 改进率: {:.1f}%".format(rate))
        
        # 显示详细记录
        typer.echo("\n📋 详细记录:")
        display_count = min(15, len(trends))  # 最多显示15条
        for trend in trends[-display_count:]:
            date = trend['date']
            score = trend['quality_score']
            improved = "✅" if trend.get('improved', False) else "⭕"
            topic = trend.get('quiz_topic', '未知主题')[:30]  # 限制长度
            typer.echo("  • {}: {:.1f}/100 {} - {}".format(
                date, score, improved, topic))
        
        if len(trends) > display_count:
            typer.echo("  ... (显示最近{}条，共{}条记录)".format(
                display_count, len(trends)))
        
        typer.echo("\n" + "=" * 60)
        
    except Exception as e:
        typer.echo("❌ 获取质量趋势时出错: {}".format(e), fg=typer.colors.RED)


def show_position_distribution():
    """显示答案位置分布分析"""
    try:
        monitor = QualityMonitor(WORKSPACE_DIR)
        distribution = monitor.get_answer_distribution_analysis()
        
        typer.echo("🎯 答案位置分布分析")
        typer.echo("=" * 60)
        
        # 基本统计
        typer.echo("📊 分布统计")
        typer.echo("  • 总记录数: {}".format(distribution['total_records']))
        expected_prob = distribution['expected_probability']
        typer.echo("  • 期望概率: {:.1f}%".format(expected_prob))
        is_uniform = '是' if distribution['is_uniform'] else '否'
        typer.echo("  • 符合均匀分布: {}".format(is_uniform))
        typer.echo("  • 最大偏差: {:.3f}".format(distribution['max_deviation']))
        
        # 详细位置分布
        typer.echo("\n📋 各位置详细分布:")
        for pos, data in distribution['position_stats'].items():
            prob = data['probability']
            deviation = data['deviation']
            status = "✅" if abs(deviation) < 0.1 else "⚠️"
            typer.echo("  • 位置{}: {:.1f}% (偏差: {:+.3f}) {}".format(
                pos, prob, deviation, status))
        
        # 质量评估
        typer.echo("\n🔍 质量评估:")
        if distribution['is_uniform']:
            typer.echo("  ✅ 答案分布均匀，质量良好")
        else:
            typer.echo("  ⚠️  答案分布不均匀，建议优化")
        
        # 特别关注选项2
        option2_prob = distribution['position_stats'].get('2', {}).get(
            'probability', 0)
        typer.echo("\n🎯 选项2关注度分析:")
        if option2_prob > 30:
            typer.echo("  ⚠️  选项2概率较高: {:.1f}% (建议调整)".format(
                option2_prob))
        elif option2_prob < 15:
            typer.echo("  ⚠️  选项2概率较低: {:.1f}% (建议增加)".format(
                option2_prob))
        else:
            typer.echo("  ✅ 选项2概率正常: {:.1f}%".format(option2_prob))
        
        typer.echo("\n" + "=" * 60)
            
    except Exception as e:
        typer.echo("❌ 获取分布分析时出错: {}".format(e), fg=typer.colors.RED)
