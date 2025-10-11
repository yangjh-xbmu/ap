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
source .venv/Scripts/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装成功"

echo ""
echo "📋 步骤 3: 运行初始化脚本..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "⚠️  初始化脚本检测到一些问题，但可以继续使用"
fi

ap i

echo ""
echo "🎉 自动化初始化完成！"

ap --help
