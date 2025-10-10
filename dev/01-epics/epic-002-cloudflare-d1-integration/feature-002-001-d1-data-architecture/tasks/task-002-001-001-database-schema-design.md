# ⚡ Task-002-001-001: 数据库表结构设计

## 📋 基本信息

- **Task ID**: task-002-001-001-database-schema-design
- **所属 Feature**: [Feature-002-001: D1 数据存储架构](../README.md)
- **所属 Epic**: [Epic-002: Cloudflare D1 教学数据集成](../../README.md)
- **状态**: 待开始
- **优先级**: 高
- **负责人**: 数据库设计师
- **审查人**: 技术负责人
- **创建日期**: 2024-01-16
- **预计工时**: 1天
- **实际工时**: [完成后填写]
- **截止日期**: 2024-01-17

## 🎯 任务描述

### 任务目标

设计完整的 Cloudflare D1 数据库表结构，支持教学场景下的学生学习数据存储、查询和分析需求。

### 背景说明

为了实现教学数据的云端存储和分析，需要设计一套完整的数据库表结构。该结构需要支持学生信息管理、学习记录跟踪、概念掌握度统计和成绩计算等核心功能。

### 预期产出

- 完整的 SQL DDL 脚本文件
- 数据库设计文档
- 表关系图（ER 图）
- 索引优化方案
- 数据字典

## 🔧 技术实现

### 技术方案

#### 实现思路

基于教学场景的数据需求，设计五个核心表：students（学生）、classes（班级）、learning_records（学习记录）、concept_mastery（概念掌握）、grades（成绩）。采用关系型数据库设计原则，确保数据一致性和查询效率。

#### 技术选型

- **数据库**: Cloudflare D1 (基于 SQLite)
- **设计工具**: SQL DDL + 文档
- **版本控制**: Git
- **验证工具**: SQLite 本地测试

#### 架构设计

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   classes   │───▶│     students     │───▶│ learning_records │
│             │    │                  │    │                 │
└─────────────┘    └──────────────────┘    └─────────────────┘
                            │                        │
                            ▼                        ▼
                   ┌─────────────────┐    ┌─────────────────┐
                   │ concept_mastery │    │     grades      │
                   │                 │    │                 │
                   └─────────────────┘    └─────────────────┘
```

### 实现细节

#### 核心逻辑

1. **学生-班级关系**: 多对一关系，一个学生属于一个班级
2. **学习记录**: 记录所有学习行为，支持时间序列分析
3. **概念掌握**: 维护最新的掌握度状态，支持快速查询
4. **成绩计算**: 基于学习数据的综合评分

#### 数据结构

**主要表结构**:

```sql
-- 班级表
CREATE TABLE classes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    teacher_id TEXT NOT NULL,
    subject TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 学生表
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    class_id TEXT NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- 学习记录表
CREATE TABLE learning_records (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    concept TEXT NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN ('explain', 'quiz', 'mastery_update')),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER DEFAULT 0,
    data TEXT, -- JSON 格式
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- 概念掌握表
CREATE TABLE concept_mastery (
    student_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    concept TEXT NOT NULL,
    mastery_score REAL DEFAULT 0 CHECK (mastery_score >= 0 AND mastery_score <= 1),
    quiz_count INTEGER DEFAULT 0,
    best_score REAL DEFAULT 0 CHECK (best_score >= 0 AND best_score <= 1),
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, topic, concept),
    FOREIGN KEY (student_id) REFERENCES students(id)
);

