### **高效开发任务模板 (Task Template)**

#### 🎯 **1. 任务目标 (Task Goal)**

*（用一句话清晰描述本次任务要达成的最终业务目标）*
> 实现 `ap t [topic]` 学习仪表盘命令，提供多主题学习进度的可视化展示和统计分析功能。

#### 📝 **2. 前置条件 (Prerequisites)**

*（执行此任务前必须满足的条件）*

- [ ] 虚拟环境已激活。
- [ ] `requirements.txt` 中的所有依赖已安装。
- [ ] `ap --help` 命令可正常执行。
- [ ] Task007 已完成：ConceptMap 类已支持多主题数据结构。
- [ ] Task008 已完成：`ap m` 命令能够创建多主题学习地图。
- [ ] 存在至少一个主题的测试数据。

#### 💻 **3. 技术规格 (Technical Specifications)**

- **命令接口 (Command Interface):**
  - **命令**: `t`, `tree`, `status`
  - **参数**: `topic` (字符串, 可选)
  - **示例1**: `ap t` (显示所有主题概览)
  - **示例2**: `ap t python` (显示指定主题详情)

- **显示模式 (Display Modes):**
  - **全局概览模式**: 显示所有主题的学习统计
  - **单主题详情模式**: 显示指定主题的概念树和进度

- **核心逻辑 (Core Logic):**
    1. **参数解析**：
       - 无参数：显示全局概览
       - 有参数：显示指定主题详情
       - 参数验证和错误处理

    2. **全局概览显示**：
       - 列出所有活跃主题
       - 显示每个主题的学习统计（总概念数、已完成数、掌握度）
       - 使用状态图标和进度条

    3. **单主题详情显示**：
       - 树状结构展示概念层级
       - 显示每个概念的学习状态和掌握度
       - 高亮显示需要关注的概念

    4. **统计计算**：
       - 计算主题完成百分比
       - 计算平均掌握度
       - 识别学习瓶颈和建议

- **显示格式 (Display Format):**
  - 使用 Unicode 字符绘制树状结构
  - 状态图标：🟢(已掌握) 🟡(学习中) ⚪(未开始) 🔴(需复习)
  - 进度条：使用字符组合显示百分比
  - 颜色支持：使用 typer 的颜色功能

- **依赖变更 (Dependencies):**
  - 无新增依赖，使用现有的 `typer`、`rich` (如果可用) 等。

#### ✅ **4. 验收标准 (Acceptance Criteria)**

*（一个可执行的、用于验证任务是否完成的清单）*

**命令功能验收：**

- [ ] **命令注册成功**：运行 `ap --help`，输出中应包含 `t, tree, status` 命令。
- [ ] **全局概览功能**：运行 `ap t`，显示所有主题的概览信息。
- [ ] **单主题详情功能**：运行 `ap t <topic>`，显示该主题的详细学习进度。

**显示格式验收：**

- [ ] **树状结构清晰**：概念层级关系通过缩进和连接符清晰展示。
- [ ] **状态图标正确**：不同学习状态使用对应的图标表示。
- [ ] **统计信息准确**：完成百分比、掌握度等统计数据计算正确。

**交互体验验收：**

- [ ] **响应速度快**：命令执行时间在 1 秒内。
- [ ] **错误处理友好**：主题不存在时提供清晰的错误信息和建议。
- [ ] **输出格式美观**：使用合适的间距、对齐和颜色。

**数据准确性验收：**

- [ ] **统计计算正确**：总概念数、完成数、掌握度计算无误。
- [ ] **状态同步**：显示的状态与 `concept_map.json` 中的数据一致。
- [ ] **层级关系正确**：父子概念关系正确展示。

**边界情况验收：**

- [ ] **空数据处理**：没有主题时显示友好提示。
- [ ] **大量数据处理**：概念数量较多时仍能正常显示。
- [ ] **特殊字符处理**：概念名称包含特殊字符时正确显示。

#### ❓ **5. 潜在风险 (Potential Risks)**

*（预判可能遇到的问题）*
> **显示格式风险**：
>
> - 不同终端对 Unicode 字符的支持程度不同。
> - 终端宽度限制可能导致显示错乱。
> - 颜色支持在某些环境下可能不可用。

> **性能风险**：
>
> - 大量概念时的渲染性能问题。
> - 复杂的树状结构计算可能耗时较长。
> - 频繁的文件读取操作。

