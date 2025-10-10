import yaml
from ap.core.concept_map import ConceptMap, slugify
from ap.core.utils import get_deepseek_client
from ap.core.settings import WORKSPACE_DIR
from ap.cli_commands.explain import (
    analyze_document_structure, create_quiz_prompt
)


def generate_quiz(
    concept: str,
    num_questions: int | None = None,
    mode: str = "auto"
):
    """
    基于解释文档生成测验题目

    Args:
        concept: 要生成测验的概念名称
        num_questions: 题目数量 (可选, 3-12范围)
        mode: 生成模式 (auto/fixed)
    """
    try:
        # 获取概念所属的主题（与 explain 函数保持一致）
        concept_map = ConceptMap()
        
        # 处理概念名称：如果包含主题前缀，只使用概念部分作为文件名（与 explain 函数保持一致）
        if '/' in concept:
            topic_slug, concept_part = concept.split('/', 1)
            concept_slug = slugify(concept_part)
        else:
            concept_slug = slugify(concept)
            # 如果没有提供主题，则需要查找
            topic_slug = concept_map.get_topic_by_concept(concept_slug)
            if not topic_slug:
                print(f"错误：找不到概念 '{concept}' 所属的主题。")
                raise

        # 构造解释文档路径 - 按主题组织
        explanation_file = WORKSPACE_DIR / topic_slug / \
            "explanation" / f"{concept_slug}.md"

        # 检查解释文档是否存在
        if not explanation_file.exists():
            print(f"错误: 未找到 '{concept}' 的解释文档。")
            print(f"请先运行 'ap e \"{concept}\"'。")
            raise FileNotFoundError(f"解释文档不存在: {explanation_file}")

        # 读取解释文档内容
        with open(explanation_file, 'r', encoding='utf-8') as f:
            explanation_content = f.read()

        # 处理题目数量
        if num_questions is not None:
            # 验证题目数量范围，移除上限限制以支持全覆盖
            if num_questions < 3:
                print(
                    f"警告: 题目数量 {num_questions} 少于最小值 3，"
                    f"已自动调整为 3"
                )
                num_questions = max(3, num_questions)
            elif num_questions > 50:
                print(
                    f"警告: 题目数量 {num_questions} 过多，建议不超过50道，"
                    f"但仍将按要求生成"
                )

        # 智能模式：分析文档结构
        if mode == "auto" and num_questions is None:
            analysis = analyze_document_structure(explanation_content)
            recommended = analysis['recommended_questions']
            print(
                f"📊 文档分析: 发现 {analysis['section_count']} 个主要知识点，"
                f"建议生成 {recommended} 道题目"
            )
            num_questions = recommended

        # 确保按主题组织的 quizzes 目录存在
        quizzes_dir = WORKSPACE_DIR / topic_slug / "quizzes"
        quizzes_dir.mkdir(parents=True, exist_ok=True)

        # 构造输出文件路径
        quiz_file = quizzes_dir / f"{concept_slug}.yml"

        # 获取 DeepSeek 客户端
        client = get_deepseek_client()

        # --- 开始健壮性生成循环 ---
        max_retries = 3
        for attempt in range(max_retries):
            print(
                f"⏳ (第 {attempt + 1}/{max_retries} 次尝试) "
                f"为 \"{concept}\" 生成 {num_questions} 道测验题目..."
            )

            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "user", "content": create_quiz_prompt(
                            concept, explanation_content, num_questions)}
                    ],
                    temperature=0.5,
                    max_tokens=4000  # 增加token限制以支持更多题目
                )

                quiz_content = response.choices[0].message.content.strip()

                # 尝试解析YAML，如果成功则跳出循环
                quiz_data = yaml.safe_load(quiz_content)
                if isinstance(quiz_data, list):
                    print("✅ YAML格式正确，继续处理...")
                    break  # 成功解析，跳出循环
                else:
                    raise ValueError("生成的YAML不是一个列表")

            except (yaml.YAMLError, ValueError) as e:
                print(f"⚠️ 第 {attempt + 1} 次尝试生成的内容YAML格式无效: {e}")
                if attempt + 1 == max_retries:
                    print("❌ 达到最大重试次数，生成失败。")
                    raise  # 抛出最终的异常
        # --- 结束健壮性生成循环 ---

        # 解析生成的YAML内容进行质量检查
        try:
            # 导入质量检查器
            from ap.core.quiz_quality_checker import QuizQualityChecker
            quality_checker = QuizQualityChecker()

            # 分析答案分布
            analysis_result = quality_checker.analyze_answer_distribution(
                quiz_data
            )

            if "error" not in analysis_result:
                quality_score = analysis_result.get('quality_score', 0)

                # 如果质量分数低于80，进行静默答案随机化
                if quality_score < 80:
                    shuffled_quiz, _ = quality_checker.shuffle_quiz_answers(
                        quiz_data
                    )

                    # 重新分析随机化后的分布
                    new_analysis = quality_checker.analyze_answer_distribution(
                        shuffled_quiz
                    )

                    # 使用随机化后的数据
                    quiz_data = shuffled_quiz
                    analysis_result = new_analysis

                # 记录到质量监控系统已被移除
                # 质量检查和改进功能保留，但不再记录监控数据

            # 将处理后的数据转换回YAML格式
            quiz_content = yaml.dump(
                quiz_data, default_flow_style=False,
                allow_unicode=True, sort_keys=False
            )

        except Exception:
            pass  # 静默处理质量检查错误

        # 保存到文件
        with open(quiz_file, 'w', encoding='utf-8') as f:
            f.write(quiz_content)

        print(f"✅ 成功: '{concept}' 的 {len(quiz_data)} 道测验题已生成在 {quiz_file}")

    except Exception as e:
        print(f"❌ 生成测验时发生严重错误: {str(e)}")
        raise
