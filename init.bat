@echo off
echo 🚀 AP CLI 自动化环境初始化脚本
echo ===============================================

echo.
echo 📋 步骤 1: 创建Python虚拟环境...
python -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功

echo.
echo 📋 步骤 2: 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装成功

echo.
echo 📋 步骤 3: 运行初始化脚本...
python setup.py
if %errorlevel% neq 0 (
    echo ⚠️  初始化脚本检测到一些问题，但可以继续使用
)

echo.
echo 📋 步骤 4: 创建示例.env文件...
if not exist .env (
    copy .env.example .env
    echo ✅ .env文件已创建
    echo ⚠️  请编辑.env文件并填入您的DeepSeek API密钥
) else (
    echo ✅ .env文件已存在
)

echo.
echo 🎉 自动化初始化完成！
echo.
echo 📝 使用说明:
echo   1. 请编辑 .env 文件，填入您的 DeepSeek API 密钥
echo   2. 使用命令: python main.py e "概念名称"
echo.
echo 示例命令:
echo   python main.py e "SOLID Principles"
echo.
pause