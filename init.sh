#!/bin/bash

echo "🚀 AP CLI 自动化环境初始化脚本"
echo "==============================================="

# 检查Python是否安装
if ! command -v python &> /dev/null; then
    echo "❌ 错误：未找到Python，请先安装Python 3.10+"
    exit 1
fi

echo ""
echo "📋 步骤 1: 创建Python虚拟环境..."
python -m venv .venv
if [ $? -ne 0 ]; then
    echo "❌ 虚拟环境创建失败"
    exit 1
fi
echo "✅ 虚拟环境创建成功"

echo ""
echo "📋 步骤 2: 激活虚拟环境并安装依赖..."
source .venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装成功"

echo ""
echo "📋 步骤 3: 运行初始化脚本..."
python setup.py
if [ $? -ne 0 ]; then
    echo "⚠️  初始化脚本检测到一些问题，但可以继续使用"
fi

echo ""
echo "📋 步骤 4: 创建示例.env文件..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env文件已创建"
    echo "⚠️  请编辑.env文件并填入您的DeepSeek API密钥"
else
    echo "✅ .env文件已存在"
fi

echo ""
echo "🎉 自动化初始化完成！"
echo ""
echo "📝 使用说明:"
echo "  1. 请编辑 .env 文件，填入您的 DeepSeek API 密钥"
echo "  2. 使用命令: python main.py e \"概念名称\""
echo ""
echo "示例命令:"
echo "  python main.py e \"SOLID Principles\""
echo ""