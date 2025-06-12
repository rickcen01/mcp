#!/usr/bin/env python3
"""
测试脚本，用于验证环境配置是否正确
"""
import sys
import os

def main():
    print("Python 版本:", sys.version)
    print("当前工作目录:", os.getcwd())
    
    # 测试导入必要的模块
    try:
        import mcp
        print("成功导入 mcp 模块")
    except ImportError as e:
        print(f"导入 mcp 模块失败: {e}")
    
    try:
        from mcp.server.fastmcp import FastMCP
        print("成功导入 FastMCP")
    except ImportError as e:
        print(f"导入 FastMCP 失败: {e}")
    
    try:
        import yaml
        print("成功导入 yaml 模块")
    except ImportError as e:
        print(f"导入 yaml 模块失败: {e}")
    
    # 测试其他依赖
    modules_to_test = [
        "sqlite3", "PyQt6", "fastapi", "uvicorn", 
        "matplotlib", "plotly", "websockets"
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"成功导入 {module} 模块")
        except ImportError as e:
            print(f"导入 {module} 模块失败: {e}")
    
    print("\n测试完成")

if __name__ == "__main__":
    main() 