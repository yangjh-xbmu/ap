# 🎯 Feature-002-004: 部署和运维

## 📋 基本信息
- **Feature ID**: feature-002-004-deployment-and-operations
- **所属 Epic**: [Epic-002: Cloudflare D1 教学数据集成](../README.md)
- **状态**: 规划中
- **优先级**: 中
- **负责人**: DevOps团队
- **开发团队**: AP开发团队
- **创建日期**: 2024-01-16
- **预计工期**: 2周
- **实际工期**: [完成后填写]

## 🎯 功能模块

### 核心功能
建立完整的 Cloudflare 生态系统部署和运维体系，包括 Cloudflare D1 数据库、Workers API、Pages 前端应用的自动化部署、监控、备份和故障恢复机制。

### 功能边界
**包含功能**:
- ✅ Cloudflare D1 数据库部署和管理
- ✅ Cloudflare Workers API 部署和版本管理
- ✅ Cloudflare Pages 前端应用部署
- ✅ CI/CD 流水线配置
- ✅ 监控和告警系统
- ✅ 数据备份和恢复策略
- ✅ 性能优化和缓存配置
- ✅ 安全配置和访问控制

**不包含功能**:
- ❌ 第三方云服务集成
- ❌ 本地开发环境管理
- ❌ 代码质量检查工具
- ❌ 用户培训和文档维护

### 技术架构
- **部署平台**: Cloudflare (D1, Workers, Pages)
- **CI/CD**: GitHub Actions
- **监控**: Cloudflare Analytics + Sentry
- **备份**: Cloudflare D1 备份 + 外部存储
- **配置管理**: Wrangler CLI + 环境变量
- **日志**: Cloudflare Workers 日志

## 👥 用户场景

### 目标用户
- **主要用户**: DevOps 工程师、系统管理员
- **次要用户**: 开发团队、项目经理
- **用户画像**: 负责系统部署和运维的技术人员，需要确保系统稳定运行

### 用户故事
**作为** DevOps 工程师，**我希望** 能够自动化部署和管理整个系统，**以便** 确保系统稳定运行并快速响应问题

#### 主要用户故事
1. **作为** DevOps 工程师，**我希望** 通过 CI/CD 自动部署应用，**以便** 提高部署效率和一致性
2. **作为** 系统管理员，**我希望** 实时监控系统状态，**以便** 及时发现和解决问题
3. **作为** DevOps 工程师，**我希望** 自动备份数据，**以便** 在故障时快速恢复
4. **作为** 开发团队，**我希望** 有多环境支持，**以便** 安全地测试和发布功能

#### 次要用户故事
1. **作为** 项目经理，**我希望** 查看部署状态和系统指标，**以便** 了解项目运行情况
2. **作为** DevOps 工程师，**我希望** 配置告警规则，**以便** 在异常时及时收到通知
3. **作为** 系统管理员，**我希望** 管理访问权限，**以便** 确保系统安全

### 使用场景
#### 场景一：自动化部署新版本
- **触发条件**: 开发团队推送代码到主分支
- **操作流程**: 代码推送 → CI/CD 触发 → 自动测试 → 部署到生产环境 → 验证部署
- **预期结果**: 新版本成功部署，系统正常运行

#### 场景二：监控告警和故障处理
- **触发条件**: 系统出现异常或性能下降
- **操作流程**: 监控检测异常 → 发送告警 → 运维人员响应 → 问题诊断和修复
- **预期结果**: 快速定位和解决问题，最小化服务中断

#### 场景三：数据备份和恢复
- **触发条件**: 定期备份或故障恢复需求
- **操作流程**: 自动备份执行 → 验证备份完整性 → 存储到安全位置 → 必要时执行恢复
- **预期结果**: 数据安全可靠，恢复流程顺畅

## ✅ 验收标准

### 功能验收标准
#### 核心功能验收
- [ ] CI/CD 流水线能够自动部署所有组件（D1、Workers、Pages）
- [ ] 监控系统能够实时跟踪关键指标和异常
- [ ] 备份系统能够定期备份数据并验证完整性
- [ ] 多环境部署（开发、测试、生产）正常工作
- [ ] 故障恢复流程经过测试验证

