#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查 MCP 模块内容
"""

import mcp
import inspect

# 打印 mcp 模块的所有属性
print("MCP 模块属性:")
for attr_name in dir(mcp):
    if not attr_name.startswith("_"):  # 排除私有属性
        attr = getattr(mcp, attr_name)
        print(f"  {attr_name}: {type(attr).__name__}")

# 检查是否有 client 相关模块
if hasattr(mcp, "client"):
    print("\nMCP client 模块属性:")
    client = mcp.client
    for attr_name in dir(client):
        if not attr_name.startswith("_"):
            attr = getattr(client, attr_name)
            print(f"  {attr_name}: {type(attr).__name__}") 