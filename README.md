# AP CLI - 智能学习助手

一个基于AI的命令行学习工具，帮助用户通过"解释-生成-测验"的完整学习循环来掌握新概念。

## ✨ 核心功能

- **🤔 智能解释 (`ap e`)**: 使用DeepSeek AI生成概念的详细Markdown解释文档
- **📝 自动出题 (`ap g`)**: 基于解释文档智能生成YAML格式的选择题测验
- **🎯 交互测验 (`ap q`)**: 命令行交互式测验，实时反馈和结果统计
- **🚀 一键学习 (`ap s`)**: 完整学习流程自动化，从解释到测验一步到位

## 🛠️ 技术栈

- **Python 3.8+** - 核心开发语言
- **Typer** - 现代化CLI框架，支持类型提示
- **OpenAI SDK** - DeepSeek API集成
- **python-dotenv** - 环境变量安全管理
- **PyYAML** - YAML格式数据处理

## 🚀 快速开始

### 自动化安装（推荐）

**Windows 用户：**
```bash
# 双击运行或在命令行执行
init.bat
```

**Linux/Mac 用户：**
```bash
# 给脚本执行权限并运行
chmod +x init.sh
./init.sh
```

### 手动安装

1. **克隆项目并进入目录**
   ```bash
   git clone <repository-url>
   cd ap
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   ```

3. **激活虚拟环境**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **安装CLI工具**
   ```bash
   pip install -e .
   ```

6. **配置API密钥**
   ```bash
   # 复制环境变量示例文件
   cp .env.example .env
   
   # 编辑.env文件，填入您的DeepSeek API密钥
   # DEEPSEEK_API_KEY=your_actual_api_key_here
   ```

## 📖 使用指南

### 基础命令

```bash
# 查看帮助
ap --help

# 生成概念解释
ap e "机器学习"

# 基于解释生成测验题目
ap g "机器学习"

# 开始交互式测验
ap q "机器学习"

# 一键完成完整学习流程
ap s "机器学习"
```

### 详细使用说明

#### 1. 生成概念解释 (`ap e`)

```bash
ap e "深度学习"
```

这将：
- 调用DeepSeek AI生成详细的概念解释
- 保存为结构化的Markdown文档到 `workspace/explanation/深度学习.md`
- 包含定义、原理、示例、优缺点和类比等完整内容

#### 2. 生成测验题目 (`ap g`)

```bash
ap g "深度学习"
```

这将：
- 读取之前生成的解释文档
- 基于内容智能生成5道选择题
- 保存为YAML格式到 `workspace/quizzes/深度学习.yml`

#### 3. 交互式测验 (`ap q`)

```bash
ap q "深度学习"
```

这将：
- 加载测验题目并开始交互式问答
- 提供实时反馈和正确答案
- 计算准确率并保存结果到 `workspace/results/`

#### 4. 完整学习流程 (`ap s`)

```bash
ap s "深度学习"
```

这将自动执行：
1. 生成概念解释文档
2. 基于解释生成测验题目
3. 启动交互式测验
4. 保存完整的学习记录

### 替代使用方式

如果遇到Typer相关问题，可以使用简化版本：

```bash
# 使用简化版本生成解释
python main_simple.py e "概念名称"

# 使用完整版本（推荐）
python main.py e "概念名称"
```

## 📁 项目结构

```
ap/
├── .env                    # API密钥配置（需手动创建）
├── .env.example           # 环境变量示例
├── .gitignore             # Git忽略文件
├── README.md              # 项目说明文档
├── requirements.txt       # Python依赖包
├── setup.py              # 项目安装配置
├── init.bat              # Windows自动化安装脚本
├── init.sh               # Linux/Mac自动化安装脚本
├── setup_env.py          # 环境验证脚本
├── main.py               # 完整版主程序（Typer）
├── main_simple.py        # 简化版主程序
├── ap/                   # 核心包目录
│   ├── __init__.py
│   └── cli.py           # CLI命令实现
├── dev/                  # 开发文档
│   ├── 全局文档.md
│   └── task*.md
└── workspace/            # 生成内容存储目录
    ├── explanation/      # 概念解释文档
    ├── quizzes/         # 测验题目文件
    └── results/         # 测验结果记录
```

## 🔧 环境验证

运行环境检查脚本确保配置正确：

```bash
python setup_env.py
```

该脚本将检查：
- Python版本兼容性
- 虚拟环境状态
- 依赖包安装情况
- API密钥配置
- CLI命令可用性

## 📊 功能状态

- ✅ **概念解释生成** - 完全实现
- ✅ **测验题目生成** - 完全实现  
- ✅ **交互式测验** - 完全实现
- ✅ **完整学习流程** - 完全实现
- ✅ **结果统计保存** - 完全实现

## 🔍 故障排除

### 常见问题

1. **环境变量未找到**
   ```bash
   # 确保.env文件存在且包含正确的API密钥
   cp .env.example .env
   # 编辑.env文件填入真实的API密钥
   ```

2. **Typer相关错误**
   ```bash
   # 使用简化版本
   python main_simple.py e "概念名称"
   ```

3. **依赖安装失败**
   ```bash
   # 升级pip并重新安装
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **CLI命令不可用**
   ```bash
   # 重新安装包
   pip install -e .
   ```

### 获取帮助

- 查看命令帮助：`ap --help`
- 查看特定命令帮助：`ap e --help`
- 运行环境检查：`python setup_env.py`

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 作者

- **AP CLI Team** - *初始开发* - yangjh@xbmu.edu.cn

---

**享受智能化的学习体验！** 🎓✨# Test comment