#### 用户体验验收
- [ ] 部署过程对用户透明，不影响正常使用
- [ ] 监控仪表盘直观易懂，关键信息一目了然
- [ ] 告警及时准确，减少误报和漏报
- [ ] 文档完整，运维人员能够快速上手

### 技术验收标准
#### 系统可靠性
- [ ] 系统可用性达到 99.9%
- [ ] 部署成功率 > 95%
- [ ] 故障恢复时间 < 30分钟
- [ ] 数据备份成功率 100%

#### 性能标准
- [ ] API 响应时间 < 500ms (P95)
- [ ] 前端页面加载时间 < 3秒
- [ ] 数据库查询性能满足业务需求
- [ ] CDN 缓存命中率 > 90%

#### 安全标准
- [ ] 所有通信使用 HTTPS
- [ ] 访问控制和身份验证正常工作
- [ ] 敏感数据加密存储
- [ ] 定期安全扫描和漏洞修复

### 测试验收标准
- [ ] 部署流程测试通过
- [ ] 监控和告警测试通过
- [ ] 备份和恢复测试通过
- [ ] 性能压力测试通过
- [ ] 安全渗透测试通过

## 🔗 依赖关系

### 前置依赖
- **技术依赖**: 所有其他 Feature (002-001, 002-002, 002-003) 必须完成
- **基础设施**: Cloudflare 账户和相关服务配置
- **工具依赖**: GitHub Actions、Wrangler CLI

### 后续影响
- **影响的系统**: 为整个 AP 教学系统提供稳定的运行环境
- **影响的用户**: 所有系统用户（学生、教师、管理员）
- **影响的业务**: 确保教学活动的连续性和数据安全

## 📋 Task 分解

### 设计阶段
- [ ] **Task-002-004-001**: 部署架构设计和环境规划 - 1天
- [ ] **Task-002-004-002**: 监控和告警策略设计 - 1天
- [ ] **Task-002-004-003**: 备份和恢复策略设计 - 0.5天

### 基础设施阶段
- [ ] **Task-002-004-004**: Cloudflare 服务配置和初始化 - 1天
- [ ] **Task-002-004-005**: 多环境配置（开发、测试、生产） - 1天
- [ ] **Task-002-004-006**: 域名和 SSL 证书配置 - 0.5天

### CI/CD 阶段
- [ ] **Task-002-004-007**: GitHub Actions 工作流配置 - 1.5天
- [ ] **Task-002-004-008**: 自动化测试集成 - 1天
- [ ] **Task-002-004-009**: 部署脚本和回滚机制 - 1天

### 监控运维阶段
- [ ] **Task-002-004-010**: 监控系统配置和仪表盘 - 1.5天
- [ ] **Task-002-004-011**: 告警规则和通知配置 - 1天
- [ ] **Task-002-004-012**: 日志收集和分析系统 - 1天

### 备份恢复阶段
- [ ] **Task-002-004-013**: 数据备份自动化配置 - 1天
- [ ] **Task-002-004-014**: 恢复流程测试和文档 - 1天

### 文档和培训阶段
- [ ] **Task-002-004-015**: 运维文档和操作手册 - 1天
- [ ] **Task-002-004-016**: 团队培训和知识转移 - 0.5天

## 📊 进度跟踪

### 当前状态
- **整体进度**: 0%
- **当前阶段**: 设计
- **已完成 Task**: 0/16
- **下一个里程碑**: 部署架构设计完成 - 2024-01-18

### 风险评估
- 🟡 **技术风险**: 中 - Cloudflare 服务配置复杂，需要深入了解
- 🟢 **时间风险**: 低 - 部署和运维相对标准化
- 🟡 **依赖风险**: 中 - 依赖其他 Feature 的完成

## 📈 成功指标

