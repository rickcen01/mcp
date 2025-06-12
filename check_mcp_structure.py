#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查 MCP 包结构
"""

import inspect
import pkgutil
import sys
import os

def explore_package(package_name):
    """探索包结构"""
    try:
        package = __import__(package_name)
        print(f"包 {package_name} 已成功导入")
        
        # 打印包路径
        print(f"包路径: {package.__path__}")
        
        # 列出包中的所有模块
        print(f"\n{package_name} 包中的模块:")
        for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
            print(f"  {'[包]' if is_pkg else '[模块]'} {name}")
            
            # 如果是子包，递归探索
            if is_pkg:
                explore_package(f"{package_name}.{name}")
        
        # 尝试导入客户端模块
        try:
            client_module = __import__(f"{package_name}.client", fromlist=["*"])
            print(f"\n{package_name}.client 模块内容:")
            for name, obj in inspect.getmembers(client_module):
                if not name.startswith("_"):  # 排除私有成员
                    print(f"  {name}: {type(obj).__name__}")
        except ImportError as e:
            print(f"无法导入 {package_name}.client: {e}")
        
    except ImportError as e:
        print(f"无法导入包 {package_name}: {e}")

if __name__ == "__main__":
    explore_package("mcp") 