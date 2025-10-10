### **高效开发任务模板 (Task Template)**

#### 🎯 **1. 任务目标 (Task Goal)**

*（用一句话清晰描述本次任务要达成的最终业务目标）*
> 更新现有的 `ap e`、`ap g`、`ap q` 命令，使其完全支持多主题路径格式（`<topic>/<concept>`）并与新的多主题数据结构兼容。

#### 📝 **2. 前置条件 (Prerequisites)**

*（执行此任务前必须满足的条件）*

- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。
- ] Task007 已完成：ConceptMap 类已支持多主题数据结构。
[ - sk008 已完成：`ap m` 命令能够创建多主题学习地图。
[ - 的 `ap e`、`ap g`、`ap q` 命令功能正常。
-
- - 技术规格 (Technical Specifications)**

- 更新 (Command Interface Updates):**
- - : `ap e <topic>/<concept>` - 生成概念解释
- - g**: `ap g <topic>/<concept>` - 生成概念测验
**- **: `ap q <topic>/<concept>` - 执行概念测验
- - 兼容**: 支持旧格式的单概念参数（自动映射到默认主题）
-

**- 更新 (File Path Updates):**

- **解释文档**: `workspace/explanation/<topic>/<concept>.md`
- **测验文件**: `workspace/quizzes/<topic>/<concept>.json`
  - **测验结果**: `workspace/results/<topic>/<concept>_<timestamp>.json`

- **核心逻辑 (Core Logic):**
    1. **路径解析逻辑**：
  - 解析 `<topic>/<concept>` 格式的参数
    - 验证主题和概念是否存在
  - 处理路径中的特殊字符和空格

    2. **向后兼容处理**：
  - 检测旧格式参数（不包含 `/`）
    - 自动映射到默认主题或提示用户选择主题
  - 提供迁移建议和帮助信息

    3. **文件路径管理**：
  - 根据主题和概念生成正确的文件路径
    - 确保目录存在，必要时自动创建
    - 处理文件名的规范化和安全性
-
  - *数据同步更新**：
  - 更新多主题格式的 `concept_map.json`
  - 步学习状态和掌握度信息
- - 据一致性

- 增强 (Error Handling):**
- - 好提示
  - 概念不存在时的建议操作
- 文件路径错误的详细说明

- - 调用失败的降级处理

- **依赖变更 (Dependencies):**

  - 无新增依赖，使用现有的 `typer`、`pathlib`、`json` 等。

#### ✅ **4. 验收标准 (Acceptance Criteria)**

*（一个可执行的、用于验证任务是否完成的清单）*

**路径解析验收：**

- [ ] **多主题格式支持**：`ap e python/variables` 能够正确解析主题和概念。
- [ ] **路径验证**：不存在的主题或概念时提供清晰的错误信息。
- [ ] **特殊字符处理**：包含空格和特殊字符的路径能够正确处理。

**文件操作验收：**

- [ ] **文件路径正确**：生成的文件保存在正确的主题目录下。
- [ ] **目录自动创建**：不存在的主题目录能够自动创建。

- [ ] **文件名规范化**：概念名称正确转换为文件系统安全的名称。

**向后兼容验收：**

- [ ] **旧格式检测**：能够识别旧格式的单概念参数。
- [ ] **兼容性处理**：旧格式参数能够正确映射或提示用户。
>
- - **迁移建议**：为旧格式用户提供升级到新格式的建议。
-
-

**数据同步验收：**

>
- - **状态更新**：命令执行后正确更新 `concept_map.json` 中的状态。
- - **掌握度同步**：测验结果能够正确更新概念的掌握度。
-
- [ ] **时间戳更新**：`metadata.last_updated` 反映最新的操作时间。

>
> -
>
**- 收：**
 --

- - **ap e 功能**：能够为指定主题的概念生成解释文档。
- [ ] **ap g 功能**：能够为指定主题的概念生成测验文件。

- [ ] **ap q 功能**：能够执行指定主题的概念测验并记录结果。
>
-

## -  **5. 潜在风险 (Potential Risks)**

-

*（预判可能遇到的问题）*
> **向后兼容风险**：
>
> -
> - 用户的工作流可能因参数格式变更而中断。
> - 式数据的迁移可能不完整或出错。
> - 用户习惯的改变需要时间适应。

> **路径处理风险**：
>
> - 不同操作系统的路径分隔符差异。

> - 特殊字符在文件系统中的兼容性问题。
> - 路径长度限制和深度限制。

> **数据一致性风险**：
>
> - 多个命令同时操作同一概念时的数据冲突。
> - 文件系统操作失败导致的数据不同步。
> - 并发访问时的数据竞争问题。

#### 🔧 **6. 实现建议 (Implementation Tips)**

*（开发过程中的最佳实践建议）*

**路径解析工具函数：**

```python
def parse_topic_concept_path(path: str) -> tuple[str, str]:
    """解析 topic/concept 格式的路径"""
    if '/' not in path:
        # 向后兼容：旧格式处理
        return handle_legacy_format(path)
    

    parts = path.split('/', 1)
    if len(parts) != 2:
        raise ValueError("路径格式不正确，请使用 'topic/concept' 格式")
    
    topic_id = parts[0].strip()
    concept_id = parts[1].strip()
    
    if not topic_id or not concept_id:
        raise ValueError("主题名称和概念名称不能为空")
    
    return topic_id, concept_id

def handle_legacy_format(concept: str) -> tuple[str, str]:
    """处理旧格式的单概念参数"""
    concept_map = ConceptMap()

    topics = concept_map.list_topics()
    
    if len(topics) == 0:
        raise ValueError("请先使用 'ap m <主题名称>' 创建学习地图")
    elif len(topics) == 1:
        # 只有一个主题，自动使用
        topic_id = list(topics.keys())[0]
        return topic_id, concept

    else:
        # 多个主题，提示用户选择
        topic_list = ', '.join(topics.keys())
        raise ValueError(f"检测到多个主题，请使用 'topic/concept' 格式。可用主题: {topic_list}")
```

**文件路径管理：**

```python
def get_file_path(topic_id: str, concept_id: str, file_type: str) -> Path:
    """获取指定类型的文件路径"""
    base_path = Path("workspace")
    concept_filename = slugify(concept_id)
    
    path_mapping = {
        "explanation": base_path / "explanation" / topic_id / f"{concept_filename}.md",

        "quiz": base_path / "quizzes" / topic_id / f"{concept_filename}.json",
        "result": base_path / "results" / topic_id / f"{concept_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    }
    
    if file_type not in path_mapping:
        raise ValueError(f"不支持的文件类型: {file_type}")
    
    file_path = path_mapping[file_type]
    
    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    return file_path
```

**命令更新模板：**

```python
def explain_concept(path: str) -> None:

    """生成概念解释 (更新版)"""
    try:
        # 1. 解析路径
        topic_id, concept_id = parse_topic_concept_path(path)
        
        # 2. 验证主题和概念存在
        concept_map = ConceptMap()
        validate_topic_concept_exists(concept_map, topic_id, concept_id)
        
        # 3. 生成文件路径
        file_path = get_file_path(topic_id, concept_id, "explanation")
        
        # 4. 调用 API 生成内容
        content = generate_explanation_content(topic_id, concept_id)
        
        # 5. 保存文件
        file_path.write_text(content, encoding='utf-8')

        
        # 6. 更新学习状态
        concept_map.update_status(topic_id, concept_id, "explanation_generated", True)
        concept_map.save()
        
        typer.echo(f"✅ 概念解释已生成: {file_path}")
        

    except ValueError as e:
        typer.echo(f"❌ 参数错误: {str(e)}")
        show_usage_help("explain")
        raise 
typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ 生成失败: {str(e)}")
        raise typer.Exit(1)
```

**验证和错误处理：**

```python
def validate_topic_concept_exists(concept_map: ConceptMap, topic_id: str, concept_id: str) -> None:
    """验证主题和概念是否存在"""
    if not concept_map.topic_exists(topic_id):
        available_topics = ', '.join(concept_map.list_topics().keys())
        raise ValueError(f"主题 '{topic_id}' 不存在。可用主题: {available_topics}")
    

    topic_data = concept_map.get_topic(topic_id)
    if concept_id not in topic_data['concepts']:
        available_concepts = ', '.join(topic_data['concepts'].keys())
        raise 
ValueError(f"概念 '{concept_id}' 在主题 '{topic_id}' 中不存在。可用概念: {available_concepts}")

def show_usage_help(command: str) -> None:
    """显示命令使用帮助"""
    help_text = {
        "explain": "使用方法: ap e <topic>/<concept>\n例如: ap e python/variables",
        "generate": "使用方法: ap g <topic>/<concept>\n例如: ap g python/variables", 
        "quiz": "使用方法: ap q <topic>/<concept>\n例如: ap q python/variables"
    }
    
    if command in help_text:
        typer.echo(f"💡 {help_text[command]}")
```

**测试策略建议：**

- 创建多个测试主题和概念
- 测试各种路径格式和边界情况
- 验证向后兼容性和迁移逻辑
- 检查文件系统操作的正确性
