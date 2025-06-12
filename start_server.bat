@echo off
:: 设置控制台代码页为 UTF-8
chcp 65001 > nul

echo 启动 Enhanced Interactive Feedback MCP...

:: 获取脚本所在目录的绝对路径
set "SCRIPT_DIR=%~dp0"

:: 切换到脚本所在目录
cd /d "%SCRIPT_DIR%"

:: 创建日志目录
if not exist "logs" mkdir logs

:: 检查虚拟环境是否存在，如果不存在则创建
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
    call .\\.venv\\Scripts\\activate.bat
    echo 安装依赖...
    pip install -r requirements.txt
) else (
    :: 激活虚拟环境
    call .\\.venv\\Scripts\\activate.bat
)

:: 首先启动MCP服务器
echo 启动 MCP 服务器...
start cmd /c "chcp 65001 > nul && .\.venv\Scripts\python.exe enhanced_mcp_server.py"

:: 等待服务器启动
echo 等待服务器启动...
timeout /t 3

:: 运行GUI界面
echo 启动 GUI 和 Web 界面...
start cmd /c "chcp 65001 > nul && .\.venv\Scripts\python.exe gui_web_interfaces.py --interface both"

echo 启动过程完成

:: 如果只想启动GUI界面，可以使用以下命令
:: python gui_web_interfaces.py --interface gui

:: 如果只想启动Web界面，可以使用以下命令
:: python gui_web_interfaces.py --interface web 