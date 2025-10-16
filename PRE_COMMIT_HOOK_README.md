# Pre-commit Hook 自动版本管理

这个pre-commit hook使用DeepSeek AI智能分析Git提交内容，自动更新`setup.py`中的版本号。

## 🚀 快速安装

### 方法一：使用安装脚本（推荐）

```bash
python install-hook.py
```

### 方法二：手动安装

```bash
# 1. 复制hook脚本到Git hooks目录
cp pre-commit-hook.py .git/hooks/pre-commit

# 2. 给脚本执行权限（Linux/Mac）
chmod +x .git/hooks/pre-commit

# 3. Windows用户可以跳过权限设置
```

## 📋 工作原理

1. **提交拦截**：每次执行`git commit`时自动触发
2. **变更分析**：收集暂存区的文件变更和diff内容
3. **AI判断**：使用DeepSeek AI分析变更类型和影响
4. **版本更新**：根据分析结果自动更新版本号
5. **自动暂存**：将更新后的`setup.py`添加到当前提交

## 🎯 版本更新规则

| 更新类型 | 版本变化 | 触发条件 | 示例 |
|---------|---------|---------|------|
| **MAJOR** | x.0.0.0 | 重大架构变更、破坏性API变更 | 1.0.0.0 → 2.0.0.0 |
| **MINOR** | x.y.0.0 | 新增功能、新命令、重要改进 | 1.0.0.0 → 1.1.0.0 |
| **PATCH** | x.y.z.0 | Bug修复、小改进、性能优化 | 1.0.0.0 → 1.0.1.0 |
| **BUILD** | x.y.z.w | 文档更新、注释修改、格式化 | 1.0.0.0 → 1.0.0.1 |
| **NONE** | 不变 | 仅Git相关文件变更 | 1.0.0.0 → 1.0.0.0 |

## 🔧 配置要求

### 必需配置

1. **DeepSeek API密钥**
   ```bash
   # 在.env文件中配置
   DEEPSEEK_API_KEY=your_api_key_here
   ```

2. **Python依赖**
   ```bash
   pip install openai python-dotenv
   ```

### 项目结构要求

```
your-project/
├── .env                    # API密钥配置
├── setup.py               # 包含version字段
├── pre-commit-hook.py     # Hook脚本
├── install-hook.py        # 安装脚本
└── .git/hooks/pre-commit  # 安装后的hook
```

## 📖 使用示例

### 正常提交流程

```bash
# 1. 修改代码
echo "新功能代码" >> ap/cli.py

# 2. 暂存变更
git add ap/cli.py

# 3. 提交（hook自动运行）
git commit -m "添加新的学习功能"

# Hook输出示例：
```bash
# [INFO] 运行pre-commit hook...
# [AI] 使用AI分析变更内容...
# [ANALYSIS] 分析结果：MINOR
# [UPDATE] 版本更新：1.0.0 -> 1.1.0
# [SUCCESS] setup.py版本号已更新
# [SUCCESS] setup.py已添加到暂存区
# [COMPLETE] Pre-commit hook执行完成
```

### 跳过Hook（紧急情况）

```bash
# 使用--no-verify跳过所有pre-commit hooks
git commit --no-verify -m "紧急修复"
```

## 🛠️ 管理命令

### 安装/卸载Hook

```bash
# 交互式安装/卸载
python install-hook.py

# 手动卸载
rm .git/hooks/pre-commit
```

### 测试Hook

```bash
# 创建测试提交
echo "test" >> test.txt
git add test.txt

# 提交时观察hook行为
git commit -m "测试提交"
```

## 🔍 故障排除

### 常见问题

1. **API密钥未配置**
   ```
   错误：未找到DEEPSEEK_API_KEY环境变量
   ```
   **解决**：在`.env`文件中配置API密钥

2. **Hook权限问题（Linux/Mac）**
   ```
   .git/hooks/pre-commit: Permission denied
   ```
   **解决**：`chmod +x .git/hooks/pre-commit`

3. **找不到setup.py**
   ```
   错误：找不到setup.py文件
   ```
   **解决**：确保在项目根目录运行，且存在setup.py文件

4. **版本号格式错误**
   ```
   错误：版本号格式不正确: 1.0
   ```
   **解决**：确保setup.py中版本号为x.y.z.w格式（四位版本号）

### 调试模式

如果需要调试hook行为，可以在hook脚本中添加调试输出：

```python
# 在pre-commit-hook.py中添加
print(f"调试：暂存文件 = {staged_files}")
print(f"调试：变更内容长度 = {len(staged_diff)}")
```

## 🎨 自定义配置

### 修改版本更新规则

编辑`pre-commit-hook.py`中的`analyze_changes_with_llm`函数，调整AI提示词：

```python
prompt = f"""
自定义的分析规则...
"""
```

### 修改版本号格式

如果使用不同的版本号格式，修改`increment_version`函数：

```python
def increment_version(current_version, update_type):
    # 自定义版本号处理逻辑
    pass
```

## 📊 Hook执行日志

Hook执行时会输出详细日志：

```
[INFO] 运行pre-commit hook...           # 开始执行
[AI] 使用AI分析变更内容...            # AI分析阶段
[ANALYSIS] 分析结果：BUILD                  # 分析结果（新增BUILD类型）
[UPDATE] 版本更新：1.0.0.0 -> 1.0.0.1    # 版本变更（四位格式）
[SUCCESS] setup.py版本号已更新             # 文件更新成功
[SUCCESS] setup.py已添加到暂存区           # 自动暂存
[COMPLETE] Pre-commit hook执行完成          # 执行完成
```

## 🔒 安全注意事项

1. **API密钥安全**：确保`.env`文件在`.gitignore`中
2. **网络依赖**：Hook需要网络连接访问DeepSeek API
3. **失败处理**：API失败时hook会跳过版本更新，不会阻止提交

## 🤝 贡献

如果您有改进建议或发现问题，欢迎：

1. 提交Issue报告问题
2. 提交Pull Request改进功能
3. 分享使用经验和最佳实践

---

**享受智能化的版本管理！** 🚀✨