# Task006: 实现学习地图生成功能 (ap m 命令)

### **高效开发任务模板 (Task Template)**

#### 🎯 **1. 任务目标 (Task Goal)**

*（用一句话清晰描述本次任务要达成的最终业务目标）*
> 实现 `ap m <topic>` 命令，用于将宏观主题拆解为结构化学习路径，生成包含所有子概念的学习地图并存储到 `concept_map.json` 文件中。

#### 📝 **2. 前置条件 (Prerequisites)**

*（执行此任务前必须满足的条件）*

- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。
- [ ] DeepSeek API 密钥已正确配置在 `.env` 文件中。
- [ ] `workspace/` 目录结构已创建。

#### 💻 **3. 技术规格 (Technical Specifications)**

- **命令接口 (Command Interface):**
  - **命令**: `m`, `map`
  - **参数**: `topic` (字符串, 必需)
  - **功能**: `ap m "Python Core Syntax"`
  - **别名支持**: 用户可以使用 `ap map "Python Core Syntax"` 作为等价命令

- **文件结构 (File Structure):**
  - **读取**: 无（首次创建）或 `workspace/concept_map.json`（更新现有地图）
  - **写入**: `workspace/concept_map.json`
  - **目录创建**: 确保 `workspace/` 目录存在

- **核心逻辑 (Core Logic):**
    1. **命令注册**: 在 `ap/cli.py` 中添加 `generate_map` 函数，并注册为 `m` 和 `map` 命令。
    2. **输入处理**: 接收 `topic` 参数，使用 slugify 规则转换为概念ID（小写，连字符替换空格和特殊字符）。
    3. **AI 提示设计**: 构建专门的 Prompt，要求 AI 将主题拆解为层级化的子概念结构。
    4. **API 调用**: 调用 DeepSeek API 获取结构化的概念分解结果。
    5. **数据解析**: 解析 AI 返回的结果，构建符合 `concept_map.json` 格式的数据结构。
    6. **文件操作**:
        - 如果 `concept_map.json` 不存在，创建新文件
        - 如果文件存在，合并新概念到现有地图中
        - 保存更新后的完整概念地图

- **数据结构设计**:

    ```json
    {
      "python-core-syntax": {
        "name": "Python Core Syntax",
        "children": [
          "variables-and-data-types",
          "control-flow", 
          "functions-and-scope",
          "data-structures"
        ],
        "status": {
          "explained": false,
          "quiz_generated": false
        },
        "mastery": {
          "best_score_percent": -1
        }
      }
    }
    ```

- **AI Prompt 设计**:

    ```
    请将以下主题拆解为结构化的学习路径。返回一个JSON格式的概念地图，包含主概念和所有子概念。

    要求：
    1. 主概念应该包含核心子概念
    2. 每个子概念应该是独立可学习的知识点
    3. 如有必要，请创立孙概念。
    4. 概念名称要具体明确，避免过于宽泛
    5. 按学习的逻辑顺序排列子概念
    6. 严格按照以下JSON格式返回，不要包含任何额外的解释文字

    主题: {topic}

    返回格式示例：
    {
      "main_concept": "Python Core Syntax",
      "children": [
        "Variables and Data Types",
        "Control Flow",
        "Functions and Scope",
        "Data Structures"
      ]
    }
    ```

- **错误处理**:
  - API 调用失败时的重试机制
  - JSON 解析错误的处理
  - 文件读写权限问题的处理
  - 无效主题输入的验证

- **依赖变更 (Dependencies):**
  - 确保 `json` 模块（Python 内置）
  - 确保 `pathlib` 模块（Python 内置）
  - 确保 `deepseek` 库已在 `requirements.txt` 中
  - 确保 `python-dotenv` 库已在 `requirements.txt` 中

#### ✅ **4. 验收标准 (Acceptance Criteria)**

*（一个可执行的、用于验证任务是否完成的清单）*

- [ ] **命令注册成功**：运行 `ap --help`，输出中应包含 `m, map` 命令及其描述。
- [ ] **参数验证**：运行 `ap m` （无参数），应显示清晰的错误提示要求提供主题。
- [ ] **功能执行成功**：运行 `ap m "Python Core Syntax"`，命令成功退出，并打印成功消息。
- [ ] **文件创建验证**：
  - [ ] `workspace/` 目录被创建（如果不存在）。
  - [ ] `workspace/concept_map.json` 文件被创建。
  - [ ] 文件内容是合法的 JSON 格式。
- [ ] **数据结构验证**：
  - [ ] JSON 包含主概念的完整信息（name, children, status, mastery）。
  - [ ] 所有子概念都有对应的条目。
  - [ ] 概念ID 使用正确的 slugify 格式。
  - [ ] 初始状态设置正确（explained: false, quiz_generated: false, best_score_percent: -1）。
- [ ] **合并功能验证**：
  - [ ] 运行第二个主题 `ap m "JavaScript Basics"`，新概念应添加到现有文件中。
  - [ ] 原有概念数据不应被覆盖。
- [ ] **别名命令验证**：运行 `ap map "Test Topic"`，功能应与 `ap m "Test Topic"` 完全相同。

#### ❓ **5. 潜在风险 (Potential Risks)**

*（预判可能遇到的问题）*
> **技术风险**：
>
> - AI 返回的 JSON 格式可能不稳定，需要做适当的解析错误处理和格式验证。
> - 对于过于复杂或模糊的主题，AI 可能无法生成合理的子概念分解。
> - 概念ID 的 slugify 转换可能产生重复或冲突的标识符。
>
> **业务风险**：
>
> - 用户输入的主题可能过于宽泛（如"编程"），导致生成的学习路径不够具体。
> - 不同用户对同一主题的理解和学习路径偏好可能不同。
>
> **数据风险**：
>
> - `concept_map.json` 文件损坏可能导致整个学习进度丢失。
> - 并发访问可能导致文件写入冲突。

#### 🔧 **6. 实现细节补充 (Implementation Details)**

- **Slugify 函数实现**:

    ```python
    import re
    
    def slugify(text: str) -> str:
        """将文本转换为文件系统友好的标识符"""
        # 转为小写
        text = text.lower()
        # 替换空格和特殊字符为连字符
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        # 去除首尾连字符
        return text.strip('-')
    ```

- **概念地图管理类设计**:

    ```python
    class ConceptMap:
        def __init__(self, file_path: str):
            self.file_path = Path(file_path)
            self.data = self.load()
        
        def load(self) -> dict:
            """加载现有概念地图"""
            
        def save(self) -> None:
            """保存概念地图到文件"""
            
        def add_concept(self, concept_id: str, concept_data: dict) -> None:
            """添加新概念到地图"""
            
        def update_status(self, concept_id: str, status_key: str, value: any) -> None:
            """更新概念状态"""
    ```

- **成功输出示例**:

    ```
    🗺️  学习地图生成成功！
    
    主题: Python Core Syntax
    └── 包含 4 个子概念:
        ├── Variables and Data Types
        ├── Control Flow  
        ├── Functions and Scope
        └── Data Structures
    
    💾 概念地图已保存到: workspace/concept_map.json
    💡 使用 'ap t' 查看完整学习仪表盘
    ```
