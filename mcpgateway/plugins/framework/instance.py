# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/plugins/framework/instance.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Your Name

This module provides a singleton instance of the PluginManager.
"""

# First-Party
from mcpgateway.config import settings
from mcpgateway.plugins.framework.manager import PluginManager

plugin_manager: PluginManager | None = PluginManager(settings.plugin_config_file) if settings.plugins_enabled else None
