"""
Example Plugin for Enhanced Interactive Feedback MCP
"""

from typing import Dict, Any

class ExamplePlugin:
    """示例插件，展示插件系统的基本用法"""
    
    def __init__(self):
        self.name = "example_plugin"
        self.version = "1.0.0"
        self.description = "示例插件，用于展示插件系统的基本功能"
    
    def initialize(self, mcp_instance: Any) -> bool:
        """初始化插件"""
        print(f"[{self.name}] 插件已初始化")
        return True
    
    def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理反馈数据"""
        # 这里可以添加对反馈数据的处理逻辑
        feedback_data["processed_by_plugin"] = self.name
        return feedback_data
    
    def shutdown(self) -> None:
        """关闭插件"""
        print(f"[{self.name}] 插件已关闭")

# 插件入口点
def get_plugin_instance():
    """返回插件实例"""
    return ExamplePlugin() 