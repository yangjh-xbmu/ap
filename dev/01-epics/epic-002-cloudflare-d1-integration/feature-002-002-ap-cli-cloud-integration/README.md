# 🎯 Feature-002-002: AP CLI 云端集成

## 📋 基本信息
- **Feature ID**: feature-002-002-ap-cli-cloud-integration
- **所属 Epic**: [Epic-002: Cloudflare D1 教学数据集成](../README.md)
- **状态**: 规划中
- **优先级**: 高
- **负责人**: 开发团队
- **开发团队**: AP开发团队
- **创建日期**: 2024-01-16
- **预计工期**: 2周
- **实际工期**: [完成后填写]

## 🎯 功能模块

### 核心功能
扩展现有的 AP CLI 系统，集成 Cloudflare D1 云端数据同步功能，实现学习数据的自动上传和同步，同时保持向后兼容性和用户体验的一致性。

### 功能边界
**包含功能**:
- ✅ ConceptMap 类扩展支持云端同步
- ✅ CLI 命令集成数据上传功能
- ✅ 配置管理系统（学生ID、班级等）
- ✅ 网络异常处理和离线缓存
- ✅ 数据同步状态跟踪

**不包含功能**:
- ❌ Web 界面开发
- ❌ 教师端功能
- ❌ Cloudflare 基础设施部署
- ❌ 用户认证系统

### 技术架构
- **编程语言**: Python 3.10+
- **CLI 框架**: Typer
- **HTTP 客户端**: requests 或 httpx
- **配置管理**: python-dotenv + YAML
- **数据格式**: JSON

## 👥 用户场景

### 目标用户
- **主要用户**: 学生（AP CLI 使用者）
- **次要用户**: 教师（通过配置管理学生）
- **用户画像**: 使用 AP 系统学习的学生，希望学习数据能够被教师跟踪

### 用户故事
**作为** 学生，**我希望** 我的学习进度能够自动同步到云端，**以便** 老师了解我的学习情况

#### 主要用户故事
1. **作为** 学生，**我希望** 使用 `ap e` 命令时自动记录学习行为，**以便** 老师了解我的学习进度
2. **作为** 学生，**我希望** 完成测验时自动上传结果，**以便** 系统更新我的掌握度
3. **作为** 学生，**我希望** 通过简单配置启用云端同步，**以便** 快速开始使用

#### 次要用户故事
1. **作为** 学生，**我希望** 网络异常时系统仍能正常工作，**以便** 不影响我的学习
2. **作为** 学生，**我希望** 能够查看数据同步状态，**以便** 确认数据已上传

### 使用场景
#### 场景一：首次配置云端同步
- **触发条件**: 学生首次使用云端功能
- **操作流程**: 运行 `ap config cloud` → 输入学生ID和班级 → 测试连接 → 配置完成
- **预期结果**: 配置保存成功，后续学习数据自动同步

#### 场景二：学习概念并自动同步
- **触发条件**: 学生使用 `ap e python/variables` 学习概念
- **操作流程**: 生成解释 → 更新本地状态 → 自动上传学习记录 → 返回结果
- **预期结果**: 概念解释生成，学习记录同步到云端

#### 场景三：网络异常处理
- **触发条件**: 网络连接异常或 API 不可用
- **操作流程**: 检测网络异常 → 缓存数据到本地 → 继续正常功能 → 网络恢复后自动同步
- **预期结果**: 用户体验不受影响，数据最终同步成功

## ✅ 验收标准

### 功能验收标准
#### 核心功能验收
- [ ] ConceptMap 类支持云端同步，API 兼容现有代码
- [ ] 所有 CLI 命令（`ap e`, `ap q`, `ap m`）集成数据上传功能
- [ ] 配置系统支持学生ID、班级ID、API端点等设置
- [ ] 网络异常时系统能够优雅降级，不影响核心功能

#### 用户体验验收
- [ ] 云端同步对用户透明，不增加额外操作步骤
- [ ] 命令响应时间增加 < 1秒（网络正常情况下）
- [ ] 提供清晰的配置指导和错误提示
- [ ] 支持禁用云端功能，保持纯本地模式

### 技术验收标准
#### 代码质量
- [ ] 代码覆盖率达到 85%
- [ ] 通过代码审查
- [ ] 符合现有项目编码规范
- [ ] 向后兼容，不破坏现有功能

#### 性能标准
- [ ] 数据上传响应时间 < 2秒
- [ ] 离线缓存机制工作正常
- [ ] 内存使用增加 < 10MB
- [ ] 支持并发操作，无数据竞争

