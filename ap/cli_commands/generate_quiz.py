import yaml
import typer
from ap.core.concept_map import ConceptMap, slugify
from ap.core.utils import call_deepseek_with_retry
from ap.core.settings import WORKSPACE_DIR
from ap.cli_commands.explain import analyze_document_structure


def create_quiz_prompt(concept: str, explanation_content: str,
                       num_questions: int) -> str:
    """构建生成测验的 Prompt"""
    return f"""基于以下解释文档，为概念 "{concept}" 生成 {num_questions} 道高质量的选择题。

解释文档内容：
{explanation_content}

要求：
1. 题目应覆盖文档中的关键知识点
2. 每道题有4个选项（A、B、C、D）
3. 只有一个正确答案
4. 选项分布要均匀（避免所有答案都是A或B）
5. 题目难度适中，适合初学者
6. 使用中文

**YAML格式要求（严格遵守）：**
- 使用2个空格缩进，不要使用Tab
- 所有文本内容必须用双引号包围
- 如果文本包含双引号，请使用单引号包围整个文本
- 每个题目之间用空行分隔
- 选项必须严格按照A、B、C、D顺序
- answer字段只能是"A"、"B"、"C"或"D"

请严格按照以下YAML格式输出，不要包含任何代码块标记：

- question: "题目内容"
  options:
    A: "选项A内容"
    B: "选项B内容"
    C: "选项C内容"
    D: "选项D内容"
  answer: "A"
  explanation: "答案解释内容"

- question: "第二道题目内容"
  options:
    A: "选项A内容"
    B: "选项B内容"
    C: "选项C内容"
    D: "选项D内容"
  answer: "B"
  explanation: "答案解释内容"

**重要提醒：**
1. 直接输出YAML内容，不要使用```yaml```代码块包装
2. 确保每个字段都有值，不要留空
3. 所有冒号后面必须有一个空格
4. 检查缩进是否一致（使用2个空格）
5. 确保没有多余的空格或特殊字符

生成 {num_questions} 道题目："""


def generate_quiz_internal(
    concept: str,
    num_questions: int = None,
    mode: str = "auto",
    max_tokens: int = 32768
):
    """
    内部调用版本的生成测验函数，避免typer.Option序列化问题

    Args:
        concept: 要生成测验的概念名称
        num_questions: 指定题目数量（默认为智能分析）
        mode: 生成模式：auto（智能分析）或 fixed（固定模式）
        max_tokens: 最大输出长度（默认32K，最大64K）
    """
    try:
        # 创建概念地图实例
        concept_map = ConceptMap()

        # 处理概念名称
        if '/' in concept:
            topic_slug, concept_part = concept.split('/', 1)
            concept_slug = slugify(concept_part)
        else:
            concept_slug = slugify(concept)
            # 如果没有提供主题，则需要查找
            topic_slug = concept_map.get_topic_by_concept(concept_slug)
            if not topic_slug:
                print(f"错误：找不到概念 '{concept}' 所属的主题。")
                return

        # 构造解释文档路径
        explanation_dir = WORKSPACE_DIR / topic_slug / "explanation"
        explanation_file = explanation_dir / f"{concept_slug}.md"

        if not explanation_file.exists():
            print(f"错误：找不到解释文档 {explanation_file}")
            print("请先运行 'ap e' 命令生成解释文档")
            return

        # 读取解释文档内容
        with open(explanation_file, 'r', encoding='utf-8') as f:
            explanation_content = f.read()

        # 智能分析题目数量
        if num_questions is None and mode == "auto":
            analysis = analyze_document_structure(explanation_content)
            num_questions = analysis['recommended_questions']
            print(
                f"📊 智能分析: 发现 {analysis['section_count']} 个主要知识点，"
                f"建议生成 {num_questions} 道题目"
            )

        # 如果仍然没有指定数量，使用默认值
        if num_questions is None:
            num_questions = 25

        # 确保按主题组织的 quizzes 目录存在
        quizzes_dir = WORKSPACE_DIR / topic_slug / "quizzes"
        quizzes_dir.mkdir(parents=True, exist_ok=True)

        # 构造输出文件路径
        quiz_file = quizzes_dir / f"{concept_slug}.yml"

        # 使用抽象的DeepSeek调用函数（推理模式）
        quiz_content = call_deepseek_with_retry(
            messages=create_quiz_prompt(
                concept, explanation_content, num_questions
            ),
            model="deepseek-reasoner",
            max_tokens=max_tokens,
            max_retries=3,
            base_temperature=0.5
        )

        # 尝试解析YAML
        quiz_data = yaml.safe_load(quiz_content)

        # 验证数据结构
        if not isinstance(quiz_data, list):
            error_type = type(quiz_data).__name__
            raise ValueError(f"生成的内容不是列表格式，而是 {error_type}")

        if len(quiz_data) == 0:
            raise ValueError("生成的题目列表为空")

        # 验证每个题目的结构
        for i, question in enumerate(quiz_data):
            if not isinstance(question, dict):
                raise ValueError(f"第 {i+1} 题不是字典格式")

            required_fields = ['question', 'options', 'answer', 'explanation']
            for field in required_fields:
                if field not in question:
                    raise ValueError(f"第 {i+1} 题缺少必需字段: {field}")

            # 验证选项格式
            options = question.get('options', {})
            if not isinstance(options, dict):
                raise ValueError(f"第 {i+1} 题的选项不是字典格式")

            expected_options = ['A', 'B', 'C', 'D']
            missing_options = [opt for opt in expected_options
                               if opt not in options]
            if missing_options:
                options_str = ', '.join(missing_options)
                raise ValueError(f"第 {i+1} 题缺少选项: {options_str}")

            # 验证答案格式
            answer = question.get('answer', '')
            if answer not in expected_options:
                raise ValueError(
                    f"第 {i+1} 题的答案 '{answer}' 不在有效选项中"
                )

        print(f"✅ YAML格式正确，成功生成 {len(quiz_data)} 道题目")

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


def generate_quiz(
    concept: str,
    num_questions: int = typer.Option(
        None,
        "--num-questions",
        "-n",
        help="指定题目数量（默认为智能分析）",
        min=3,
        max=50
    ),
    mode: str = typer.Option(
        "auto",
        "--mode",
        help="生成模式：auto（智能分析）或 fixed（固定模式）"
    ),
    max_tokens: int = typer.Option(
        32768,
        "--max-tokens",
        help="最大输出长度（默认32K，最大64K）",
        min=1000,
        max=65536
    )
):
    """
    基于解释文档生成测验题目

    Args:
        concept: 要生成测验的概念名称
        num_questions: 题目数量（可选，默认智能分析）
        mode: 生成模式 (auto/fixed，默认auto)
        max_tokens: 最大输出长度（默认32K，最大64K）
    """
    # 调用内部版本，避免typer.Option序列化问题
    return generate_quiz_internal(
        concept=concept,
        num_questions=num_questions,
        mode=mode,
        max_tokens=max_tokens
    )
