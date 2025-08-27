# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/plugins/framework/helpers.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Your Name

This module provides helper functions to simplify plugin development.
"""

import logging
from typing import Any, Optional

from mcpgateway.plugins.framework.models import PluginContext


def get_plugin_logger(plugin_name: str) -> logging.Logger:
    """
    Get a logger for a plugin.

    This helper function returns a logger that is prefixed with the plugin's name,
    making it easy to identify log messages from a specific plugin.

    Args:
        plugin_name: The name of the plugin.

    Returns:
        A logger instance.
    """
    return logging.getLogger(f"mcp.plugin.{plugin_name}")


def get_config_value(context: PluginContext, key: str, default: Optional[Any] = None) -> Any:
    """
    Safely get a value from the plugin's configuration.

    Args:
        context: The PluginContext for the current hook invocation.
        key: The configuration key to retrieve.
        default: The default value to return if the key is not found.

    Returns:
        The configuration value or the default.
    """
    if context.plugin_config and context.plugin_config.config:
        return context.plugin_config.config.get(key, default)
    return default


def get_global_context_value(context: PluginContext, key: str, default: Optional[Any] = None) -> Any:
    """
    Safely get a value from the global context.

    Args:
        context: The PluginContext for the current hook invocation.
        key: The global context key to retrieve (e.g., "request_id", "user").
        default: The default value to return if the key is not found.

    Returns:
        The global context value or the default.
    """
    return getattr(context, key, default)
