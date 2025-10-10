"""
测验质量检查模块

该模块用于验证AI生成的测验题目质量，确保：
1. 正确答案在各个位置的分布符合均匀随机分布
2. 正确答案为选项2的概率不超过随机分布预期值
3. 提供答案位置随机化功能
4. 生成质量检查报告
"""

import random
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class QuizQualityChecker:
    """测验质量检查器"""
    
    def __init__(self):
        self.expected_probability = 0.25  # 4选1的期望概率
        self.tolerance = 0.1  # 允许的偏差范围
        
    def analyze_answer_distribution(self, quiz_data: List[Dict]) -> Dict:
        """
        分析测验题目中正确答案的位置分布
        
        Args:
            quiz_data: 测验题目数据列表
            
        Returns:
            分析结果字典
        """
        if not quiz_data:
            return {"error": "测验数据为空"}
            
        answer_positions = []
        
        for question in quiz_data:
            if not all(key in question for key in ['question', 'options', 'answer']):
                continue
                
            correct_answer = question['answer']
            options = question['options']
            
            # 找到正确答案在选项中的位置
            try:
                position = options.index(correct_answer) + 1  # 1-based index
                answer_positions.append(position)
            except ValueError:
                # 正确答案不在选项中，记录为错误
                continue
        
        if not answer_positions:
            return {"error": "未找到有效的题目数据"}
            
        # 统计各位置的分布
        position_counts = Counter(answer_positions)
        total_questions = len(answer_positions)
        
        # 计算各位置的概率
        position_probabilities = {
            pos: count / total_questions 
            for pos, count in position_counts.items()
        }
        
        # 检查是否符合均匀分布
        uniform_check = self._check_uniform_distribution(position_probabilities, total_questions)
        
        # 特别检查选项2的概率
        option2_probability = position_probabilities.get(2, 0)
        option2_check = option2_probability <= (self.expected_probability + self.tolerance)
        
        return {
            "total_questions": total_questions,
            "position_counts": dict(position_counts),
            "position_probabilities": position_probabilities,
            "uniform_distribution_check": uniform_check,
            "option2_probability": option2_probability,
            "option2_check_passed": option2_check,
            "quality_score": self._calculate_quality_score(position_probabilities),
            "recommendations": self._generate_recommendations(position_probabilities)
        }
    
    def _check_uniform_distribution(self, probabilities: Dict[int, float], total_questions: int) -> Dict:
        """检查是否符合均匀分布"""
        # 计算卡方检验统计量
        expected_count = total_questions / 4
        chi_square = 0
        
        for position in range(1, 5):
            observed_count = probabilities.get(position, 0) * total_questions
            chi_square += (observed_count - expected_count) ** 2 / expected_count
        
        # 简化的判断：如果所有位置的概率都在期望值±容差范围内，认为符合均匀分布
        is_uniform = all(
            abs(probabilities.get(pos, 0) - self.expected_probability) <= self.tolerance
            for pos in range(1, 5)
        )
        
        return {
            "is_uniform": is_uniform,
            "chi_square": chi_square,
            "deviations": {
                pos: abs(probabilities.get(pos, 0) - self.expected_probability)
                for pos in range(1, 5)
            }
        }
    
    def _calculate_quality_score(self, probabilities: Dict[int, float]) -> float:
        """计算质量分数 (0-100)"""
        # 计算与理想均匀分布的偏差
        total_deviation = sum(
            abs(probabilities.get(pos, 0) - self.expected_probability)
            for pos in range(1, 5)
        )
        
        # 转换为质量分数 (偏差越小，分数越高)
        max_possible_deviation = 4 * self.expected_probability  # 最大可能偏差
        quality_score = max(0, 100 * (1 - total_deviation / max_possible_deviation))
        
        return round(quality_score, 2)
    
    def _generate_recommendations(self, probabilities: Dict[int, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 检查各位置的偏差
        for position in range(1, 5):
            prob = probabilities.get(position, 0)
            deviation = abs(prob - self.expected_probability)
            
            if deviation > self.tolerance:
                if prob > self.expected_probability:
                    recommendations.append(f"位置{position}的正确答案过多 ({prob:.2%})，建议减少")
                else:
                    recommendations.append(f"位置{position}的正确答案过少 ({prob:.2%})，建议增加")
        
        # 特别检查选项2
        option2_prob = probabilities.get(2, 0)
        if option2_prob > self.expected_probability + self.tolerance:
            recommendations.append(f"选项2作为正确答案的频率过高 ({option2_prob:.2%})，建议调整")
        
        if not recommendations:
            recommendations.append("答案分布良好，符合随机分布要求")
            
        return recommendations
    
    def shuffle_quiz_answers(self, quiz_data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        随机化测验题目的答案位置
        
        Args:
            quiz_data: 原始测验数据
            
        Returns:
            (随机化后的测验数据, 随机化统计信息)
        """
        shuffled_quiz = []
        shuffle_stats = {"position_changes": [], "target_distribution": []}
        
        # 预先计算目标分布，确保均匀性
        total_questions = len(quiz_data)
        target_positions = []
        
        # 为每个位置分配大致相等的题目数量
        for position in range(1, 5):
            count = total_questions // 4
            if position <= total_questions % 4:
                count += 1
            target_positions.extend([position] * count)
        
        # 随机打乱目标位置
        random.shuffle(target_positions)
        
        for i, question in enumerate(quiz_data):
            if not all(key in question for key in ['question', 'options', 'answer']):
                shuffled_quiz.append(question)
                continue
            
            original_answer = question['answer']
            original_options = question['options'][:]
            
            # 找到原始正确答案位置
            try:
                original_position = original_options.index(original_answer) + 1
            except ValueError:
                shuffled_quiz.append(question)
                continue
            
            # 获取目标位置
            target_position = target_positions[i] if i < len(target_positions) else random.randint(1, 4)
            
            # 重新排列选项
            new_options = original_options[:]
            random.shuffle(new_options)
            
            # 确保正确答案在目标位置
            if original_answer in new_options:
                current_pos = new_options.index(original_answer)
                target_index = target_position - 1
                
                # 交换位置
                new_options[current_pos], new_options[target_index] = \
                    new_options[target_index], new_options[current_pos]
            
            # 创建新的题目
            shuffled_question = {
                "question": question['question'],
                "options": new_options,
                "answer": original_answer
            }
            
            shuffled_quiz.append(shuffled_question)
            
            # 记录统计信息
            shuffle_stats["position_changes"].append({
                "question_index": i,
                "original_position": original_position,
                "target_position": target_position
            })
        
        # 统计目标分布
        target_counter = Counter(target_positions)
        shuffle_stats["target_distribution"] = dict(target_counter)
        
        return shuffled_quiz, shuffle_stats
    
    def generate_quality_report(self, analysis_result: Dict, concept: str) -> str:
        """生成质量检查报告"""
        report_lines = [
            f"测验质量检查报告 - {concept}",
            "=" * 50,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"📊 基本统计:",
            f"  总题目数: {analysis_result.get('total_questions', 0)}",
            f"  质量分数: {analysis_result.get('quality_score', 0)}/100",
            "",
            f"📍 答案位置分布:",
        ]
        
        position_counts = analysis_result.get('position_counts', {})
        position_probs = analysis_result.get('position_probabilities', {})
        
        for position in range(1, 5):
            count = position_counts.get(position, 0)
            prob = position_probs.get(position, 0)
            expected = self.expected_probability
            status = "✅" if abs(prob - expected) <= self.tolerance else "❌"
            
            report_lines.append(f"  位置{position}: {count}题 ({prob:.1%}) {status}")
        
        report_lines.extend([
            "",
            f"🎯 均匀分布检查:",
            f"  符合均匀分布: {'✅ 是' if analysis_result.get('uniform_distribution_check', {}).get('is_uniform', False) else '❌ 否'}",
            "",
            f"🔍 选项2特别检查:",
            f"  选项2概率: {analysis_result.get('option2_probability', 0):.1%}",
            f"  检查通过: {'✅ 是' if analysis_result.get('option2_check_passed', False) else '❌ 否'}",
            "",
            f"💡 改进建议:",
        ])
        
        recommendations = analysis_result.get('recommendations', [])
        for rec in recommendations:
            report_lines.append(f"  • {rec}")
        
        return "\n".join(report_lines)
    
    def save_quality_report(self, report: str, concept_slug: str, topic_slug: str, workspace_dir: Path):
        """保存质量检查报告"""
        reports_dir = workspace_dir / topic_slug / "quality_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"{concept_slug}_quality_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_file