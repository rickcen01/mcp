#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI and Web Interfaces for Enhanced Interactive Feedback MCP Server

This module provides GUI and Web interfaces for the Enhanced Interactive Feedback MCP Server.
"""

import os
import sys
import logging
import json
import argparse
import threading
import webbrowser
from typing import Dict, Any, List, Optional, Union, Callable
import locale
import mcp

# 确保正确处理 UTF-8 编码
if sys.platform == 'win32':
    # Windows 平台设置控制台编码
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)
    kernel32.SetConsoleOutputCP(65001)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("enhanced-feedback-mcp-interfaces")

# Check dependencies for GUI interface
GUI_AVAILABLE = False
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
        QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
        QDialog, QFormLayout, QCheckBox, QSpinBox
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QIcon, QAction
    GUI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"PyQt6 not available: {e}. GUI interface will not be available.")
    logger.info("To enable GUI interface, install: pip install PyQt6")

# Check dependencies for Web interface
WEB_AVAILABLE = False
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from pydantic import BaseModel
    WEB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"FastAPI/Uvicorn not available: {e}. Web interface will not be available.")
    logger.info("To enable Web interface, install: pip install fastapi uvicorn")

# Check dependencies for charts
CHARTS_AVAILABLE = False
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    CHARTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Matplotlib not available: {e}. Charts will not be available.")
    logger.info("To enable charts, install: pip install matplotlib")

class MockMCPClient:
    """模拟 MCP 客户端，用于测试"""
    
    def __init__(self):
        self.logger = logging.getLogger("mock-mcp-client")
        self.logger.info("创建模拟 MCP 客户端")
    
    def call(self, tool_name, **kwargs):
        """模拟调用 MCP 工具"""
        self.logger.info(f"调用工具: {tool_name}, 参数: {kwargs}")
        
        # 返回模拟数据
        if tool_name == "enhanced_interactive_feedback":
            return {
                "logs": "",
                "interactive_feedback": "这是一个模拟的反馈响应"
            }
        elif tool_name == "enhanced_feedback_analytics":
            return {
                "patterns": {
                    "feedback_types": {"question": 5, "suggestion": 3},
                    "avg_response_time": 2.5,
                    "common_tags": {"bug": 4, "feature": 3},
                    "total_feedbacks": 8
                },
                "suggestions": ["增加更多单元测试", "改进错误处理"]
            }
        else:
            return {"status": "success", "message": f"工具 {tool_name} 调用成功"}

def create_mcp_client():
    """创建 MCP 客户端连接（现在返回模拟客户端）"""
    try:
        # 返回模拟客户端
        logger.info("创建模拟 MCP 客户端")
        return MockMCPClient()
    except Exception as e:
        logger.error(f"创建模拟 MCP 客户端失败: {e}")
        raise

class GUIInterface:
    """GUI Interface for Enhanced Feedback MCP"""
    
    def __init__(self, mcp_client):
        """Initialize the GUI interface"""
        if not GUI_AVAILABLE:
            logger.error("Cannot initialize GUI: PyQt6 not available")
            return
        
        self.mcp_client = mcp_client
        self.app = QApplication(sys.argv)
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("增强型交互反馈 MCP")
        self.main_window.setMinimumSize(800, 600)
        
        # Set up UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Add tabs
        tabs.addTab(self._create_dashboard_tab(), "仪表盘")
        tabs.addTab(self._create_feedback_tab(), "反馈")
        tabs.addTab(self._create_templates_tab(), "模板")
        tabs.addTab(self._create_analytics_tab(), "分析")
        tabs.addTab(self._create_settings_tab(), "设置")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.status_label = QLabel("就绪")
        self.main_window.statusBar().addWidget(self.status_label)
        
        # Set central widget
        self.main_window.setCentralWidget(central_widget)
        
        # Create menu bar
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Create the menu bar"""
        menu_bar = self.main_window.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("文件")
        
        exit_action = QAction("退出", self.main_window)
        exit_action.triggered.connect(self.app.quit)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self.main_window)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_dashboard_tab(self):
        """Create the dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary section
        summary_group = QWidget()
        summary_layout = QHBoxLayout(summary_group)
        
        # Stats widgets
        stats = [
            ("总反馈数", "0"),
            ("响应率", "0%"),
            ("平均响应时间", "0秒"),
            ("活跃模板", "0")
        ]
        
        for title, value in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            title_label = QLabel(title)
            value_label = QLabel(value)
            value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
            
            stat_layout.addWidget(title_label)
            stat_layout.addWidget(value_label)
            
            summary_layout.addWidget(stat_widget)
        
        layout.addWidget(summary_group)
        
        # Recent feedback section
        layout.addWidget(QLabel("最近反馈"))
        
        recent_feedback_table = QTableWidget(5, 4)
        recent_feedback_table.setHorizontalHeaderLabels(["类型", "消息", "状态", "时间"])
        recent_feedback_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(recent_feedback_table)
        
        # Chart section
        if CHARTS_AVAILABLE:
            layout.addWidget(QLabel("反馈活动"))
            
            figure = Figure(figsize=(5, 3))
            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
            
            ax = figure.add_subplot(111)
            ax.plot([0, 1, 2, 3, 4], [0, 1, 4, 9, 16])
            ax.set_ylabel('反馈数量')
            figure.tight_layout()
        else:
            layout.addWidget(QLabel("图表不可用。请安装matplotlib启用此功能。"))
        
        # Refresh button
        refresh_button = QPushButton("刷新仪表盘")
        layout.addWidget(refresh_button)
        
        return tab
    
    def _create_feedback_tab(self):
        """Create the feedback tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create feedback form
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        
        # Message field
        self.feedback_message = QTextEdit()
        form_layout.addRow("消息:", self.feedback_message)
        
        # Type field
        self.feedback_type = QComboBox()
        self.feedback_type.addItems(["问题", "确认", "选择", "代码审查", "建议", "错误报告"])
        form_layout.addRow("类型:", self.feedback_type)
        
        # Language field
        self.feedback_language = QComboBox()
        self.feedback_language.addItems(["en", "zh"])
        form_layout.addRow("语言:", self.feedback_language)
        
        # Priority field
        self.feedback_priority = QComboBox()
        self.feedback_priority.addItems(["低", "中", "高", "紧急"])
        form_layout.addRow("优先级:", self.feedback_priority)
        
        # Project field
        self.feedback_project = QLineEdit()
        form_layout.addRow("项目:", self.feedback_project)
        
        # Tags field
        self.feedback_tags = QLineEdit()
        self.feedback_tags.setPlaceholderText("逗号分隔的标签")
        form_layout.addRow("标签:", self.feedback_tags)
        
        layout.addWidget(form_group)
        
        # Send button
        send_button = QPushButton("发送反馈")
        send_button.clicked.connect(self._send_feedback)
        layout.addWidget(send_button)
        
        # History section
        layout.addWidget(QLabel("反馈历史"))
        
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["ID", "类型", "消息", "状态", "时间戳"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.history_table)
        
        return tab
    
    def _create_templates_tab(self):
        """Create the templates tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Available templates
        layout.addWidget(QLabel("可用模板"))
        
        templates_table = QTableWidget(0, 3)
        templates_table.setHorizontalHeaderLabels(["名称", "描述", "语言"])
        templates_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(templates_table)
        
        # Template creation form
        layout.addWidget(QLabel("创建新模板"))
        
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        
        # Name field
        template_name = QLineEdit()
        form_layout.addRow("名称:", template_name)
        
        # Description field
        template_description = QLineEdit()
        form_layout.addRow("描述:", template_description)
        
        # English content
        template_content_en = QTextEdit()
        form_layout.addRow("英文内容:", template_content_en)
        
        # Chinese content
        template_content_zh = QTextEdit()
        form_layout.addRow("中文内容:", template_content_zh)
        
        layout.addWidget(form_group)
        
        # Create button
        create_button = QPushButton("创建模板")
        layout.addWidget(create_button)
        
        return tab

    def _create_analytics_tab(self):
        """Create the analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Time period selection
        period_group = QWidget()
        period_layout = QHBoxLayout(period_group)
        
        period_layout.addWidget(QLabel("时间周期:"))
        
        period_combo = QComboBox()
        period_combo.addItems(["最近7天", "最近30天", "最近90天", "最近一年", "全部时间"])
        period_layout.addWidget(period_combo)
        
        period_layout.addStretch()
        
        layout.addWidget(period_group)
        
        # Charts
        if CHARTS_AVAILABLE:
            # Feedback by type chart
            layout.addWidget(QLabel("按类型划分的反馈"))
            
            type_figure = Figure(figsize=(5, 3))
            type_canvas = FigureCanvas(type_figure)
            layout.addWidget(type_canvas)
            
            # Response time chart
            layout.addWidget(QLabel("平均响应时间"))
            
            time_figure = Figure(figsize=(5, 3))
            time_canvas = FigureCanvas(time_figure)
            layout.addWidget(time_canvas)
        else:
            layout.addWidget(QLabel("图表不可用。请安装matplotlib启用此功能。"))
        
        # Stats table
        layout.addWidget(QLabel("反馈统计"))
        
        stats_table = QTableWidget(0, 3)
        stats_table.setHorizontalHeaderLabels(["指标", "值", "变化"])
        stats_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(stats_table)
        
        return tab

    def _create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Server settings
        layout.addWidget(QLabel("服务器设置"))
        
        server_form = QWidget()
        server_layout = QFormLayout(server_form)
        
        server_host = QLineEdit("localhost")
        server_layout.addRow("主机:", server_host)
        
        server_port = QSpinBox()
        server_port.setRange(1000, 65535)
        server_port.setValue(3001)
        server_layout.addRow("端口:", server_port)
        
        server_timeout = QSpinBox()
        server_timeout.setRange(1, 3600)
        server_timeout.setValue(600)
        server_layout.addRow("超时 (秒):", server_timeout)
        
        layout.addWidget(server_form)
        
        # Notification settings
        layout.addWidget(QLabel("通知设置"))
        
        notify_form = QWidget()
        notify_layout = QFormLayout(notify_form)
        
        notify_sound = QCheckBox("启用")
        notify_layout.addRow("声音:", notify_sound)
        
        notify_desktop = QCheckBox("启用")
        notify_layout.addRow("桌面:", notify_desktop)
        
        layout.addWidget(notify_form)
        
        # Save button
        save_button = QPushButton("保存设置")
        layout.addWidget(save_button)
        
        return tab

    def _send_feedback(self):
        """Send feedback using the MCP client"""
        if not self.mcp_client:
            QMessageBox.warning(self.main_window, "错误", "MCP客户端不可用")
            return
        
        # Get form values
        message = self.feedback_message.toPlainText()
        feedback_type = self.feedback_type.currentText()
        language = self.feedback_language.currentText()
        priority = self.feedback_priority.currentText()
        project = self.feedback_project.text()
        
        # Parse tags
        tags_text = self.feedback_tags.text()
        tags = [tag.strip() for tag in tags_text.split(',')] if tags_text else []
        
        # Validate
        if not message:
            QMessageBox.warning(self.main_window, "错误", "消息不能为空")
            return
        
        try:
            # Send feedback via MCP client
            # This is a mock for now; in real implementation we'd use the MCP client
            result = {
                "feedback_id": "mock-id",
                "status": "已发送"
            }
            
            QMessageBox.information(self.main_window, "成功", "反馈发送成功")
            
            # Add to history table
            self._add_feedback_to_history(result)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "错误", f"发送反馈失败: {e}")
    
    def _add_feedback_to_history(self, feedback):
        """Add a feedback item to the history table"""
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        
        self.history_table.setItem(row, 0, QTableWidgetItem(feedback["feedback_id"]))
        self.history_table.setItem(row, 1, QTableWidgetItem(self.feedback_type.currentText()))
        self.history_table.setItem(row, 2, QTableWidgetItem(self.feedback_message.toPlainText()[:30] + "..."))
        self.history_table.setItem(row, 3, QTableWidgetItem(feedback["status"]))
        self.history_table.setItem(row, 4, QTableWidgetItem("刚刚"))
    
    def _show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(
            self.main_window,
            "关于增强型反馈MCP",
            "增强型交互反馈 MCP 服务器\n版本 2.0.0\n\n"
            "一个为AI助手提供的强大用户反馈系统。"
        )
    
    def run(self):
        """运行 GUI 界面"""
        try:
            logger.info("正在显示 GUI 界面...")
            self.main_window.show()
            
            # 如果是在主线程中运行，则执行事件循环
            if threading.current_thread() is threading.main_thread():
                logger.info("在主线程中执行 GUI 事件循环")
                self.app.exec()
            else:
                logger.info("GUI 界面已在子线程中显示")
        except Exception as e:
            logger.error(f"GUI 界面运行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())


class WebInterface:
    """Web Interface for Enhanced Feedback MCP"""
    
    def __init__(self, mcp_client, host="localhost", port=8000, open_browser=True):
        """Initialize the Web interface"""
        if not WEB_AVAILABLE:
            logger.error("Cannot initialize Web interface: FastAPI/Uvicorn not available")
            return
        
        self.mcp_client = mcp_client
        self.host = host
        self.port = port
        self.open_browser = open_browser
        
        # Create FastAPI app
        self.app = FastAPI(title="Enhanced Feedback MCP", version="2.0.0")
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Set up the FastAPI routes"""
        @self.app.get("/")
        async def root():
            return {"status": "ok", "message": "Enhanced Feedback MCP Web Interface"}
        
        @self.app.get("/health")
        async def health():
            return {"status": "ok"}
        
        # API routes
        @self.app.post("/api/feedback")
        async def create_feedback(request: Dict[str, Any]):
            try:
                # In a real implementation, this would call the MCP client
                return {"feedback_id": "mock-id", "status": "sent"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/feedback/{feedback_id}")
        async def get_feedback(feedback_id: str):
            # In a real implementation, this would fetch feedback from the MCP client
            return {"feedback_id": feedback_id, "status": "sent"}
        
        @self.app.get("/api/analytics")
        async def get_analytics(days: int = 30):
            try:
                # In a real implementation, this would fetch analytics from the MCP client
                return {"total": 0, "response_rate": 0}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # WebSocket for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    # In a real implementation, this would send periodic updates
                    await websocket.send_json({"type": "ping", "timestamp": "now"})
                    await websocket.receive_text()
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.close()
    
    def run(self):
        """Run the Web interface"""
        if self.open_browser:
            threading.Thread(target=lambda: webbrowser.open(f"http://{self.host}:{self.port}")).start()
        
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Enhanced Interactive Feedback MCP GUI and Web Interfaces")
    parser.add_argument("--interface", choices=["gui", "web", "both"], default="both",
                        help="启动的界面类型: gui, web 或 both")
    args = parser.parse_args()
    
    try:
        # 创建 MCP 客户端连接
        mcp_client = create_mcp_client()
        
        # 根据接口类型选择启动方式
        if args.interface == "gui":
            # 只启动 GUI，在主线程中运行
            if GUI_AVAILABLE:
                logger.info("在主线程中启动 GUI 界面")
                GUIInterface(mcp_client).run()
            else:
                logger.error("GUI 界面不可用，请安装 PyQt6")
                sys.exit(1)
        
        elif args.interface == "web":
            # 只启动 Web 界面，在主线程中运行
            if WEB_AVAILABLE:
                logger.info("在主线程中启动 Web 界面")
                WebInterface(mcp_client).run()
            else:
                logger.error("Web 界面不可用，请安装 FastAPI 和 Uvicorn")
                sys.exit(1)
        
        elif args.interface == "both":
            # 同时启动 GUI 和 Web 界面
            web_thread = None
            
            # 如果 GUI 可用，在主线程中运行 GUI
            if GUI_AVAILABLE:
                logger.info("准备在主线程中启动 GUI 界面")
                gui_interface = GUIInterface(mcp_client)
                
                # 如果 Web 也可用，在子线程中启动 Web
                if WEB_AVAILABLE:
                    logger.info("准备在子线程中启动 Web 界面")
                    web_interface = WebInterface(mcp_client)
                    web_thread = threading.Thread(target=web_interface.run)
                    web_thread.daemon = True
                    web_thread.start()
                    logger.info("Web 界面已在子线程中启动")
                
                # 在主线程中运行 GUI
                logger.info("在主线程中运行 GUI 界面")
                gui_interface.run()
            
            # 如果 GUI 不可用但 Web 可用，在主线程中运行 Web
            elif WEB_AVAILABLE:
                logger.info("GUI 界面不可用，在主线程中启动 Web 界面")
                WebInterface(mcp_client).run()
            
            # 如果两者都不可用，报错
            else:
                logger.error("GUI 和 Web 界面都不可用，请安装必要的依赖")
                sys.exit(1)
    
    except Exception as e:
        logger.error(f"启动界面失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()