### 业务指标
- **系统可用性**: > 99.9%
- **部署频率**: 支持每日多次部署
- **故障恢复时间**: < 30分钟
- **用户满意度**: 系统稳定性评分 > 4.5/5

### 技术指标
- **部署成功率**: > 95%
- **监控覆盖率**: 100% 关键组件被监控
- **告警准确率**: > 90% (减少误报)
- **备份成功率**: 100%

## 🔄 变更记录

| 日期 | 版本 | 变更内容 | 变更原因 | 影响评估 |
|------|------|----------|----------|----------|
| 2024-01-16 | v1.0 | 初始版本创建 | 项目启动 | 无 |

## 📝 备注

### 部署架构设计

#### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare 生态系统                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Cloudflare  │  │ Cloudflare  │  │   Cloudflare D1     │   │
│  │   Pages     │  │  Workers    │  │    Database         │   │
│  │ (前端应用)   │  │  (API服务)   │  │   (数据存储)         │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
│         │                │                      │            │
│         └────────────────┼──────────────────────┘            │
│                          │                                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Cloudflare CDN & Security                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   外部监控和备份                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │   Sentry    │  │  GitHub     │  │   外部备份存储       │   │
│  │ (错误监控)   │  │ Actions     │  │  (AWS S3/其他)      │   │
│  │             │  │ (CI/CD)     │  │                     │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 环境配置策略
```yaml
# 环境配置矩阵
environments:
  development:
    domain: "dev-ap.example.com"
    d1_database: "ap-dev-db"
    workers_name: "ap-api-dev"
    pages_project: "ap-teacher-dev"
    monitoring: "basic"
    
  staging:
    domain: "staging-ap.example.com"
    d1_database: "ap-staging-db"
    workers_name: "ap-api-staging"
    pages_project: "ap-teacher-staging"
    monitoring: "full"
    
  production:
    domain: "ap.example.com"
    d1_database: "ap-prod-db"
    workers_name: "ap-api-prod"
    pages_project: "ap-teacher-prod"
    monitoring: "full"
    backup: "enabled"
```

### CI/CD 流水线设计

#### GitHub Actions 工作流
```yaml
# .github/workflows/deploy.yml
name: Deploy AP System

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.10'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          
      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          npm run test
          python -m pytest
          
      - name: Run linting
        run: |
          npm run lint
          python -m flake8
          
  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Wrangler
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          
      - name: Deploy D1 Database
        run: |
          wrangler d1 execute ap-staging-db --file=./database/schema.sql
          wrangler d1 execute ap-staging-db --file=./database/seed.sql
          
      - name: Deploy Workers API
        run: |
          wrangler deploy --env staging
          
      - name: Deploy Pages Frontend
        run: |
          npm run build:staging
          wrangler pages deploy dist --project-name ap-teacher-staging
          
      - name: Run smoke tests
        run: |
          npm run test:e2e:staging
          
  deploy-production:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Wrangler
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          
      - name: Backup Production Database
        run: |
          wrangler d1 backup create ap-prod-db
          
      - name: Deploy D1 Database (Migration)
        run: |
          wrangler d1 migrations apply ap-prod-db
          
      - name: Deploy Workers API
        run: |
          wrangler deploy --env production
          
      - name: Deploy Pages Frontend
        run: |
          npm run build:production
          wrangler pages deploy dist --project-name ap-teacher-prod
          
      - name: Run production tests
        run: |
          npm run test:e2e:production
          
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

#### 部署脚本设计
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
BACKUP=${2:-false}

echo "🚀 开始部署到 $ENVIRONMENT 环境..."

# 1. 环境检查
echo "📋 检查环境配置..."
if ! wrangler whoami; then
    echo "❌ Wrangler 未登录"
    exit 1
fi

# 2. 备份（生产环境）
if [ "$ENVIRONMENT" = "production" ] && [ "$BACKUP" = "true" ]; then
    echo "💾 创建数据库备份..."
    BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
    wrangler d1 backup create ap-prod-db --name "$BACKUP_NAME"
    echo "✅ 备份创建完成: $BACKUP_NAME"
fi

# 3. 数据库迁移
echo "🗄️ 执行数据库迁移..."
wrangler d1 migrations apply "ap-${ENVIRONMENT}-db"

# 4. 部署 Workers API
echo "⚡ 部署 Workers API..."
wrangler deploy --env "$ENVIRONMENT"

# 5. 构建和部署前端
echo "🎨 构建前端应用..."
npm run "build:$ENVIRONMENT"

echo "📤 部署前端应用..."
wrangler pages deploy dist --project-name "ap-teacher-$ENVIRONMENT"

# 6. 健康检查
echo "🔍 执行健康检查..."
HEALTH_URL="https://api-$ENVIRONMENT.ap.example.com/health"
if curl -f "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    exit 1
fi

# 7. 烟雾测试
echo "🧪 执行烟雾测试..."
npm run "test:smoke:$ENVIRONMENT"

echo "🎉 部署完成！"
```

