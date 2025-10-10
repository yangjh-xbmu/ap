# ConceptMap 多主题数据结构使用指南

## 概述

ConceptMap 类已重构为支持多主题数据结构，允许在单个概念地图中管理多个学习主题。新架构保持向后兼容，支持从旧格式自动迁移。

## 核心特性

- **多主题支持**: 在一个概念地图中管理多个学习主题
- **智能主题推断**: 自动识别概念所属主题，无需手动指定
- **自动数据迁移**: 从旧的单主题格式自动升级到新的多主题格式
- **向后兼容**: 保持与现有代码的兼容性
- **KISS 原则**: 简单直观的 API 设计

## 基本用法

### 1. 创建和初始化

```python
from core.concept_map import ConceptMap

# 创建新的概念地图
concept_map = ConceptMap("concept_map.json")

# 如果文件不存在，会创建新的多主题结构
# 如果文件是旧格式，会自动迁移到新格式
```

### 2. 主题管理

```python
# 添加新主题
concept_map.add_topic("python", "Python Programming")
concept_map.add_topic("javascript", "JavaScript Development")

# 检查主题是否存在
if concept_map.topic_exists("python"):
    print("Python 主题已存在")

# 获取主题信息
python_topic = concept_map.get_topic("python")
print(f"主题名称: {python_topic['name']}")

# 列出所有主题
topics = concept_map.list_topics()
print(f"所有主题: {topics}")

# 删除主题
concept_map.remove_topic("javascript")
```

### 3. 概念管理

```python
# 添加概念到指定主题
concept_data = {
    "name": "Variables and Data Types",
    "children": ["integers", "strings", "lists"],
    "status": {
        "explained": False,
        "quiz_generated": False
    },
    "mastery": {
        "best_score_percent": -1
    }
}

concept_map.add_concept("python", "variables-and-data-types", concept_data)

# 获取概念
concept = concept_map.get_concept("python", "variables-and-data-types")
print(f"概念名称: {concept['name']}")

# 更新概念状态
concept_map.update_status("python", "variables-and-data-types", "explained", True)
concept_map.update_status("python", "variables-and-data-types", "quiz_generated", True)

# 更新掌握程度
concept_map.update_mastery("python", "variables-and-data-types", 85.0)
```

### 4. 数据持久化

```python
# 保存数据到文件
concept_map.save()

# 重新加载数据
concept_map.load()
```

## 高级用法

### 1. 获取默认主题

```python
# 获取默认主题 ID（优先返回 "default"，否则返回第一个主题）
default_topic_id = concept_map.get_default_topic_id()
if default_topic_id:
    print(f"默认主题: {default_topic_id}")
```

### 2. 智能主题推断

```python
# 根据概念 ID 自动查找所属主题
concept_id = "variables-and-data-types"
topic_id = concept_map.get_topic_by_concept(concept_id)

if topic_id:
    print(f"概念 '{concept_id}' 属于主题: {topic_id}")
    # 可以直接获取概念数据
    concept_data = concept_map.get_concept(topic_id, concept_id)
else:
    print(f"未找到概念 '{concept_id}' 所属的主题")

# 实际应用场景：CLI 命令中的自动主题推断
# 当用户执行 `ap e "变量与基本数据类型"` 时：
# 1. 系统检测到概念名称中没有 '/' 分隔符
# 2. 自动调用 get_topic_by_concept() 查找主题
# 3. 找到概念属于 "python核心语法" 主题
# 4. 自动保存到正确的主题目录下
```

### 3. 扁平化概念视图（向后兼容）

```python
# 获取所有概念的扁平化视图（用于向后兼容）
all_concepts = concept_map.get_all_concepts_flat()
for concept_id, concept_data in all_concepts.items():
    print(f"{concept_id}: {concept_data['name']}")
```

### 4. 批量操作

```python
# 批量添加概念
concepts_to_add = [
    ("functions", {"name": "Functions", "children": []}),
    ("classes", {"name": "Classes and Objects", "children": []}),
    ("modules", {"name": "Modules and Packages", "children": []})
]

for concept_id, concept_data in concepts_to_add:
    concept_map.add_concept("python", concept_id, concept_data)

# 保存所有更改
concept_map.save()
```

