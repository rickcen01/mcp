#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本所在目录
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在，如果不存在则创建
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    # 激活虚拟环境
    source .venv/bin/activate
fi

# 首先启动MCP服务器（在后台运行）
python enhanced_mcp_server.py &

# 等待服务器启动（给服务器一些时间启动）
sleep 2

# 运行GUI界面，使用both参数同时启动GUI和Web界面
python gui_web_interfaces.py --interface both

# 如果只想启动GUI界面，可以使用以下命令
# python gui_web_interfaces.py --interface gui

# 如果只想启动Web界面，可以使用以下命令
# python gui_web_interfaces.py --interface web 