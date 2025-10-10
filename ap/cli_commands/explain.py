from ap.core.concept_map import ConceptMap, slugify
from ap.core.utils import get_deepseek_client
from ap.core.settings import WORKSPACE_DIR


def create_explanation_prompt(concept: str) -> str:
    """构建生成解释的 Prompt"""
    return f"""请为以下概念生成一份详细的、适合初学者的中文解释文档：

概念：{concept}

文档应包含：
1.  **核心定义**：用简洁的语言解释这个概念是什么。
2.  **关键特征**：列出并解释该概念的主要特点或属性。
3.  **简单类比**：使用一个或多个生活中的例子或类比来帮助理解。
4.  **代码示例**（如果适用）：如果概念与编程相关，提供一个清晰、简洁、可运行的代码示例，并附上详细的注释。
5.  **常见问题**：提出2-3个关于该概念的常见问题，并给出解答。

请使用 Markdown 格式，确保结构清晰、排版整洁。"""


def analyze_document_structure(content: str) -> dict:
    """分析文档结构，返回建议的题目数量"""
    lines = content.split('\n')
    section_count = 0
    subsection_count = 0
    code_blocks = 0
    examples = 0
    
    for line in lines:
        line = line.strip()
        # 统计主要章节（# 和 ##）
        if line.startswith('##'):
            subsection_count += 1
        elif line.startswith('#'):
            section_count += 1
        # 统计代码块
        elif line.startswith('```'):
            code_blocks += 1
        # 统计示例（包含"例如"、"示例"、"Example"等关键词的行）
        elif any(keyword in line.lower() 
                 for keyword in ['例如', '示例', 'example', '举例', '比如']):
            examples += 1
    
    # 计算总知识点数量
    total_knowledge_points = (section_count + subsection_count + 
                              (code_blocks // 2) + examples)
    
    # 基于知识点数量推荐题目数量，确保全覆盖
    if total_knowledge_points <= 5:
        recommended = max(3, total_knowledge_points)
    elif total_knowledge_points <= 10:
        recommended = max(5, total_knowledge_points)
    elif total_knowledge_points <= 20:
        recommended = total_knowledge_points
    elif total_knowledge_points <= 30:
        recommended = total_knowledge_points  # 确保每个知识点都有对应题目
    else:
        # 对于超过30个知识点的内容，也要确保全覆盖
        recommended = total_knowledge_points
    
    return {
        'section_count': total_knowledge_points,  # 返回总知识点数量
        'recommended_questions': recommended,
        'details': {
            'main_sections': section_count,
            'subsections': subsection_count,
            'code_blocks': code_blocks // 2,  # 代码块成对出现
            'examples': examples
        }
    }


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

请严格按照以下YAML格式输出，不要包含任何代码块标记：

- question: "题目内容"
  options:
    A: "选项A"
    B: "选项B" 
    C: "选项C"
    D: "选项D"
  answer: "A"
  explanation: "答案解释"

- question: "题目内容2"
  options:
    A: "选项A"
    B: "选项B"
    C: "选项C" 
    D: "选项D"
  answer: "B"
  explanation: "答案解释"

注意：直接输出YAML内容，不要使用```yaml```代码块包装。"""


def explain(concept: str):
    """
    生成概念的详细解释文档

    Args:
        concept: 要解释的概念名称
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
                raise

        # 构造输出文件路径 - 按主题组织
        explanation_dir = WORKSPACE_DIR / topic_slug / "explanation"
        explanation_dir.mkdir(parents=True, exist_ok=True)

        explanation_file = explanation_dir / f"{concept_slug}.md"

        # 获取 DeepSeek 客户端
        client = get_deepseek_client()

        # 生成解释内容
        print(f"🤔 正在为 \"{concept}\" 生成解释文档...")

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

        print(f"成功为 \"{concept}\" 生成解释文档，已保存至 {explanation_file}")

    except Exception as e:
        print(f"生成解释文档时发生错误: {str(e)}")
        raise