## 数据结构

### 新格式数据结构

```json
{
  "topics": {
    "python": {
      "name": "Python Programming",
      "created_at": "2024-01-15T10:30:00Z",
      "concepts": {
        "variables-and-data-types": {
          "name": "Variables and Data Types",
          "children": ["integers", "strings", "lists"],
          "status": {
            "explained": true,
            "quiz_generated": true
          },
          "mastery": {
            "best_score_percent": 85.0
          }
        }
      }
    }
  },
  "metadata": {
    "version": "2.0",
    "created_at": "2024-01-15T10:30:00Z",
    "last_modified": "2024-01-15T11:45:00Z",
    "active_topics": ["python"]
  }
}
```

## 迁移说明

### 自动迁移

当加载旧格式的概念地图文件时，系统会自动：

1. 检测旧格式数据
2. 创建备份文件（原文件名 + `.backup`）
3. 将所有概念迁移到 "default" 主题下
4. 保存新格式数据
5. 显示迁移完成信息

### 旧格式示例

```json
{
  "python-basics": {
    "name": "Python Basics",
    "children": ["variables", "functions"],
    "status": {"explained": true, "quiz_generated": false},
    "mastery": {"best_score_percent": 85.0}
  }
}
```

### 迁移后格式

```json
{
  "topics": {
    "default": {
      "name": "Default Topic",
      "concepts": {
        "python-basics": {
          "name": "Python Basics",
          "children": ["variables", "functions"],
          "status": {"explained": true, "quiz_generated": false},
          "mastery": {"best_score_percent": 85.0}
        }
      }
    }
  },
  "metadata": {
    "version": "2.0",
    "active_topics": ["default"]
  }
}
```

## 错误处理

```python
try:
    # 尝试添加概念到不存在的主题
    concept_map.add_concept("nonexistent", "test", {"name": "Test"})
except ValueError as e:
    print(f"错误: {e}")

try:
    # 尝试获取不存在的概念
    concept = concept_map.get_concept("python", "nonexistent")
    if concept is None:
        print("概念不存在")
except Exception as e:
    print(f"获取概念时出错: {e}")
```

## 最佳实践

1. **主题命名**: 使用有意义的主题 ID，如 "python", "javascript", "data-science"
2. **概念 ID**: 使用 kebab-case 格式，如 "variables-and-data-types"
3. **定期保存**: 在重要操作后调用 `save()` 方法
4. **错误处理**: 始终检查操作结果和处理可能的异常
5. **备份**: 重要数据变更前手动创建备份

## 与现有代码的兼容性

新的 ConceptMap 类保持与现有代码的兼容性：

- `get_all_concepts_flat()` 方法提供扁平化视图
- 自动迁移确保旧数据可以无缝升级
- 核心 API（如 `update_status`, `update_mastery`）保持不变

这确保了现有的代码可以继续工作，同时逐步迁移到多主题架构。

## CLI 命令中的智能主题推断

### 概念解释命令 (`ap e`)

智能主题推断让用户无需手动指定主题，系统会自动识别概念所属的主题：

```bash
# 传统方式：需要指定完整路径
ap e "python核心语法/变量与基本数据类型"

# 智能推断：只需概念名称
ap e "变量与基本数据类型"
# 系统自动：
# 1. 检测概念名称中没有 '/' 分隔符
# 2. 在概念地图中查找该概念
# 3. 找到概念属于 "python核心语法" 主题
# 4. 保存到 workspace/python核心语法/explanation/变量与基本数据类型.md
```

### 测验生成命令 (`ap g`)

同样支持智能主题推断：

```bash
# 智能推断概念所属主题
ap g "变量与基本数据类型" --num-questions 5

# 系统自动保存到正确的主题目录
# workspace/python核心语法/quizzes/变量与基本数据类型.yml
```

### 工作原理

1. **输入解析**: 检查概念名称是否包含 `/` 分隔符
2. **主题查找**: 如果没有分隔符，调用 `get_topic_by_concept()` 方法
3. **路径构建**: 使用找到的主题构建正确的文件保存路径
4. **优雅降级**: 如果找不到主题，使用默认主题或提示用户

这个特性大大简化了用户体验，让学习过程更加流畅！