#### 🎯 **1. 任务目标 (Task Goal)**

实现 `ap g <concept>` 命令，它能读取指定概念的 Markdown 解释文档，并调用 LLM API 生成一套对应的 YAML 格式测验题。

#### 📝 **2. 前置条件 (Prerequisites)**

- [ ] 项目骨架已按“启动简报”搭建完成。
- [ ] `ap e <concept>` 命令已能成功执行，并至少已生成一个概念的工作区，例如 `workspace/solid-principles/explanation.md`。
- [ ] `requirements.txt` 已包含 `typer`, `openai`, `python-dotenv`，且依赖已安装。

#### 💻 **3. 技术规格 (Technical Specifications)**

- **命令接口 (Command Interface):**
  - **命令**: `g` (在 Typer 中注册)
  - **参数**: `concept` (字符串, 必需)
  - **示例**: `ap g "设计模式"`

- **文件结构 (File Structure):**
  - **读取**: `workspace/explanation/<concept-slug>.md`
  - **写入**: `workspace/quizzes/<concept-slug>.yml`
  - *(注: `<concept-slug>` 是 `concept` 参数经过规范化处理后的文件名，例如 "设计模式" -> "design-model")*

- **核心逻辑 (Core Logic):**
    1. 在 `main.py` 中，定义一个名为 `generate` 的新函数，并使用 `@app.command("g")` 装饰器将其注册为 `g` 命令。
    2. 函数接收 `concept: str` 参数。
    3. **路径处理:**
        - 实现（或复用）一个函数将 `concept` 字符串规范化为 `concept-slug`。
        - 构造输入文件路径：`workspace/explanation/<concept-slug>.md`。
    4. **前置检查:**
        - 检查 `<concept-slug>.md` 文件是否存在。
        - 如果文件不存在，使用 `typer.secho` 打印一条清晰的错误信息（例如：`❌ Error: Explanation for '设计模式' not found. Please run 'ap e "设计模式"' first.`），并以非零状态码退出 (`raise typer.Exit(code=1)`)。
    5. **Prompt 构建:**
        - 读取 `<concept-slug>.md` 的全部内容。
        - 构建一个精确的 Prompt，要求 LLM 基于提供的文本生成 5 个 YAML 格式的选择题。**必须包含格式示例以确保输出稳定**，如下：

          ```python
          prompt = f"""
          Based on the following text, please generate 5 multiple-choice questions in YAML format.
          Each question must include a 'question' key, an 'options' key (which is a list of 4 strings), and an 'answer' key (which is the exact text of the correct option).
        
          Strictly adhere to the YAML format provided in the example below. Do not include any extra introductory text, explanations, or code block markers (like ```yaml).

          ---
          EXAMPLE:
          - question: "What is the 'S' in SOLID?"
            options:
              - "Single Responsibility Principle"
              - "Software Lifecycle"
              - "System Design"
              - "Simple Object"
            answer: "Single Responsibility Principle"
          ---
        
          Here is the text to base the questions on:
        
          {markdown_content}
          """
          ```

    6. **API 调用:** 调用 OpenAI API，将构建好的 Prompt 发送过去。
    7. **文件写入:**
        - 获取 LLM 返回的纯文本内容。
        - 构造输出文件路径：`workspace/quizzes/<concept-slug>.yml`。
        - 将返回的文本直接写入该文件，覆盖旧内容。
    8. **成功反馈:** 向用户打印一条成功的消息，例如：`✅ Success: Quiz for '设计模式' generated at workspace/quizzes/<concept-slug>.yml`。

- **依赖变更 (Dependencies):**
  - 将 `PyYAML` 添加到 `requirements.txt` 文件中，因为后续任务 `ap q` 将需要用它来解析 YAML 文件。

#### ✅ **4. 验收标准 (Acceptance Criteria)**

- [ ] **依赖安装**: `pip install PyYAML` 后，`PyYAML` 出现在 `requirements.txt` 中。
- [ ] **命令注册成功**: 运行 `ap --help`，输出中应能看到 `g` 命令及其帮助信息。
- [ ] **错误处理**: 运行 `ap g "non-existent-concept"`，终端应打印明确的错误提示，且程序正常退出。
- [ ] **功能执行成功**:
  - 先运行 `ap e "Python Decorators"` 确保解释文档存在。
  - 再运行 `ap g "Python Decorators"`，命令应成功退出并打印成功消息。
- [ ] **产物验证**:
  - `workspace/quiz/python-decorators.yml` 文件被成功创建。
  - 用文本编辑器打开 `quiz.yml`，其内容是合法的 YAML 格式。
  - 内容应包含一个问题列表，每个问题都有 `question`, `options`, `answer` 三个键。

#### ❓ **5. 潜在风险 (Potential Risks)**

- **LLM 输出不稳定:** LLM 可能返回非 YAML 格式的文本或包含了额外的解释。初始版本可先假设其输出是完美的，后续可增加对返回内容的清洗和校验逻辑。
- **上下文长度限制:** 如果 `explanation.md` 文件内容过长，可能会超出 LLM 模型的上下文窗口限制，导致 API 调用失败。当前任务可暂不处理此边缘情况。
