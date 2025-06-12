# install.sh - 安装脚本
#!/bin/bash

echo "🚀 Enhanced Interactive Feedback MCP Server Installation"
echo "======================================================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )[0-9]+\.[0-9]+')
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# 检查uv包管理器
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✅ uv package manager ready"

# 创建项目目录
project_dir="$HOME/.local/share/enhanced-feedback-mcp"
mkdir -p "$project_dir"
cd "$project_dir"

echo "📁 Project directory created: $project_dir"

# 创建虚拟环境和安装依赖
echo "📦 Setting up virtual environment and dependencies..."
uv venv venv
source venv/bin/activate

# 安装基础依赖
uv pip install mcp fastmcp PyYAML

# 创建配置文件
echo "⚙️ Creating configuration files..."
cat > enhanced_feedback_config.yaml << 'EOF'
server:
  name: "enhanced-interactive-feedback-mcp"
  version: "2.0.0"
  timeout: 600
  
language:
  default: "en"
  supported: ["en", "zh"]
  
analytics:
  enabled: true
  retention_days: 365
  
collaboration:
  enabled: true
  
notifications:
  enabled: true
  channels: ["console"]
  
templates:
  directory: "templates"
  custom_enabled: true
EOF

# 创建启动脚本
echo "🔧 Creating startup script..."
cat > start_server.sh << 'EOF'
#!/bin/bash
cd "$HOME/.local/share/enhanced-feedback-mcp"
source venv/bin/activate
python server.py "$@"
EOF

chmod +x start_server.sh

# 创建MCP配置示例
echo "📝 Creating MCP configuration example..."
cat > mcp_config_example.json << 'EOF'
{
  "mcpServers": {
    "enhanced-interactive-feedback-mcp": {
      "command": "bash",
      "args": [
        "-c",
        "cd $HOME/.local/share/enhanced-feedback-mcp && source venv/bin/activate && python server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback",
        "get_feedback_analytics", 
        "create_feedback_template",
        "execute_with_feedback"
      ]
    }
  }
}
EOF

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the server.py file to: $project_dir/server.py"
echo "2. Start the server: $project_dir/start_server.sh"
echo "3. Configure your AI assistant to use the MCP server"
echo "4. Example MCP configuration saved to: $project_dir/mcp_config_example.json"
echo ""
echo "🔧 Configuration file location: $project_dir/enhanced_feedback_config.yaml"
echo "📊 Data will be stored in: $HOME/.enhanced_feedback_mcp/"
echo ""
echo "🌐 For web interface (optional): uv pip install fastapi uvicorn"
echo "🖥️  For GUI interface (optional): uv pip install PyQt6"
