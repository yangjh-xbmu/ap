### **高效开发任务模板 (Task Template)**

#### 🎯 **1. 任务目标 (Task Goal)**
*（用一句话清晰描述本次任务要达成的最终业务目标）*
> **示例**：实现 `ap g <concept>` 命令，用于根据已生成的解释文档创建一套测验题。

#### 📝 **2. 前置条件 (Prerequisites)**
*（执行此任务前必须满足的条件）*
- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。

#### 💻 **3. 技术规格 (Technical Specifications)**

*   **命令接口 (Command Interface):**
    *   **命令**: `g`, `generate`
    *   **参数**: `concept` (字符串, 必需)
    *   **功能**: `ap g "Python装饰器"`

*   **文件结构 (File Structure):**
    *   **读取**: `workspace/explanation/<concept>.md`
    *   **写入**: `workspace/quizzes/<concept>.yml`

*   **核心逻辑 (Core Logic):**
    1.  在 `ap/cli.py` 中添加 `generate_quiz` 函数，并注册为 `g` 和 `generate` 命令。
    2.  函数接收 `concept` 参数，并找到对应的 `explanation.md` 文件。
    3.  如果文件不存在，打印错误信息并退出。
    4.  读取 `.md` 文件内容，构建一个新的 Prompt，要求 AI 根据文档内容生成5道选择题（包含题目、选项、答案），并以 YAML 格式返回。
    5.  调用 DeepSeek API 获取返回的 YAML 文本。
    6.  将返回的文本保存到 `workspace/quizzes/<concept>.yml` 文件中。

*   **依赖变更 (Dependencies):**
    *   `PyYAML` (如果尚未在 `requirements.txt` 中)。

#### ✅ **4. 验收标准 (Acceptance Criteria)**
*（一个可执行的、用于验证任务是否完成的清单）*
- [ ] **命令注册成功**：运行 `ap --help`，输出中应包含 `g, generate` 命令。
- [ ] **文件查找正确**：运行 `ap g "一个不存在的概念"`，终端应打印明确的错误提示。
- [ ] **功能执行成功**：运行 `ap g "Python装饰器"`，命令成功退出，并打印成功消息。
- [ ] **产物验证**：
    - [ ] `workspace/quizzes/` 目录被创建。
    - [ ] `workspace/quizzes/python装饰器.yml` 文件被创建。
    - [ ] 文件内容是合法的 YAML 格式，并包含至少5道题目。

#### ❓ **5. 潜在风险 (Potential Risks)**
*（预判可能遇到的问题）*
> **示例**：
> *   AI 返回的 YAML 格式可能不稳定，需要做适当的错误处理。
> *   对于非常长的文档，可能会超出 Prompt 的最大长度限制。