> **数据一致性风险**：
>
> - `concept_map.json` 文件损坏或格式错误。
> - 并发访问导致的数据不一致。
> - 统计计算中的浮点数精度问题。

#### 🔧 **6. 实现建议 (Implementation Tips)**

*（开发过程中的最佳实践建议）*

**主函数结构：**

```python
def display_tree(topic: str = None) -> None:
    """显示学习进度树状图"""
    try:
        concept_map = ConceptMap()
        
        if topic is None:
            # 显示全局概览
            display_global_overview(concept_map)
        else:
            # 显示单主题详情
            if not concept_map.topic_exists(topic):
                typer.echo(f"❌ 主题 '{topic}' 不存在")
                suggest_available_topics(concept_map)
                raise typer.Exit(1)
            
            display_topic_details(concept_map, topic)
            
    except Exception as e:
        typer.echo(f"❌ 显示失败: {str(e)}")
        raise typer.Exit(1)
```

**全局概览显示：**

```python
def display_global_overview(concept_map: ConceptMap) -> None:
    """显示所有主题的概览"""
    topics = concept_map.list_topics()
    
    if not topics:
        typer.echo("📚 还没有创建任何学习主题")
        typer.echo("💡 使用 'ap m <主题名称>' 创建第一个学习地图")
        return
    
    typer.echo("📊 学习进度概览")
    typer.echo("=" * 50)
    
    for topic_id, topic_data in topics.items():
        stats = calculate_topic_stats(topic_data)
        progress_bar = create_progress_bar(stats['completion_rate'])
        
        typer.echo(f"📖 {topic_data['name']}")
        typer.echo(f"   进度: {progress_bar} {stats['completion_rate']:.1f}%")
        typer.echo(f"   概念: {stats['completed']}/{stats['total']} 已完成")
        typer.echo(f"   掌握度: {stats['avg_mastery']:.1f}%")
        typer.echo()
```

**单主题详情显示：**

```python
def display_topic_details(concept_map: ConceptMap, topic_id: str) -> None:
    """显示单个主题的详细信息"""
    topic_data = concept_map.get_topic(topic_id)
    concepts = topic_data['concepts']
    
    typer.echo(f"📖 {topic_data['name']}")
    typer.echo("=" * 50)
    
    # 显示概念树
    display_concept_tree(concepts, level=0)
    
    # 显示统计信息
    stats = calculate_topic_stats(topic_data)
    typer.echo("\n📊 学习统计:")
    typer.echo(f"   总概念数: {stats['total']}")
    typer.echo(f"   已完成: {stats['completed']}")
    typer.echo(f"   完成率: {stats['completion_rate']:.1f}%")
    typer.echo(f"   平均掌握度: {stats['avg_mastery']:.1f}%")
```

**树状结构渲染：**

```python
def display_concept_tree(concepts: dict, level: int = 0, prefix: str = "") -> None:
    """递归显示概念树"""
    for i, (concept_id, concept_data) in enumerate(concepts.items()):
        is_last = i == len(concepts) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "
        
        # 状态图标
        status_icon = get_status_icon(concept_data['status'])
        mastery_text = f"({concept_data['mastery']['score']}%)" if concept_data['mastery']['score'] > 0 else ""
        
        typer.echo(f"{prefix}{current_prefix}{status_icon} {concept_data['name']} {mastery_text}")
        
        # 递归显示子概念
        if concept_data.get('children'):
            display_concept_tree(
                concept_data['children'], 
                level + 1, 
                prefix + next_prefix
            )
```

**统计计算函数：**

```python
def calculate_topic_stats(topic_data: dict) -> dict:
    """计算主题的学习统计信息"""
    concepts = topic_data['concepts']
    total_concepts = count_all_concepts(concepts)
    completed_concepts = count_completed_concepts(concepts)
    total_mastery = sum_all_mastery(concepts)
    
    return {
        'total': total_concepts,
        'completed': completed_concepts,
        'completion_rate': (completed_concepts / total_concepts * 100) if total_concepts > 0 else 0,
        'avg_mastery': (total_mastery / total_concepts) if total_concepts > 0 else 0
    }
```

**用户体验优化：**

- 使用清晰的视觉分隔符
- 提供有用的提示和建议
- 支持终端宽度自适应
- 实现渐进式信息展示
