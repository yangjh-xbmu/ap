### **高效开发任务模板 (Task Template) - Task004**

#### 🎯 **1. 任务目标 (Task Goal)**

*（用一句话清晰描述本次任务要达成的最终业务目标）*
> 实现 `ap s <concept>` 命令，用于一键完成概念学习的完整流程：生成解释文档(e)、创建测验题目(g)、运行交互式测验(q)。

#### 📝 **2. 前置条件 (Prerequisites)**

*（执行此任务前必须满足的条件）*

- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。
- [ ] `ap e`、`ap g`、`ap q` 命令均已实现并正常工作。

#### 💻 **3. 技术规格 (Technical Specifications)**

- **命令接口 (Command Interface):**
  - **命令**: `s`, `study`
  - **参数**: `concept` (字符串, 必需)
  - **功能**: `ap s "Python装饰器"`

- **文件结构 (File Structure):**
  - **生成**: `workspace/explanation/<concept>.md`
  - **生成**: `workspace/quizzes/<concept>.yml`
  - **生成**: `workspace/results/<concept>_<timestamp>.json`

- **核心逻辑 (Core Logic):**
    1. 在 `ap/cli.py` 中添加 `study` 函数，并注册为 `s` 和 `study` 命令。
    2. 函数接收 `concept` 参数，按顺序执行以下步骤：
        - **步骤1**: 调用 `explain(concept)` 生成概念解释文档
        - **步骤2**: 调用 `generate_quiz(concept)` 生成测验题目
        - **步骤3**: 调用 `quiz(concept)` 运行交互式测验
    3. 每个步骤完成后显示进度信息。
    4. 如果任一步骤失败，停止执行并显示错误信息。
    5. 全部完成后显示总结信息。

- **依赖变更 (Dependencies):**
  - 无新增依赖，复用现有功能。

#### ✅ **4. 验收标准 (Acceptance Criteria)**

*（一个可执行的、用于验证任务是否完成的清单）*

- [ ] **命令注册成功**：运行 `ap --help`，输出中应包含 `s, study` 命令。
- [ ] **完整流程执行**：运行 `ap s "新概念"`，应依次执行以下步骤：
  - [ ] 生成解释文档并显示成功消息
  - [ ] 生成测验题目并显示成功消息  
  - [ ] 启动交互式测验并完成答题
- [ ] **产物验证**：
  - [ ] `workspace/explanation/新概念.md` 文件被创建。
  - [ ] `workspace/quizzes/新概念.yml` 文件被创建。
  - [ ] `workspace/results/新概念_<timestamp>.json` 文件被创建。
- [ ] **错误处理**：如果某个步骤失败，应停止执行并显示清晰的错误信息。
- [ ] **进度显示**：每个步骤完成时应显示进度信息，让用户了解当前执行状态。

#### ❓ **5. 潜在风险 (Potential Risks)**

*（预判可能遇到的问题）*
>
> - 如果解释文档生成失败，后续步骤无法继续执行。
> - 如果测验题目生成失败，用户无法进行测验。
> - 交互式测验过程中用户可能中途退出，需要优雅处理。
> - 整个流程可能耗时较长，需要给用户适当的进度反馈。
> - API 调用失败或网络问题可能导致流程中断。
