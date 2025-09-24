# AP CLI - 命令行学习工具

一个帮助用户通过"提问-生成-测验"循环来学习新概念的命令行工具。

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

1. **创建虚拟环境**：
   ```bash
   python -m venv .venv
   ```

2. **激活虚拟环境**：
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **配置 API 密钥**：
   ```bash
   # 复制环境变量示例文件
   cp .env.example .env
   
   # 编辑 .env 文件，填入您的 DeepSeek API 密钥
   # DEEPSEEK_API_KEY=your_actual_api_key_here
   ```

## 功能特性

- **`ap e <concept>`**: 生成概念的详细 Markdown 解释文档
- **`ap g <concept>`**: 根据解释文档生成 YAML 格式的测验题目（开发中）
- **`ap q <concept>`**: 开始交互式测验（开发中）

## 使用方法

### 生成概念解释

```bash
# 使用简化版本（推荐，避免依赖问题）
python main_simple.py e "SOLID Principles"

# 或使用 Typer 版本
python main.py e "SOLID Principles"
```

这将：
- 调用 DeepSeek API 生成详细的 Markdown 解释
- 在 `workspace/solid-principles/` 目录下保存 `explanation.md` 文件
- 包含定义、原理、示例、优缺点和类比等结构化内容

### 项目结构

```
ap_cli/
├── .gitignore          # Git 忽略文件
├── .env                # API 密钥配置（需要手动创建）
├── .env.example        # 环境变量示例
├── main.py             # 主程序入口（Typer版本）
├── main_simple.py      # 简化版主程序（推荐使用）
├── setup.py            # 自动化初始化脚本
├── init.bat            # Windows 自动化安装脚本
├── init.sh             # Linux/Mac 自动化安装脚本
├── requirements.txt    # 项目依赖
├── README.md           # 项目说明
└── workspace/          # 生成内容存储目录
    └── concept-name/   # 每个概念一个文件夹
        ├── explanation.md
        ├── quiz.yml
        └── result_*.json
```

## 技术栈

- **Python 3.10+**
- **Typer**: 命令行框架（可选）
- **OpenAI**: DeepSeek API 客户端
- **python-dotenv**: 环境变量管理
- **PyYAML**: YAML 文件处理

## 开发状态

- ✅ `ap e` 命令：完成
- 🚧 `ap g` 命令：开发中
- 🚧 `ap q` 命令：开发中

## 故障排除

如果遇到 Typer 相关的错误，请使用简化版本：
```bash
python main_simple.py e "概念名称"
```

## 环境验证

运行初始化脚本检查环境配置：
```bash
python setup.py
```