#### 安全标准
- [ ] API 通信使用 HTTPS
- [ ] 敏感配置信息加密存储
- [ ] 输入数据验证和清理
- [ ] 错误信息不泄露敏感信息

### 测试验收标准
- [ ] 单元测试通过率 100%
- [ ] 集成测试覆盖所有 CLI 命令
- [ ] 网络异常场景测试通过
- [ ] 性能测试满足要求

## 🔗 依赖关系

### 前置依赖
- **技术依赖**: Feature-002-001 (D1 数据存储架构) 必须完成
- **数据依赖**: Cloudflare Workers API 可用
- **其他 Feature**: Epic-001 多主题学习系统

### 后续影响
- **影响的 Feature**: Feature-002-003 (教师管理界面) 依赖此功能提供数据
- **影响的系统**: 为整个教学数据生态提供数据源
- **影响的用户**: 所有使用 AP CLI 的学生

## 📋 Task 分解

### 设计阶段
- [ ] **Task-002-002-001**: ConceptMap 类云端同步设计 - 1天
- [ ] **Task-002-002-002**: 配置管理系统设计 - 0.5天
- [ ] **Task-002-002-003**: 网络异常处理策略设计 - 0.5天

### 开发阶段
- [ ] **Task-002-002-004**: HTTP 客户端和 API 集成 - 1天
- [ ] **Task-002-002-005**: ConceptMap 类扩展实现 - 2天
- [ ] **Task-002-002-006**: CLI 命令集成数据上传 - 2天
- [ ] **Task-002-002-007**: 配置管理功能实现 - 1天
- [ ] **Task-002-002-008**: 离线缓存和同步机制 - 1.5天

### 测试阶段
- [ ] **Task-002-002-009**: 单元测试编写 - 1.5天
- [ ] **Task-002-002-010**: 集成测试和 CLI 测试 - 1天
- [ ] **Task-002-002-011**: 网络异常场景测试 - 1天

### 部署阶段
- [ ] **Task-002-002-012**: 文档更新和使用指南 - 1天
- [ ] **Task-002-002-013**: 版本兼容性测试 - 0.5天

## 📊 进度跟踪

### 当前状态
- **整体进度**: 0%
- **当前阶段**: 设计
- **已完成 Task**: 0/13
- **下一个里程碑**: ConceptMap 设计完成 - 2024-01-18

### 风险评估
- 🟡 **技术风险**: 中 - 需要保持向后兼容性
- 🟡 **时间风险**: 中 - 涉及多个 CLI 命令的修改
- 🟢 **资源风险**: 低 - 团队熟悉现有代码库

## 📈 成功指标

### 业务指标
- **用户采用率**: > 80% 的学生启用云端同步
- **数据同步率**: > 99% 的学习行为成功同步
- **用户满意度**: 用户反馈云端功能不影响使用体验

### 技术指标
- **系统稳定性**: 云端集成后系统崩溃率 < 0.1%
- **响应时间**: 命令执行时间增加 < 20%
- **数据准确性**: 本地和云端数据一致性 > 99.9%

## 🔄 变更记录

| 日期 | 版本 | 变更内容 | 变更原因 | 影响评估 |
|------|------|----------|----------|----------|
| 2024-01-16 | v1.0 | 初始版本创建 | 项目启动 | 无 |

## 📝 备注

### 技术实现细节

#### ConceptMap 类扩展设计
```python
class ConceptMap:
    def __init__(self, workspace_dir: str, cloud_config: Optional[CloudConfig] = None):
        self.workspace_dir = workspace_dir
        self.cloud_config = cloud_config
        self.cloud_client = CloudClient(cloud_config) if cloud_config else None
        self.sync_queue = SyncQueue()  # 离线缓存队列
        
    def update_concept_status(self, topic: str, concept: str, status_update: dict):
        # 更新本地状态
        self._update_local_status(topic, concept, status_update)
        
        # 异步同步到云端
        if self.cloud_client:
            self._sync_to_cloud_async(topic, concept, status_update)
    
    def _sync_to_cloud_async(self, topic: str, concept: str, data: dict):
        try:
            self.cloud_client.upload_learning_record(
                topic=topic,
                concept=concept,
                action_type=data.get('action_type'),
                data=data
            )
        except NetworkError:
            # 网络异常时加入同步队列
            self.sync_queue.add(topic, concept, data)
```

#### 配置管理设计
```python
# ~/.ap/config.yaml
cloud:
  enabled: true
  student_id: "student_001"
  class_id: "class_2024_cs_01"
  api_endpoint: "https://ap-api.example.com"
  api_key: "encrypted_api_key"
  sync_interval: 30  # 秒
  offline_cache_size: 1000  # 最大缓存记录数

# 环境变量支持
# AP_CLOUD_ENABLED=true
# AP_STUDENT_ID=student_001
# AP_CLASS_ID=class_2024_cs_01
# AP_API_ENDPOINT=https://ap-api.example.com
# AP_API_KEY=your_api_key
```