### 监控和告警系统

#### Cloudflare Analytics 配置
```javascript
// workers/src/analytics.js
export class AnalyticsCollector {
  constructor(env) {
    this.env = env;
  }

  // 记录 API 调用指标
  async recordAPICall(request, response, duration) {
    const metrics = {
      timestamp: Date.now(),
      method: request.method,
      url: request.url,
      status: response.status,
      duration: duration,
      userAgent: request.headers.get('User-Agent'),
      ip: request.headers.get('CF-Connecting-IP')
    };

    // 发送到 Cloudflare Analytics
    await this.env.ANALYTICS.writeDataPoint(metrics);
  }

  // 记录错误
  async recordError(error, context) {
    const errorData = {
      timestamp: Date.now(),
      message: error.message,
      stack: error.stack,
      context: context,
      severity: this.getSeverity(error)
    };

    // 发送到 Sentry
    if (this.env.SENTRY_DSN) {
      await this.sendToSentry(errorData);
    }

    // 发送到 Cloudflare Analytics
    await this.env.ANALYTICS.writeDataPoint({
      type: 'error',
      ...errorData
    });
  }

  getSeverity(error) {
    if (error.name === 'DatabaseError') return 'high';
    if (error.name === 'ValidationError') return 'medium';
    return 'low';
  }
}
```

#### 告警规则配置
```yaml
# monitoring/alerts.yml
alerts:
  - name: "API 响应时间过高"
    condition: "avg(api_response_time) > 1000ms"
    duration: "5m"
    severity: "warning"
    channels: ["slack", "email"]
    
  - name: "API 错误率过高"
    condition: "rate(api_errors) > 5%"
    duration: "2m"
    severity: "critical"
    channels: ["slack", "email", "sms"]
    
  - name: "数据库连接失败"
    condition: "count(database_connection_errors) > 0"
    duration: "1m"
    severity: "critical"
    channels: ["slack", "email", "sms"]
    
  - name: "前端页面加载缓慢"
    condition: "avg(page_load_time) > 5000ms"
    duration: "10m"
    severity: "warning"
    channels: ["slack"]
    
  - name: "用户活跃度异常下降"
    condition: "count(active_users) < 50% of avg(7d)"
    duration: "30m"
    severity: "warning"
    channels: ["slack", "email"]
```

