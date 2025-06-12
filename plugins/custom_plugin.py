#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Custom Plugin for Enhanced Interactive Feedback MCP Server
"""

import logging
from typing import Dict, Any, Optional

class CustomPlugin:
    """
    Custom plugin template for Enhanced Interactive Feedback MCP Server
    
    This class implements hooks that will be called by the server
    during various feedback events.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the plugin with optional configuration
        
        Args:
            config: Plugin configuration from the enhanced_feedback_config.yaml
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.logger.info("CustomPlugin initialized")
    
    def on_feedback_received(self, feedback: Dict[str, Any]) -> None:
        """
        Called when new feedback is received from the user
        
        Args:
            feedback: The feedback data including type, message, etc.
        """
        self.logger.info(f"Feedback received: {feedback.get('message', '')}")
        # Add your custom handling logic here
        
    def on_feedback_responded(self, feedback: Dict[str, Any], response: Optional[str]) -> None:
        """
        Called when the user responds to a feedback request
        
        Args:
            feedback: The original feedback data
            response: The user's response
        """
        self.logger.info(f"Feedback response received: {response}")
        # Add your custom handling logic here
        
    def on_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Called when an error occurs during feedback processing
        
        Args:
            error: The exception that was raised
            context: Additional context about when the error occurred
        """
        self.logger.error(f"Error in feedback: {error}", exc_info=True)
        # Add your custom error handling logic here
        
    def get_analytics_data(self) -> Dict[str, Any]:
        """
        Provides custom analytics data for the dashboard
        
        Returns:
            Dict containing custom analytics data
        """
        return {
            "custom_metric": 42,
            "plugin_status": "operational"
        }


# Plugin entry point - must be named 'plugin_instance'
plugin_instance = CustomPlugin() 