#### CLI 命令集成示例
```python
@app.command()
def explain(concept: str):
    """生成概念解释并同步学习记录"""
    # 现有逻辑
    topic, concept_name = parse_concept(concept)
    explanation = generate_explanation(topic, concept_name)
    
    # 更新本地状态
    concept_map.update_concept_status(topic, concept_name, {
        'explained': True,
        'action_type': 'explain',
        'timestamp': datetime.now().isoformat(),
        'duration': explanation_time
    })
    
    # 云端同步在 ConceptMap 内部自动处理
    typer.echo(f"✅ 概念解释已生成: {explanation_file}")
    
    # 显示同步状态（可选）
    if concept_map.cloud_enabled:
        sync_status = concept_map.get_sync_status()
        if sync_status.pending > 0:
            typer.echo(f"📤 {sync_status.pending} 条记录待同步")
```

#### 网络异常处理机制
```python
class SyncQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = deque(maxlen=max_size)
        self.retry_interval = 60  # 秒
        
    def add(self, topic: str, concept: str, data: dict):
        """添加待同步记录"""
        record = {
            'topic': topic,
            'concept': concept,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'retry_count': 0
        }
        self.queue.append(record)
        
    def process_pending(self, cloud_client: CloudClient):
        """处理待同步记录"""
        while self.queue:
            record = self.queue.popleft()
            try:
                cloud_client.upload_learning_record(**record)
            except NetworkError:
                record['retry_count'] += 1
                if record['retry_count'] < 3:
                    self.queue.append(record)  # 重新加入队列
                break  # 网络仍然异常，停止处理
```

#### API 客户端设计
```python
class CloudClient:
    def __init__(self, config: CloudConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        })
        
    def upload_learning_record(self, topic: str, concept: str, 
                             action_type: str, data: dict) -> bool:
        """上传学习记录到云端"""
        payload = {
            'student_id': self.config.student_id,
            'topic': topic,
            'concept': concept,
            'action_type': action_type,
            'timestamp': data.get('timestamp'),
            'data': data
        }
        
        try:
            response = self.session.post(
                f'{self.config.api_endpoint}/api/learning-records',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.warning(f"Failed to sync learning record: {e}")
            raise NetworkError(f"Network error: {e}")
            
    def update_concept_mastery(self, topic: str, concept: str, 
                             mastery_score: float) -> bool:
        """更新概念掌握度"""
        payload = {
            'student_id': self.config.student_id,
            'topic': topic,
            'concept': concept,
            'mastery_score': mastery_score,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            response = self.session.put(
                f'{self.config.api_endpoint}/api/concept-mastery',
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.warning(f"Failed to update mastery: {e}")
            raise NetworkError(f"Network error: {e}")
```

### 配置命令设计
```python
@app.command()
def config(
    action: str = typer.Argument(..., help="配置操作: setup, show, test"),
    student_id: Optional[str] = typer.Option(None, help="学生ID"),
    class_id: Optional[str] = typer.Option(None, help="班级ID"),
    api_endpoint: Optional[str] = typer.Option(None, help="API端点")
):
    """配置云端同步设置"""
    if action == "setup":
        setup_cloud_config(student_id, class_id, api_endpoint)
    elif action == "show":
        show_current_config()
    elif action == "test":
        test_cloud_connection()
    else:
        typer.echo("❌ 无效的配置操作")

def setup_cloud_config(student_id: str, class_id: str, api_endpoint: str):
    """交互式配置云端同步"""
    if not student_id:
        student_id = typer.prompt("请输入学生ID")
    if not class_id:
        class_id = typer.prompt("请输入班级ID")
    if not api_endpoint:
        api_endpoint = typer.prompt("请输入API端点", 
                                  default="https://ap-api.example.com")
    
    # 测试连接
    typer.echo("🔍 测试连接...")
    if test_connection(student_id, class_id, api_endpoint):
        # 保存配置
        save_cloud_config(student_id, class_id, api_endpoint)
        typer.echo("✅ 云端同步配置成功")
    else:
        typer.echo("❌ 连接测试失败，请检查配置")
```

### 注意事项
- 保持向后兼容性，现有用户不受影响
- 云端功能为可选功能，默认禁用
- 网络异常时优雅降级，不影响核心学习功能
- 敏感信息（API密钥）需要加密存储
- 提供详细的错误信息和调试日志
- 考虑数据隐私保护，遵循相关法规要求