#### 监控仪表盘设计
```javascript
// monitoring/dashboard.js
export const dashboardConfig = {
  title: "AP 系统监控仪表盘",
  
  panels: [
    {
      title: "系统概览",
      type: "stats",
      metrics: [
        { name: "总请求数", query: "sum(api_requests_total)" },
        { name: "活跃用户", query: "count(unique_users)" },
        { name: "错误率", query: "rate(api_errors)" },
        { name: "平均响应时间", query: "avg(api_response_time)" }
      ]
    },
    
    {
      title: "API 性能趋势",
      type: "timeseries",
      metrics: [
        { name: "响应时间", query: "avg(api_response_time)" },
        { name: "请求量", query: "rate(api_requests_total)" },
        { name: "错误率", query: "rate(api_errors)" }
      ],
      timeRange: "24h"
    },
    
    {
      title: "数据库性能",
      type: "timeseries",
      metrics: [
        { name: "查询时间", query: "avg(db_query_duration)" },
        { name: "连接数", query: "count(db_connections)" },
        { name: "慢查询", query: "count(slow_queries)" }
      ],
      timeRange: "24h"
    },
    
    {
      title: "用户活动",
      type: "heatmap",
      metrics: [
        { name: "用户活跃度", query: "count(user_actions) by hour" }
      ],
      timeRange: "7d"
    },
    
    {
      title: "错误分布",
      type: "pie",
      metrics: [
        { name: "错误类型", query: "count(errors) by type" }
      ],
      timeRange: "24h"
    }
  ]
};
```

### 备份和恢复策略

#### 自动备份脚本
```bash
#!/bin/bash
# scripts/backup.sh

set -e

ENVIRONMENT=${1:-production}
RETENTION_DAYS=${2:-30}

echo "💾 开始备份 $ENVIRONMENT 环境数据..."

# 1. 创建时间戳
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="auto-backup-$TIMESTAMP"

# 2. 备份 D1 数据库
echo "🗄️ 备份 D1 数据库..."
wrangler d1 backup create "ap-${ENVIRONMENT}-db" --name "$BACKUP_NAME"

# 3. 导出数据到外部存储
echo "📤 导出数据到外部存储..."
wrangler d1 export "ap-${ENVIRONMENT}-db" --output "/tmp/db-export-$TIMESTAMP.sql"

# 4. 上传到 AWS S3（或其他云存储）
if [ -n "$AWS_S3_BUCKET" ]; then
    echo "☁️ 上传到 S3..."
    aws s3 cp "/tmp/db-export-$TIMESTAMP.sql" \
        "s3://$AWS_S3_BUCKET/backups/$ENVIRONMENT/db-export-$TIMESTAMP.sql"
    
    # 清理本地文件
    rm "/tmp/db-export-$TIMESTAMP.sql"
fi

# 5. 清理过期备份
echo "🧹 清理过期备份..."
CUTOFF_DATE=$(date -d "$RETENTION_DAYS days ago" +%Y%m%d)

# 列出并删除过期的 Cloudflare 备份
wrangler d1 backup list "ap-${ENVIRONMENT}-db" --json | \
    jq -r ".[] | select(.created_at < \"$CUTOFF_DATE\") | .name" | \
    while read -r backup_name; do
        echo "🗑️ 删除过期备份: $backup_name"
        wrangler d1 backup delete "ap-${ENVIRONMENT}-db" "$backup_name"
    done

# 6. 验证备份完整性
echo "✅ 验证备份完整性..."
BACKUP_SIZE=$(wrangler d1 backup list "ap-${ENVIRONMENT}-db" --json | \
    jq -r ".[] | select(.name == \"$BACKUP_NAME\") | .size")

if [ "$BACKUP_SIZE" -gt 0 ]; then
    echo "✅ 备份创建成功: $BACKUP_NAME (大小: $BACKUP_SIZE bytes)"
else
    echo "❌ 备份验证失败"
    exit 1
fi

echo "🎉 备份完成！"
```

