#!/usr/bin/env python3
"""
Enhanced Interactive Feedback MCP Server
增强型交互式反馈MCP服务器

Features:
- 原有的交互式反馈功能
- 多语言支持 (中文/英文)
- 反馈历史记录和分析
- 智能建议系统
- 团队协作支持
- 自定义反馈模板
- 性能监控和分析
- 插件系统
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import subprocess
import sqlite3
import hashlib
import uuid

# MCP SDK imports
from mcp.server.fastmcp import FastMCP

# Additional imports for enhanced features
import yaml
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced-feedback-mcp")

class FeedbackType(Enum):
    """反馈类型枚举"""
    QUESTION = "question"
    CONFIRMATION = "confirmation" 
    SELECTION = "selection"
    CODE_REVIEW = "code_review"
    SUGGESTION = "suggestion"
    ERROR_REPORT = "error_report"

class Priority(Enum):
    """优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class FeedbackHistory:
    """反馈历史记录数据类"""
    id: str
    timestamp: datetime
    project_path: str
    feedback_type: FeedbackType
    question: str
    response: str
    response_time: float
    ai_summary: str
    tags: List[str]
    priority: Priority
    user_id: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'feedback_type': self.feedback_type.value,
            'priority': self.priority.value
        }

class AnalyticsEngine:
    """分析引擎，用于反馈模式分析和智能建议"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    question TEXT NOT NULL,
                    response TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    ai_summary TEXT,
                    tags TEXT,
                    priority TEXT NOT NULL,
                    user_id TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    language TEXT DEFAULT 'en',
                    preferred_feedback_types TEXT,
                    notification_settings TEXT,
                    custom_templates TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_settings (
                    project_path TEXT PRIMARY KEY,
                    auto_suggestions BOOLEAN DEFAULT 1,
                    feedback_frequency TEXT DEFAULT 'normal',
                    team_members TEXT,
                    project_type TEXT
                )
            """)
    
    def save_feedback(self, feedback: FeedbackHistory):
        """保存反馈记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO feedback_history 
                (id, timestamp, project_path, feedback_type, question, response, 
                 response_time, ai_summary, tags, priority, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.id,
                feedback.timestamp.isoformat(),
                feedback.project_path,
                feedback.feedback_type.value,
                feedback.question,
                feedback.response,
                feedback.response_time,
                feedback.ai_summary,
                ','.join(feedback.tags),
                feedback.priority.value,
                feedback.user_id
            ))
    
    def get_feedback_patterns(self, project_path: str, days: int = 30) -> Dict[str, Any]:
        """分析反馈模式"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT feedback_type, response_time, tags, priority 
                FROM feedback_history 
                WHERE project_path = ? AND timestamp > ?
            """, (project_path, cutoff_date))
            
            data = cursor.fetchall()
        
        if not data:
            return {"patterns": "insufficient_data", "suggestions": []}
        
        # 分析反馈类型分布
        type_distribution = Counter(row[0] for row in data)
        
        # 分析响应时间
        response_times = [row[1] for row in data]
        avg_response_time = sum(response_times) / len(response_times)
        
        # 分析标签
        all_tags = []
        for row in data:
            if row[2]:  # tags
                all_tags.extend(row[2].split(','))
        tag_distribution = Counter(all_tags)
        
        # 生成智能建议
        suggestions = self._generate_suggestions(type_distribution, avg_response_time, tag_distribution)
        
        return {
            "patterns": {
                "feedback_types": dict(type_distribution),
                "avg_response_time": avg_response_time,
                "common_tags": dict(tag_distribution.most_common(5)),
                "total_feedbacks": len(data)
            },
            "suggestions": suggestions
        }
    
    def _generate_suggestions(self, type_dist: Counter, avg_time: float, tag_dist: Counter) -> List[str]:
        """基于模式生成智能建议"""
        suggestions = []
        
        # 基于反馈类型分布的建议
        if type_dist.get('error_report', 0) > len(type_dist) * 0.3:
            suggestions.append("项目可能存在较多错误，建议增加代码检查和测试")
        
        if type_dist.get('code_review', 0) > len(type_dist) * 0.4:
            suggestions.append("代码审查频繁，考虑设置自动化代码质量检查")
        
        # 基于响应时间的建议
        if avg_time > 60:  # 超过60秒
            suggestions.append("平均响应时间较长，考虑简化反馈问题或使用预设选项")
        elif avg_time < 5:  # 少于5秒
            suggestions.append("响应时间很快，可以考虑增加更详细的反馈问题")
        
        # 基于标签的建议
        if 'performance' in [tag for tag, _ in tag_dist.most_common(3)]:
            suggestions.append("性能问题频繁出现，建议进行性能优化专项工作")
        
        return suggestions

class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: str):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        self.load_default_templates()
    
    def load_default_templates(self):
        """加载默认模板"""
        default_templates = {
            "code_review": {
                "en": "Please review the following code changes:\n{changes}\n\nWhat are your thoughts?",
                "zh": "请审查以下代码更改：\n{changes}\n\n您有什么想法？"
            },
            "confirmation": {
                "en": "I'm about to {action}. Should I proceed?",
                "zh": "我即将{action}。是否继续？"
            },
            "error_handling": {
                "en": "An error occurred: {error}\n\nHow would you like me to handle this?",
                "zh": "发生错误：{error}\n\n您希望我如何处理？"
            },
            "suggestion": {
                "en": "I have a suggestion: {suggestion}\n\nWhat do you think?",
                "zh": "我有一个建议：{suggestion}\n\n您觉得怎么样？"
            }
        }
        
        templates_file = self.templates_dir / "default_templates.yaml"
        if not templates_file.exists():
            with open(templates_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_templates, f, default_flow_style=False, allow_unicode=True)
    
    def get_template(self, template_type: str, language: str = "en", **kwargs) -> str:
        """获取模板并格式化"""
        templates_file = self.templates_dir / "default_templates.yaml"
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            template = templates.get(template_type, {}).get(language, 
                templates.get(template_type, {}).get("en", "{message}"))
            
            return template.format(**kwargs)
        except Exception as e:
            logger.error(f"Error loading template: {e}")
            return kwargs.get('message', 'No message provided')

class EnhancedFeedbackMCP:
    """增强型反馈MCP服务器"""
    
    def __init__(self):
        self.app = FastMCP("Enhanced Interactive Feedback MCP")
        self.data_dir = Path.home() / ".enhanced_feedback_mcp"
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化组件
        self.analytics = AnalyticsEngine(str(self.data_dir / "feedback.db"))
        self.template_manager = TemplateManager(str(self.data_dir / "templates"))
        
        # 注册工具
        self._register_tools()
        
        logger.info("Enhanced Feedback MCP Server initialized")
    
    def _register_tools(self):
        """注册MCP工具"""
        
        @self.app.tool()
        def interactive_feedback(
            project_directory: str,
            message: str,
            feedback_type: str = "question",
            priority: str = "medium",
            options: Optional[List[str]] = None,
            language: str = "en",
            timeout: int = 300,
            tags: Optional[List[str]] = None,
            user_id: str = "default"
        ) -> Dict[str, Any]:
            """
            增强型交互式反馈工具
            
            Args:
                project_directory: 项目目录路径
                message: 反馈消息或问题
                feedback_type: 反馈类型 (question/confirmation/selection/code_review/suggestion/error_report)
                priority: 优先级 (low/medium/high/urgent)
                options: 预设选项列表 (用于选择题)
                language: 语言设置 (en/zh)
                timeout: 超时时间（秒）
                tags: 标签列表
                user_id: 用户ID
            
            Returns:
                包含用户反馈和分析信息的字典
            """
            try:
                # 验证参数
                feedback_type_enum = FeedbackType(feedback_type)
                priority_enum = Priority(priority)
                
                # 生成唯一ID
                feedback_id = str(uuid.uuid4())
                start_time = time.time()
                
                # 获取智能建议
                patterns = self.analytics.get_feedback_patterns(project_directory)
                
                # 格式化消息
                formatted_message = self._format_message(
                    message, feedback_type_enum, language, options, patterns.get("suggestions", [])
                )
                
                # 显示反馈界面
                response = self._show_feedback_dialog(
                    formatted_message, options, timeout, priority_enum, language
                )
                
                response_time = time.time() - start_time
                
                # 保存反馈记录
                feedback_record = FeedbackHistory(
                    id=feedback_id,
                    timestamp=datetime.now(),
                    project_path=project_directory,
                    feedback_type=feedback_type_enum,
                    question=message,
                    response=response,
                    response_time=response_time,
                    ai_summary="",  # 可以通过AI生成摘要
                    tags=tags or [],
                    priority=priority_enum,
                    user_id=user_id
                )
                
                self.analytics.save_feedback(feedback_record)
                
                # 生成实时建议
                next_suggestions = self._generate_next_suggestions(
                    project_directory, feedback_record
                )
                
                return {
                    "feedback_id": feedback_id,
                    "response": response,
                    "response_time": response_time,
                    "patterns": patterns,
                    "next_suggestions": next_suggestions,
                    "status": "success"
                }
                
            except Exception as e:
                logger.error(f"Error in interactive_feedback: {e}")
                return {
                    "error": str(e),
                    "status": "error"
                }
        
        @self.app.tool()
        def get_feedback_analytics(
            project_directory: str,
            days: int = 30,
            user_id: str = "default"
        ) -> Dict[str, Any]:
            """
            获取反馈分析报告
            
            Args:
                project_directory: 项目目录
                days: 分析天数
                user_id: 用户ID
            
            Returns:
                分析报告
            """
            try:
                patterns = self.analytics.get_feedback_patterns(project_directory, days)
                
                return {
                    "project": project_directory,
                    "analysis_period_days": days,
                    "patterns": patterns["patterns"],
                    "suggestions": patterns["suggestions"],
                    "generated_at": datetime.now().isoformat(),
                    "status": "success"
                }
            except Exception as e:
                logger.error(f"Error in get_feedback_analytics: {e}")
                return {"error": str(e), "status": "error"}
        
        @self.app.tool()
        def create_feedback_template(
            template_name: str,
            template_content: Dict[str, str],
            template_type: str = "custom"
        ) -> Dict[str, Any]:
            """
            创建自定义反馈模板
            
            Args:
                template_name: 模板名称
                template_content: 模板内容 (多语言支持)
                template_type: 模板类型
            
            Returns:
                创建结果
            """
            try:
                templates_file = self.template_manager.templates_dir / f"{template_name}.yaml"
                
                template_data = {
                    "type": template_type,
                    "created_at": datetime.now().isoformat(),
                    "content": template_content
                }
                
                with open(templates_file, 'w', encoding='utf-8') as f:
                    yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)
                
                return {
                    "template_name": template_name,
                    "file_path": str(templates_file),
                    "status": "created"
                }
            except Exception as e:
                logger.error(f"Error creating template: {e}")
                return {"error": str(e), "status": "error"}
        
        @self.app.tool()
        def execute_with_feedback(
            command: str,
            project_directory: str,
            require_confirmation: bool = True,
            language: str = "en"
        ) -> Dict[str, Any]:
            """
            执行命令并请求反馈
            
            Args:
                command: 要执行的命令
                project_directory: 项目目录
                require_confirmation: 是否需要确认
                language: 语言设置
            
            Returns:
                执行结果和反馈
            """
            try:
                if require_confirmation:
                    # 请求执行确认
                    confirmation_message = self.template_manager.get_template(
                        "confirmation", language, action=command
                    )
                    
                    confirmation_result = interactive_feedback(
                        project_directory=project_directory,
                        message=confirmation_message,
                        feedback_type="confirmation",
                        priority="medium",
                        options=["Yes", "No", "Modify"],
                        language=language
                    )
                    
                    if confirmation_result.get("response", "").lower() not in ["yes", "是"]:
                        return {
                            "status": "cancelled",
                            "message": "Command execution cancelled by user",
                            "feedback": confirmation_result
                        }
                
                # 执行命令
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=project_directory,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # 如果有错误，请求错误处理反馈
                if result.returncode != 0:
                    error_message = self.template_manager.get_template(
                        "error_handling", language, error=result.stderr
                    )
                    
                    error_feedback = interactive_feedback(
                        project_directory=project_directory,
                        message=error_message,
                        feedback_type="error_report",
                        priority="high",
                        language=language,
                        tags=["error", "command_execution"]
                    )
                    
                    return {
                        "status": "error",
                        "command": command,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "error_feedback": error_feedback
                    }
                
                return {
                    "status": "success",
                    "command": command,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
            except Exception as e:
                logger.error(f"Error in execute_with_feedback: {e}")
                return {"error": str(e), "status": "error"}
    
    def _format_message(
        self, 
        message: str, 
        feedback_type: FeedbackType, 
        language: str, 
        options: Optional[List[str]], 
        suggestions: List[str]
    ) -> str:
        """格式化反馈消息"""
        
        # 添加类型标识
        type_labels = {
            "en": {
                FeedbackType.QUESTION: "❓ Question",
                FeedbackType.CONFIRMATION: "✅ Confirmation", 
                FeedbackType.SELECTION: "📋 Selection",
                FeedbackType.CODE_REVIEW: "🔍 Code Review",
                FeedbackType.SUGGESTION: "💡 Suggestion",
                FeedbackType.ERROR_REPORT: "⚠️ Error Report"
            },
            "zh": {
                FeedbackType.QUESTION: "❓ 问题",
                FeedbackType.CONFIRMATION: "✅ 确认",
                FeedbackType.SELECTION: "📋 选择",
                FeedbackType.CODE_REVIEW: "🔍 代码审查", 
                FeedbackType.SUGGESTION: "💡 建议",
                FeedbackType.ERROR_REPORT: "⚠️ 错误报告"
            }
        }
        
        label = type_labels.get(language, type_labels["en"]).get(feedback_type, "")
        formatted = f"{label}\n\n{message}"
        
        # 添加选项
        if options:
            options_label = "Options:" if language == "en" else "选项："
            formatted += f"\n\n{options_label}\n"
            for i, option in enumerate(options, 1):
                formatted += f"{i}. {option}\n"
        
        # 添加智能建议
        if suggestions:
            suggestions_label = "💡 AI Suggestions:" if language == "en" else "💡 AI建议："
            formatted += f"\n\n{suggestions_label}\n"
            for suggestion in suggestions[:3]:  # 最多显示3个建议
                formatted += f"• {suggestion}\n"
        
        return formatted
    
    def _show_feedback_dialog(
        self, 
        message: str, 
        options: Optional[List[str]], 
        timeout: int, 
        priority: Priority,
        language: str
    ) -> str:
        """显示反馈对话框（简化版，实际应该使用GUI）"""
        
        print("\n" + "="*60)
        print(f"🤖 Enhanced Interactive Feedback MCP")
        print(f"⏰ Timeout: {timeout}s | 🔥 Priority: {priority.value.upper()}")
        print("="*60)
        print(message)
        print("="*60)
        
        try:
            if options:
                while True:
                    response = input(f"\n{'Please enter your choice (number or text):' if language == 'en' else '请输入您的选择（数字或文本）：'} ").strip()
                    
                    # 检查是否是数字选择
                    if response.isdigit():
                        idx = int(response) - 1
                        if 0 <= idx < len(options):
                            return options[idx]
                        else:
                            print(f"{'Invalid option number.' if language == 'en' else '无效的选项编号。'}")
                            continue
                    
                    # 检查是否是文本匹配
                    for option in options:
                        if response.lower() == option.lower():
                            return option
                    
                    # 如果都不匹配，返回原始输入
                    return response
            else:
                return input(f"\n{'Your response:' if language == 'en' else '您的回复：'} ").strip()
        
        except KeyboardInterrupt:
            return "cancelled" if language == "en" else "已取消"
        except Exception as e:
            logger.error(f"Error in dialog: {e}")
            return "error" if language == "en" else "错误"
    
    def _generate_next_suggestions(self, project_path: str, feedback: FeedbackHistory) -> List[str]:
        """基于当前反馈生成下一步建议"""
        suggestions = []
        
        # 基于反馈类型生成建议
        if feedback.feedback_type == FeedbackType.ERROR_REPORT:
            suggestions.append("考虑添加错误处理和日志记录")
            suggestions.append("运行相关测试确保修复有效")
        
        elif feedback.feedback_type == FeedbackType.CODE_REVIEW:
            suggestions.append("考虑重构以提高代码可读性")
            suggestions.append("添加单元测试覆盖新功能")
        
        elif feedback.feedback_type == FeedbackType.CONFIRMATION:
            if "yes" in feedback.response.lower():
                suggestions.append("执行后验证结果是否符合预期")
                suggestions.append("考虑自动化类似操作")
        
        # 基于响应时间生成建议
        if feedback.response_time > 30:
            suggestions.append("问题可能过于复杂，考虑分解为更小的步骤")
        
        return suggestions
    
    def run(self):
        """运行MCP服务器"""
        logger.info("Starting Enhanced Interactive Feedback MCP Server...")
        asyncio.run(self.app.run())

if __name__ == "__main__":
    server = EnhancedFeedbackMCP()
    server.run()
