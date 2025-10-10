from ap.cli_commands.explain import explain
from ap.cli_commands.generate_quiz import generate_quiz_internal
from ap.cli_commands.quiz import quiz


def study(concept: str):
    """
    一键完成学习流程：生成解释文档 -> 创建测验题目 -> 运行交互式测验

    Args:
        concept: 要学习的概念名称
    """
    print(f"开始学习 '{concept}' 的完整流程...")
    print("=" * 50)

    try:
        # 步骤1: 生成解释文档
        print("步骤 1/3: 生成概念解释文档...")
        explain(concept)
        print("步骤 1/3: 完成")
        print()

        # 步骤2: 生成测验题目
        print("步骤 2/3: 生成测验题目...")
        generate_quiz_internal(concept, num_questions=None, mode="auto")
        print("步骤 2/3: 完成")
        print()

        # 步骤3: 运行交互式测验
        print("步骤 3/3: 开始交互式测验...")
        print("=" * 50)
        quiz(concept)

        print()
        print("=" * 50)
        print(f"学习流程完成！'{concept}' 的完整学习已结束。")

    except Exception as e:
        print()
        print("=" * 50)
        print(f"学习流程中断：在处理 '{concept}' 时发生错误。")
        print(f"详细信息: {str(e)}")
        raise