#### 恢复流程脚本
```bash
#!/bin/bash
# scripts/restore.sh

set -e

ENVIRONMENT=${1:-staging}
BACKUP_NAME=${2}

if [ -z "$BACKUP_NAME" ]; then
    echo "❌ 请指定备份名称"
    echo "用法: $0 <environment> <backup_name>"
    exit 1
fi

echo "🔄 开始恢复 $ENVIRONMENT 环境数据..."

# 1. 确认操作
echo "⚠️ 警告: 此操作将覆盖 $ENVIRONMENT 环境的所有数据"
read -p "确认继续? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ 操作已取消"
    exit 1
fi

# 2. 创建当前数据的备份
echo "💾 创建当前数据备份..."
CURRENT_BACKUP="pre-restore-$(date +%Y%m%d-%H%M%S)"
wrangler d1 backup create "ap-${ENVIRONMENT}-db" --name "$CURRENT_BACKUP"

# 3. 执行恢复
echo "🔄 执行数据恢复..."
wrangler d1 backup restore "ap-${ENVIRONMENT}-db" "$BACKUP_NAME"

# 4. 验证恢复结果
echo "✅ 验证恢复结果..."
HEALTH_URL="https://api-$ENVIRONMENT.ap.example.com/health"
if curl -f "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ 恢复成功，系统正常运行"
else
    echo "❌ 恢复后系统异常，请检查"
    exit 1
fi

# 5. 运行数据一致性检查
echo "🔍 运行数据一致性检查..."
npm run "test:data-integrity:$ENVIRONMENT"

echo "🎉 恢复完成！"
echo "📝 当前数据已备份为: $CURRENT_BACKUP"
```

#### 定时备份配置
```yaml
# .github/workflows/backup.yml
name: Automated Backup

on:
  schedule:
    # 每天凌晨 2 点执行备份
    - cron: '0 2 * * *'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to backup'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  backup:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Wrangler
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          
      - name: Configure AWS CLI
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
          
      - name: Run backup
        run: |
          chmod +x scripts/backup.sh
          ./scripts/backup.sh ${{ github.event.inputs.environment || 'production' }}
          
      - name: Notify backup status
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#ops'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 性能优化配置

#### Cloudflare 缓存策略
```javascript
// workers/src/cache.js
export class CacheManager {
  constructor() {
    this.defaultTTL = 300; // 5分钟
    this.longTTL = 3600;   // 1小时
  }

  // 设置缓存策略
  getCacheHeaders(path, method) {
    // API 数据缓存策略
    if (path.startsWith('/api/')) {
      if (method === 'GET') {
        if (path.includes('/students/') || path.includes('/classes/')) {
          return {
            'Cache-Control': `public, max-age=${this.defaultTTL}`,
            'Vary': 'Authorization'
          };
        }
        
        if (path.includes('/analytics/') || path.includes('/reports/')) {
          return {
            'Cache-Control': `public, max-age=${this.longTTL}`,
            'Vary': 'Authorization'
          };
        }
      }
      
      // POST/PUT/DELETE 不缓存
      return {
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      };
    }

    // 静态资源缓存策略
    if (path.match(/\.(js|css|png|jpg|svg|woff2?)$/)) {
      return {
        'Cache-Control': `public, max-age=${this.longTTL * 24}`, // 24小时
        'Vary': 'Accept-Encoding'
      };
    }

    // 默认策略
    return {
      'Cache-Control': `public, max-age=${this.defaultTTL}`
    };
  }

  // 缓存失效
  async invalidateCache(patterns) {
    for (const pattern of patterns) {
      await caches.default.delete(pattern);
    }
  }
}
```

#### 数据库查询优化
```sql
-- database/optimizations.sql

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_learning_records_student_topic 
ON learning_records(student_id, topic);

CREATE INDEX IF NOT EXISTS idx_learning_records_timestamp 
ON learning_records(created_at);

CREATE INDEX IF NOT EXISTS idx_concept_mastery_student_concept 
ON concept_mastery(student_id, concept_id);

CREATE INDEX IF NOT EXISTS idx_grades_student_timestamp 
ON grades(student_id, created_at);

-- 创建视图简化复杂查询
CREATE VIEW IF NOT EXISTS student_progress_summary AS
SELECT 
    s.id as student_id,
    s.name as student_name,
    c.id as class_id,
    c.name as class_name,
    COUNT(DISTINCT lr.topic) as topics_studied,
    COUNT(DISTINCT lr.concept) as concepts_learned,
    AVG(cm.mastery_score) as average_mastery,
    MAX(lr.created_at) as last_activity
FROM students s
JOIN classes c ON s.class_id = c.id
LEFT JOIN learning_records lr ON s.id = lr.student_id
LEFT JOIN concept_mastery cm ON s.id = cm.student_id
GROUP BY s.id, s.name, c.id, c.name;

