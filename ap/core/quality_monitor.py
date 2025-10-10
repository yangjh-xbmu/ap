"""
质量监控模块 - 持续跟踪测验题目质量
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from collections import defaultdict


class QualityMonitor:
    """质量监控器 - 跟踪测验质量数据"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.monitor_dir = workspace_dir / "quality_monitor"
        self.monitor_dir.mkdir(exist_ok=True)
        
        # 数据文件路径
        self.quality_data_file = self.monitor_dir / "quality_data.json"
        self.daily_stats_file = self.monitor_dir / "daily_stats.json"
        
    def record_quiz_quality(self, quiz_topic: str, quality_data: Dict):
        """记录测验质量数据"""
        try:
            # 加载现有数据
            all_data = self._load_quality_data()
            
            # 添加新记录
            record = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'topic': quiz_topic,
                'total_questions': quality_data.get('total_questions', 0),
                'quality_score': quality_data.get('quality_score', 0),
                'answer_distribution': quality_data.get(
                    'answer_distribution', {}),
                'improved': quality_data.get('improved', False),
                'improvement_details': quality_data.get(
                    'improvement_details', {})
            }
            
            all_data.append(record)
            
            # 保存数据
            self._save_quality_data(all_data)
            
            # 更新每日统计
            self._update_daily_stats(record)
            
        except Exception as e:
            print(f"记录质量数据时出错: {e}")
    
    def get_overall_stats(self) -> Dict:
        """获取总体统计信息"""
        try:
            data = self._load_quality_data()
            
            if not data:
                return {
                    'total_quizzes': 0,
                    'total_questions': 0,
                    'avg_quality_score': 0,
                    'improvement_count': 0,
                    'improvement_rate': 0
                }
            
            total_quizzes = len(data)
            total_questions = sum(r.get('total_questions', 0) for r in data)
            avg_score = sum(r.get('quality_score', 0) for r in data) / len(data)
            improvement_count = sum(1 for r in data if r.get('improved', False))
            improvement_rate = (improvement_count / total_quizzes) * 100
            
            return {
                'total_quizzes': total_quizzes,
                'total_questions': total_questions,
                'avg_quality_score': avg_score,
                'improvement_count': improvement_count,
                'improvement_rate': improvement_rate
            }
            
        except Exception as e:
            print(f"获取总体统计时出错: {e}")
            return {}
    
    def get_quality_trends(self, days: int = 30) -> list:
        """获取质量趋势数据"""
        try:
            data = self._load_quality_data()
            
            # 过滤最近N天的数据
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = [
                r for r in data 
                if datetime.fromisoformat(r['timestamp']) >= cutoff_date
            ]
            
            return recent_data
            
        except Exception as e:
            print(f"获取质量趋势时出错: {e}")
            return []
    
    def get_answer_distribution_analysis(self) -> Dict:
        """获取答案分布分析"""
        try:
            data = self._load_quality_data()
            
            if not data:
                return {
                    'total_records': 0,
                    'expected_probability': 25.0,
                    'is_uniform': True,
                    'max_deviation': 0,
                    'position_stats': {}
                }
            
            # 统计所有答案位置
            position_counts = defaultdict(int)
            total_questions = 0
            
            for record in data:
                distribution = record.get('answer_distribution', {})
                for pos, count in distribution.items():
                    position_counts[pos] += count
                    total_questions += count
            
            # 计算概率和偏差
            expected_prob = 25.0  # 4个选项，每个25%
            position_stats = {}
            deviations = []
            
            for pos in ['1', '2', '3', '4']:
                count = position_counts.get(pos, 0)
                probability = (count / total_questions * 100) if total_questions > 0 else 0
                deviation = abs(probability - expected_prob) / 100
                
                position_stats[pos] = {
                    'count': count,
                    'probability': probability,
                    'deviation': deviation
                }
                deviations.append(deviation)
            
            max_deviation = max(deviations) if deviations else 0
            is_uniform = max_deviation <= 0.1  # 10%的偏差阈值
            
            return {
                'total_records': len(data),
                'expected_probability': expected_prob,
                'is_uniform': is_uniform,
                'max_deviation': max_deviation,
                'position_stats': position_stats
            }
            
        except Exception as e:
            print(f"获取答案分布分析时出错: {e}")
            return {}
    
    def generate_monitoring_report(self) -> str:
        """生成监控报告"""
        try:
            stats = self.get_overall_stats()
            trends = self.get_quality_trends(30)
            distribution = self.get_answer_distribution_analysis()
            
            report = []
            report.append("📊 测验质量监控报告")
            report.append("=" * 50)
            report.append("")
            
            # 总体统计
            report.append("📈 总体统计:")
            report.append(f"  总测验数: {stats.get('total_quizzes', 0)}")
            report.append(f"  总题目数: {stats.get('total_questions', 0)}")
            report.append(f"  平均质量分数: {stats.get('avg_quality_score', 0):.1f}/100")
            report.append(f"  改进次数: {stats.get('improvement_count', 0)}")
            report.append(f"  改进率: {stats.get('improvement_rate', 0):.1f}%")
            report.append("")
            
            # 30天趋势
            report.append("📅 30天质量趋势:")
            report.append(f"  记录数: {len(trends)}")
            if trends:
                avg_score = sum(t.get('quality_score', 0) for t in trends) / len(trends)
                report.append(f"  平均分数: {avg_score:.1f}/100")
            report.append("")
            
            # 答案分布分析
            report.append("🎯 答案位置分布分析:")
            report.append(f"  总记录数: {distribution.get('total_records', 0)}")
            expected = distribution.get('expected_probability', 25.0)
            report.append(f"  期望概率: {expected:.1f}%")
            is_uniform = distribution.get('is_uniform', True)
            report.append(f"  符合均匀分布: {'是' if is_uniform else '否'}")
            max_dev = distribution.get('max_deviation', 0)
            report.append(f"  最大偏差: {max_dev:.3f}")
            
            position_stats = distribution.get('position_stats', {})
            for pos in ['1', '2', '3', '4']:
                if pos in position_stats:
                    data = position_stats[pos]
                    prob = data.get('probability', 0)
                    dev = data.get('deviation', 0)
                    report.append(f"  位置{pos}: {prob:.1f}% (偏差: {dev:+.3f})")
            
            # 特别关注选项2
            option2_data = position_stats.get('2', {})
            option2_prob = option2_data.get('probability', 0)
            if option2_prob > 30:
                report.append(f"\n⚠️  选项2概率较高: {option2_prob:.1f}%")
            else:
                report.append(f"\n✅ 选项2概率正常: {option2_prob:.1f}%")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"❌ 生成监控报告时出错: {e}"
    
    def save_monitoring_report(self) -> Path:
        """保存监控报告到文件"""
        try:
            report = self.generate_monitoring_report()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.monitor_dir / f"monitoring_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return report_file
            
        except Exception as e:
            print(f"保存监控报告时出错: {e}")
            return None
    
    def _load_quality_data(self) -> list:
        """加载质量数据"""
        try:
            if self.quality_data_file.exists():
                with open(self.quality_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def _save_quality_data(self, data: list):
        """保存质量数据"""
        try:
            with open(self.quality_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存质量数据时出错: {e}")
    
    def _update_daily_stats(self, record: Dict):
        """更新每日统计"""
        try:
            # 加载现有每日统计
            daily_stats = self._load_daily_stats()
            
            date = record['date']
            if date not in daily_stats:
                daily_stats[date] = {
                    'quiz_count': 0,
                    'total_questions': 0,
                    'total_score': 0,
                    'improvement_count': 0
                }
            
            # 更新统计
            daily_stats[date]['quiz_count'] += 1
            daily_stats[date]['total_questions'] += record.get('total_questions', 0)
            daily_stats[date]['total_score'] += record.get('quality_score', 0)
            if record.get('improved', False):
                daily_stats[date]['improvement_count'] += 1
            
            # 保存更新后的统计
            self._save_daily_stats(daily_stats)
            
        except Exception as e:
            print(f"更新每日统计时出错: {e}")
    
    def _load_daily_stats(self) -> Dict:
        """加载每日统计数据"""
        try:
            if self.daily_stats_file.exists():
                with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def _save_daily_stats(self, stats: Dict):
        """保存每日统计数据"""
        try:
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存每日统计时出错: {e}")