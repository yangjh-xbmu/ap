### **高效开发任务模板 (Task Template)**

#### 🎯 **1. 任务目标 (Task Goal)**

*（用一句话清晰描述本次任务要达成的最终业务目标）*
> 实现 `ap m <topic>` 命令的多主题学习地图生成功能，支持为指定主题创建结构化学习路径并自动创建相关目录结构。

#### 📝 **2. 前置条件 (Prerequisites)**

*（执行此任务前必须满足的条件）*

- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。
- [ ] Task007 已完成：ConceptMap 类已支持多主题数据结构。
- [ ] DeepSeek API 密钥已正确配置。

#### 💻 **3. 技术规格 (Technical Specifications)**

- **命令接口 (Command Interface):**
  - **命令**: `m`, `map`
  - **参数**: `topic` (字符串, 必需)
  - **示例**: `ap m "Python Programming"`
  - **功能**: 为指定主题生成学习地图并创建目录结构

- **文件结构 (File Structure):**
  - **读写**: `workspace/concept_map.json` (多主题数据结构)
  - **创建**: `workspace/explanation/<topic_id>/` 目录
  - **创建**: `workspace/quizzes/<topic_id>/` 目录
  - **创建**: `workspace/results/<topic_id>/` 目录

- **核心逻辑 (Core Logic):**
    1. **主题ID生成**：
       - 使用 `slugify` 函数将主题名称转换为文件系统安全的ID
       - 例如："Python Programming" → "python-programming"

    2. **学习地图生成**：
       - 调用 DeepSeek API 生成结构化学习路径
       - 解析 JSON 响应并验证数据结构
       - 将概念数据存储到多主题格式中

    3. **目录结构创建**：
       - 自动创建主题相关的三个目录
       - 确保目录权限和路径正确性

    4. **数据更新**：
       - 更新 `concept_map.json` 中的主题信息
       - 更新 `metadata.active_topics` 和 `metadata.last_updated`
       - 保存数据到文件系统

- **API 集成 (API Integration):**
  - 使用现有的 `get_deepseek_client()` 函数
  - 复用现有的 prompt 模板和参数配置
  - 增强 JSON 解析和错误处理逻辑

- **依赖变更 (Dependencies):**
  - 无新增依赖，使用现有的 `typer`、`pathlib`、`json` 等。

#### ✅ **4. 验收标准 (Acceptance Criteria)**

*（一个可执行的、用于验证任务是否完成的清单）*

**命令功能验收：**

- [ ] **命令注册成功**：运行 `ap --help`，输出中应包含 `m, map` 命令。
- [ ] **参数处理正确**：`ap m "Python Programming"` 能够正确解析主题名称。
- [ ] **主题ID生成**：主题名称能够正确转换为文件系统安全的ID。

**数据结构验收：**

- [ ] **多主题格式**：生成的 `concept_map.json` 符合项目规范的多主题结构。
- [ ] **主题信息完整**：新主题包含 `name`、`created_at`、`concepts` 字段。
- [ ] **概念结构正确**：每个概念包含 `name`、`children`、`status`、`mastery` 字段。

**目录创建验收：**

- [ ] **目录自动创建**：执行后自动创建三个主题目录。
- [ ] **路径正确性**：目录路径符合 `workspace/<type>/<topic_id>/` 格式。
- [ ] **权限正确**：创建的目录具有正确的读写权限。

**API 集成验收：**

- [ ] **API 调用成功**：能够成功调用 DeepSeek API 生成学习内容。
- [ ] **JSON 解析正确**：能够正确解析 API 返回的 JSON 数据。
- [ ] **错误处理完善**：API 异常时提供清晰的错误信息。

**元数据验收：**

- [ ] **活跃主题更新**：`metadata.active_topics` 包含新创建的主题。
- [ ] **时间戳更新**：`metadata.last_updated` 反映最新的操作时间。
- [ ] **版本号正确**：数据文件版本号为 "2.0"。

#### ❓ **5. 潜在风险 (Potential Risks)**

*（预判可能遇到的问题）*
> **API 调用风险**：
>
> - DeepSeek API 返回的 JSON 格式可能不稳定或不完整。
> - 网络异常导致 API 调用失败。
> - API 配额限制或认证问题。

> **文件系统风险**：
>
> - 目录创建权限不足。
> - 磁盘空间不足导致文件写入失败。
> - 并发访问导致的文件锁定问题。

> **数据一致性风险**：
>
> - 主题ID冲突（相同名称的主题）。
> - 数据写入过程中的异常导致数据不完整。
> - JSON 格式验证失败。

#### 🔧 **6. 实现建议 (Implementation Tips)**

*（开发过程中的最佳实践建议）*

**重构 generate_map 函数：**

```python
def generate_map(topic_name: str) -> None:
    """为指定主题生成学习地图"""
    try:
        # 1. 生成主题ID
        topic_id = slugify(topic_name)
        
        # 2. 检查主题是否已存在
        concept_map = ConceptMap()
        if concept_map.topic_exists(topic_id):
            typer.echo(f"主题 '{topic_name}' 已存在，使用 'ap t {topic_id}' 查看详情")
            return
        
        # 3. 调用 API 生成学习内容
        client = get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"为 '{topic_name}' 创建学习地图..."}],
            # ... 其他参数
        )
        
        # 4. 解析和验证数据
        concepts_data = json.loads(response.choices[0].message.content)
        validate_concepts_structure(concepts_data)
        
        # 5. 添加主题和概念
        concept_map.add_topic(topic_id, topic_name)
        for concept_id, concept_data in concepts_data.items():
            concept_map.add_concept(topic_id, concept_id, concept_data)
        
        # 6. 创建目录结构
        create_topic_directories(topic_id)
        
        # 7. 保存数据
        concept_map.save()
        
        typer.echo(f"✅ 主题 '{topic_name}' 的学习地图已生成")
        
    except Exception as e:
        typer.echo(f"❌ 生成学习地图失败: {str(e)}")
        raise typer.Exit(1)
```

**目录创建逻辑：**

```python
def create_topic_directories(topic_id: str) -> None:
    """为主题创建相关目录结构"""
    base_path = Path("workspace")
    directories = [
        base_path / "explanation" / topic_id,
        base_path / "quizzes" / topic_id,
        base_path / "results" / topic_id
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        typer.echo(f"📁 创建目录: {directory}")
```

**数据验证策略：**

```python
def validate_concepts_structure(data: dict) -> None:
    """验证概念数据结构的完整性"""
    required_fields = ["name", "children", "status", "mastery"]
    
    for concept_id, concept_data in data.items():
        if not isinstance(concept_data, dict):
            raise ValueError(f"概念 '{concept_id}' 数据格式错误")
        
        for field in required_fields:
            if field not in concept_data:
                raise ValueError(f"概念 '{concept_id}' 缺少必需字段: {field}")
```

**错误处理最佳实践：**

- 使用明确的错误消息和建议操作
- 在关键操作前进行数据备份
- 实现事务性操作，确保数据一致性
- 记录详细的错误日志便于调试