-- 成绩表
CREATE TABLE grades (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    class_id TEXT NOT NULL,
    period TEXT NOT NULL,
    total_score REAL NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    learning_time_score REAL CHECK (learning_time_score >= 0 AND learning_time_score <= 100),
    mastery_score REAL CHECK (mastery_score >= 0 AND mastery_score <= 100),
    quiz_score REAL CHECK (quiz_score >= 0 AND quiz_score <= 100),
    participation_score REAL CHECK (participation_score >= 0 AND participation_score <= 100),
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
```

#### 索引设计

```sql
-- 学生表索引
CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_students_email ON students(email);

-- 学习记录表索引
CREATE INDEX idx_learning_records_student ON learning_records(student_id);
CREATE INDEX idx_learning_records_timestamp ON learning_records(timestamp);
CREATE INDEX idx_learning_records_topic_concept ON learning_records(topic, concept);
CREATE INDEX idx_learning_records_action_type ON learning_records(action_type);

-- 概念掌握表索引
CREATE INDEX idx_concept_mastery_student ON concept_mastery(student_id);
CREATE INDEX idx_concept_mastery_topic ON concept_mastery(topic);
CREATE INDEX idx_concept_mastery_score ON concept_mastery(mastery_score);

-- 成绩表索引
CREATE INDEX idx_grades_student_period ON grades(student_id, period);
CREATE INDEX idx_grades_class_period ON grades(class_id, period);
CREATE INDEX idx_grades_calculated_at ON grades(calculated_at);
```

### 代码结构

```
database/
├── schema/
│   ├── 01_create_tables.sql
│   ├── 02_create_indexes.sql
│   ├── 03_create_triggers.sql
│   └── 04_insert_sample_data.sql
├── docs/
│   ├── database_design.md
│   ├── er_diagram.png
│   └── data_dictionary.md
└── tests/
    ├── schema_validation.sql
    └── performance_tests.sql
```

## 🔗 依赖关系

### 前置依赖

#### 技术依赖

- [ ] Cloudflare D1 数据库服务可用
- [ ] SQLite 本地开发环境

#### 任务依赖

- [ ] 无直接任务依赖

#### 资源依赖

- [ ] 教学场景需求分析文档
- [ ] 现有 AP 系统数据模型参考

### 后续影响

- **影响的 Task**: 所有后续的 API 开发和数据操作任务
- **影响的组件**: Cloudflare Workers API 层
- **影响的用户**: 开发团队和最终用户

## ✅ 验收条件

### 功能验收

- [ ] 所有表结构创建成功，字段类型和约束正确
- [ ] 外键关系建立正确，引用完整性得到保证
- [ ] 索引创建成功，查询性能满足要求
- [ ] 数据字典完整，包含所有表和字段说明

### 代码质量验收

- [ ] SQL 语句符合标准规范，可读性良好
- [ ] 表名和字段名遵循命名约定
- [ ] 包含必要的注释和文档
- [ ] 通过 SQL 语法检查

### 测试验收

- [ ] 表结构在 SQLite 环境下测试通过
- [ ] 索引性能测试满足预期
- [ ] 数据完整性约束测试通过
- [ ] 样本数据插入和查询测试成功

### 文档验收

- [ ] 数据库设计文档完整准确
- [ ] ER 图清晰展示表关系
- [ ] 数据字典包含所有必要信息
- [ ] 索引优化方案文档化

### 部署验收

- [ ] SQL 脚本可以在 Cloudflare D1 环境执行
- [ ] 提供数据库初始化脚本
- [ ] 包含数据迁移和回滚方案

## 🧪 测试计划

### 单元测试

#### 测试用例

- **测试场景1**: 表结构创建测试
  - 输入: DDL 脚本
  - 预期输出: 所有表创建成功，无错误
- **测试场景2**: 约束验证测试
  - 输入: 违反约束的数据
  - 预期输出: 约束错误，数据插入失败
- **测试场景3**: 外键关系测试
  - 输入: 引用不存在的外键数据
  - 预期输出: 外键约束错误

### 集成测试

- [ ] 与 Cloudflare D1 的兼容性测试
- [ ] 大数据量下的性能测试
- [ ] 并发操作的数据一致性测试

### 性能测试

- [ ] 索引查询性能测试: 复杂查询 < 100ms
- [ ] 批量插入性能测试: 1000条记录 < 1s
- [ ] 并发查询测试: 50个并发查询正常响应

## 🚨 风险评估

### 技术风险

- **风险等级**: 低
- **风险描述**: Cloudflare D1 基于 SQLite，技术相对成熟
- **缓解措施**: 在本地 SQLite 环境充分测试后再部署

### 时间风险

- **风险等级**: 低
- **风险描述**: 数据库设计相对标准，时间风险较小
- **缓解措施**: 参考现有最佳实践，避免过度设计

### 依赖风险

- **风险等级**: 中
- **风险描述**: 依赖 Cloudflare D1 服务的稳定性和功能限制
- **缓解措施**: 研究 D1 的功能限制，设计时避开已知问题

## 📊 进度跟踪

### 当前状态

- **完成度**: 0%
- **当前阶段**: 设计
- **剩余工时**: 8小时
- **预计完成时间**: 2024-01-17

### 工作日志

| 日期 | 工作内容 | 耗时 | 进度 | 备注 |
|------|----------|------|------|------|
| 2024-01-16 | 任务创建和需求分析 | 1小时 | 10% | 初始规划 |

### 阻塞问题

| 问题描述 | 影响程度 | 负责人 | 预计解决时间 | 状态 |
|----------|----------|--------|--------------|------|
| 暂无 | - | - | - | - |

## 🔄 变更记录

| 日期 | 版本 | 变更类型 | 变更内容 | 变更原因 | 影响评估 |
|------|------|----------|----------|----------|----------|
| 2024-01-16 | v1.0 | 需求 | 初始任务创建 | 项目启动 | 无 |

## 📝 备注

### 注意事项

- Cloudflare D1 基于 SQLite，某些高级 SQL 功能可能不支持
- 考虑数据隐私保护，学生个人信息需要合规处理
- 设计时考虑未来扩展性，预留必要的字段和表结构

### 已知问题

- Cloudflare D1 目前处于 Beta 阶段，功能可能有限制
- SQLite 不支持某些复杂的数据类型和函数

### 后续优化

- 根据实际使用情况优化索引策略
- 考虑数据分区和归档策略
- 评估是否需要引入缓存层提升性能

### 数据字典模板

#### classes 表

| 字段名 | 数据类型 | 是否必填 | 默认值 | 说明 |
|--------|----------|----------|--------|------|
| id | TEXT | 是 | - | 班级唯一标识，建议使用 UUID |
| name | TEXT | 是 | - | 班级名称，如"2024级计算机1班" |
| teacher_id | TEXT | 是 | - | 教师ID，关联教师信息 |
| subject | TEXT | 否 | - | 科目名称，如"Python编程" |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 否 | CURRENT_TIMESTAMP | 更新时间 |

#### students 表

| 字段名 | 数据类型 | 是否必填 | 默认值 | 说明 |
|--------|----------|----------|--------|------|
| id | TEXT | 是 | - | 学生唯一标识，建议使用学号 |
| name | TEXT | 是 | - | 学生姓名 |
| class_id | TEXT | 是 | - | 所属班级ID |
| email | TEXT | 否 | - | 学生邮箱，用于通知 |
| created_at | DATETIME | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | 否 | CURRENT_TIMESTAMP | 更新时间 |

#### learning_records 表

| 字段名 | 数据类型 | 是否必填 | 默认值 | 说明 |
|--------|----------|----------|--------|------|
| id | TEXT | 是 | - | 记录唯一标识，使用 UUID |
| student_id | TEXT | 是 | - | 学生ID |
| topic | TEXT | 是 | - | 学习主题，如"python" |
| concept | TEXT | 是 | - | 具体概念，如"variables" |
| action_type | TEXT | 是 | - | 动作类型：explain/quiz/mastery_update |
| timestamp | DATETIME | 否 | CURRENT_TIMESTAMP | 学习时间 |
| duration | INTEGER | 否 | 0 | 学习时长（秒） |
| data | TEXT | 否 | - | JSON格式的详细数据 |

#### concept_mastery 表

| 字段名 | 数据类型 | 是否必填 | 默认值 | 说明 |
|--------|----------|----------|--------|------|
| student_id | TEXT | 是 | - | 学生ID |
| topic | TEXT | 是 | - | 学习主题 |
| concept | TEXT | 是 | - | 具体概念 |
| mastery_score | REAL | 否 | 0 | 掌握度分数 (0-1) |
| quiz_count | INTEGER | 否 | 0 | 测验次数 |
| best_score | REAL | 否 | 0 | 最佳测验分数 (0-1) |
| last_updated | DATETIME | 否 | CURRENT_TIMESTAMP | 最后更新时间 |

#### grades 表

| 字段名 | 数据类型 | 是否必填 | 默认值 | 说明 |
|--------|----------|----------|--------|------|
| id | TEXT | 是 | - | 成绩记录ID |
| student_id | TEXT | 是 | - | 学生ID |
| class_id | TEXT | 是 | - | 班级ID |
| period | TEXT | 是 | - | 评分周期，如"2024-01" |
| total_score | REAL | 是 | - | 总分 (0-100) |
| learning_time_score | REAL | 否 | - | 学习时长得分 |
| mastery_score | REAL | 否 | - | 掌握度得分 |
| quiz_score | REAL | 否 | - | 测验得分 |
| participation_score | REAL | 否 | - | 参与度得分 |
| calculated_at | DATETIME | 否 | CURRENT_TIMESTAMP | 计算时间 |
