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
    Get a namespaced logger for a plugin.

    This helper function returns a logger that is automatically namespaced under
    `mcp.plugin.<plugin_name>`. This makes it easy to identify and filter
    log messages from a specific plugin in the gateway's logs.

    Args:
        plugin_name: The name of the plugin (usually the slug).

    Returns:
        A standard Python logger instance.

    Usage:
        ```python
        from mcpgateway.plugins.framework.helpers import get_plugin_logger

        class MyPlugin(Plugin):
            def __init__(self, config: PluginConfig):
                super().__init__(config)
                self.logger = get_plugin_logger("my_plugin")
                self.logger.info("MyPlugin has been initialized.")
        ```
    """
    return logging.getLogger(f"mcp.plugin.{plugin_name}")


def get_config_value(context: PluginContext, key: str, default: Optional[Any] = None) -> Any:
    """
    Safely retrieve a value from the plugin's specific configuration.

    This function provides a safe way to access values from the `config`
    dictionary defined in the `plugins/config.yaml` file for the current plugin.
    It handles cases where the `config` dictionary might not exist or the key
    is not present, returning a default value instead.

    Args:
        context: The `PluginContext` object passed to the hook method.
        key: The configuration key to retrieve.
        default: The default value to return if the key is not found.

    Returns:
        The configuration value, or the default value if not found.

    Usage:
        ```python
        # In your plugin's hook method:
        api_key = get_config_value(context, "api_key", "default_key")
        if api_key == "default_key":
            self.logger.warning("api_key not found in plugin config.")
        ```
    """
    if context.plugin_config and context.plugin_config.config:
        return context.plugin_config.config.get(key, default)
    return default


def get_global_context_value(context: PluginContext, key: str, default: Optional[Any] = None) -> Any:
    """
    Safely retrieve a value from the global request context.

    The global context contains information about the overall request, such as
    the `request_id`, the `user` who made the request, and the `server_id` it's
    associated with. This helper provides a safe way to access these attributes.

    Args:
        context: The `PluginContext` object passed to the hook method.
        key: The global context attribute to retrieve (e.g., "request_id", "user").
        default: The default value to return if the attribute is not found.

    Returns:
        The value of the global context attribute, or the default value.

    Usage:
        ```python
        # In your plugin's hook method:
        request_id = get_global_context_value(context, "request_id", "unknown_request")
        self.logger.info(f"Processing request: {request_id}")
        ```
    """
    return getattr(context, key, default)
