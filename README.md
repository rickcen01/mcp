# Enhanced Interactive Feedback MCP Server

A dynamic MCP server management service that creates, runs, and manages Model Context Protocol (MCP) servers dynamically. This service itself functions as an MCP server and launches/manages other MCP servers as child processes, enabling a flexible MCP ecosystem.

<a href="https://glama.ai/mcp/servers/@rickcen01/mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@rickcen01/mcp/badge" alt="Enhanced Interactive Feedback Server MCP server" />
</a>

## 🚀 Features

### 原有功能增强
- ✅ 交互式反馈机制（支持问题、确认、选择等多种类型）
- ✅ 项目级配置管理
- ✅ 跨平台支持（Windows、macOS、Linux）
- ✅ 多AI工具兼容（Cursor、Cline、Windsurf等）

### 🆕 新增功能

#### 1. 智能分析引擎
- 📊 反馈模式分析和可视化
- 🤖 基于历史数据的智能建议
- 📈 性能监控和响应时间分析
- 🎯 个性化反馈优化

#### 2. 多语言支持
- 🌐 支持中文、英文等多种语言
- 🔄 自动语言检测
- 📝 本地化反馈模板

#### 3. 团队协作
- 👥 多用户支持
- 🔐 基于角色的访问控制
- 📝 团队反馈历史共享
- 💬 协作式代码审查

#### 4. 反馈模板系统
- 📋 内置常用模板
- ✏️ 自定义模板创建
- 🔧 模板参数化支持
- 📚 模板库管理

#### 5. 增强的反馈类型
- ❓ 问题询问
- ✅ 操作确认
- 📋 选项选择
- 🔍 代码审查
- 💡 建议提供
- ⚠️ 错误报告

#### 6. 通知和提醒
- 🔔 多渠道通知（控制台、文件、Webhook）
- ⏰ 优先级管理
- 🎵 声音提醒
- 📱 移动端推送（计划中）

#### 7. 插件系统
- 🔌 Slack集成
- 💬 Discord集成
- 📧 邮件通知
- 🎫 Jira集成

## 📦 Installation

### 快速安装
```bash
# 下载安装脚本
curl -LsSf https://github.com/your-repo/enhanced-feedback-mcp/install.sh | sh

# 或手动安装
git clone https://github.com/your-repo/enhanced-feedback-mcp.git
cd enhanced-feedback-mcp
chmod +x install.sh
./install.sh
```

### 手动安装
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/enhanced-feedback-mcp.git
cd enhanced-feedback-mcp

# 2. 安装依赖
uv sync

# 3. 运行服务器
uv run server.py
```

## ⚙️ Configuration

### MCP配置示例（Cursor）
```json
{
  "mcpServers": {
    "enhanced-interactive-feedback-mcp": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/enhanced-feedback-mcp",
        "run", "server.py"
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
```

### 自定义提示词
```
在完成任何任务之前，请务必调用 interactive_feedback MCP工具来获取用户反馈。
使用中文进行交互，并根据任务类型选择合适的 feedback_type。
如果反馈为空，可以结束请求，但不要循环调用。
```

## 🛠️ Usage Examples

### 基础反馈
```python
# AI助手调用示例
interactive_feedback(
    project_directory="/path/to/project",
    message="我已经实现了用户登录功能，需要您确认是否符合要求？",
    feedback_type="confirmation",
    language="zh",
    priority="medium"
)
```

### 代码审查
```python
interactive_feedback(
    project_directory="/path/to/project", 
    message="请审查这个新增的用户认证模块",
    feedback_type="code_review",
    language="zh",
    tags=["authentication", "security"],
    priority="high"
)
```

### 错误处理
```python
execute_with_feedback(
    command="npm test",
    project_directory="/path/to/project",
    require_confirmation=True,
    language="zh"
)
```

### 获取分析报告
```python
get_feedback_analytics(
    project_directory="/path/to/project",
    days=30
)
```

## 📊 Analytics Dashboard

增强版提供详细的分析功能：

- 📈 反馈频率趋势
- ⏱️ 平均响应时间
- 🏷️ 常用标签分析
- 🎯 智能建议准确性
- 👥 团队协作统计

## 🔧 Advanced Features

### 自定义模板
```yaml
# templates/custom_template.yaml
type: "custom"
content:
  en: "Custom template: {message}"
  zh: "自定义模板：{message}"
```

### 插件开发
```python
# plugins/custom_plugin.py
class CustomPlugin:
    def on_feedback_received(self, feedback):
        # 自定义处理逻辑
        pass
```

### Webhook集成
```yaml
# 配置Webhook通知
notifications:
  webhook:
    url: "https://your-webhook.com/feedback"
    headers:
      Authorization: "Bearer your-token"
```

## 🤝 Contributing

欢迎贡献代码和建议！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 License

MIT License - 详见 LICENSE 文件

## 🙏 Acknowledgments

基于原始项目 [interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp) 
由 [@fabiomlferreira](https://x.com/fabiomlferreira) 开发

增强功能由 AI 辅助开发完成