-- 创建物化视图（如果 D1 支持）
-- CREATE MATERIALIZED VIEW daily_activity_summary AS
-- SELECT 
--     DATE(created_at) as activity_date,
--     COUNT(DISTINCT student_id) as active_students,
--     COUNT(*) as total_activities,
--     COUNT(DISTINCT topic) as topics_covered
-- FROM learning_records
-- GROUP BY DATE(created_at);
```

### 安全配置

#### Cloudflare 安全规则
```javascript
// workers/src/security.js
export class SecurityManager {
  constructor(env) {
    this.env = env;
    this.rateLimits = new Map();
  }

  // 速率限制
  async checkRateLimit(ip, endpoint) {
    const key = `${ip}:${endpoint}`;
    const now = Date.now();
    const windowMs = 60000; // 1分钟窗口
    const maxRequests = this.getMaxRequests(endpoint);

    const requests = this.rateLimits.get(key) || [];
    const validRequests = requests.filter(time => now - time < windowMs);

    if (validRequests.length >= maxRequests) {
      throw new Error('Rate limit exceeded');
    }

    validRequests.push(now);
    this.rateLimits.set(key, validRequests);
  }

  getMaxRequests(endpoint) {
    if (endpoint.startsWith('/api/auth/')) return 5;   // 认证接口限制更严格
    if (endpoint.startsWith('/api/upload/')) return 10; // 上传接口
    return 100; // 默认限制
  }

  // 输入验证和清理
  sanitizeInput(input, type) {
    if (typeof input !== 'string') return input;

    switch (type) {
      case 'email':
        return input.toLowerCase().trim();
      case 'name':
        return input.trim().replace(/[<>]/g, '');
      case 'id':
        return input.replace(/[^a-zA-Z0-9_-]/g, '');
      default:
        return input.trim();
    }
  }

  // CORS 配置
  getCORSHeaders(origin) {
    const allowedOrigins = [
      'https://ap.example.com',
      'https://teacher.ap.example.com',
      'https://staging-ap.example.com'
    ];

    if (allowedOrigins.includes(origin)) {
      return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400'
      };
    }

    return {};
  }
}
```

### 运维文档模板

#### 故障处理手册
```markdown
# AP 系统故障处理手册

## 常见故障及处理方法

### 1. API 响应缓慢
**症状**: API 响应时间 > 2秒
**可能原因**: 
- 数据库查询缓慢
- Workers 冷启动
- 网络延迟

**处理步骤**:
1. 检查 Cloudflare Analytics 确认问题范围
2. 查看数据库慢查询日志
3. 检查 Workers 执行时间
4. 必要时重启 Workers 实例

### 2. 数据库连接失败
**症状**: 500 错误，数据库连接超时
**可能原因**:
- D1 服务异常
- 连接池耗尽
- 网络问题

**处理步骤**:
1. 检查 Cloudflare 服务状态
2. 重启 Workers 实例
3. 检查数据库配置
4. 联系 Cloudflare 支持

### 3. 前端页面无法访问
**症状**: 404 或白屏
**可能原因**:
- Pages 部署失败
- DNS 解析问题
- CDN 缓存问题

**处理步骤**:
1. 检查 Pages 部署状态
2. 验证 DNS 配置
3. 清除 CDN 缓存
4. 重新部署应用

## 紧急联系方式
- 技术负责人: [联系方式]
- Cloudflare 支持: [支持渠道]
- 团队 Slack: #ops-emergency
```

### 注意事项
- 确保所有敏感信息（API 密钥、数据库连接字符串）通过环境变量管理
- 定期更新依赖包和安全补丁
- 建立完善的监控和告警机制，及时发现和处理问题
- 制定详细的灾难恢复计划，定期进行演练
- 保持文档更新，确保团队成员了解最新的运维流程
- 考虑多地域部署，提高系统可用性和性能
- 实施蓝绿部署或金丝雀发布，降低部署风险