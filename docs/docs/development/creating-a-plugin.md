# Creating a Plugin

This tutorial will guide you through the process of creating a new "native" plugin for the MCP Gateway using the Plugin Development Kit (PDK).

## Prerequisites

- Python 3.10+
- The MCP Gateway project cloned to your local machine.
- `cookiecutter` installed. If you don't have it, you can install it with pip:
  ```bash
  pip install cookiecutter
  ```

## Step 1: Generate a New Plugin

The PDK includes a `cookiecutter` template for creating native plugins. To use it, navigate to the root of the MCP Gateway project and run the following command:

```bash
cookiecutter plugin_templates/native_pdk
```

You will be prompted for the following information:

- `plugin_name`: The display name of your plugin. Let's call it "Hello World Plugin".
- `description`: A short description of what your plugin does.
- `author`: Your name.
- `version`: The initial version of your plugin (0.1.0 is a good start).

`cookiecutter` will then generate a new directory for your plugin inside the `plugins` directory. The directory will be named based on the "slugified" version of your plugin name (e.g., `hello_world_plugin`).

## Step 2: Explore the Plugin Structure

Your newly generated plugin directory will have the following structure:

```
plugins/
└── hello_world_plugin/
    ├── __init__.py
    ├── config.yaml
    ├── plugin-manifest.yaml
    └── plugin.py
```

- `__init__.py`: An empty file that makes the directory a Python package.
- `config.yaml`: The configuration file that registers your plugin with the gateway.
- `plugin-manifest.yaml`: A file containing metadata about your plugin.
- `plugin.py`: The main file where you will write your plugin's logic.

## Step 3: Add Your Plugin's Logic

Open the `plugins/hello_world_plugin/plugin.py` file. You will see a class named `HelloWorldPlugin` (the name is generated from your `plugin_name`). This class has several methods that correspond to the available hooks in the plugin framework.

Let's add a simple log message to the `tool_pre_invoke` hook. This hook is called right before a tool is invoked.

```python
# In plugins/hello_world_plugin/plugin.py

# ... (imports)

import logging

logger = logging.getLogger(__name__)

class HelloWorldPlugin(Plugin):
    # ... (__init__ method)

    # ... (other hooks)

    async def tool_pre_invoke(self, payload: ToolPreInvokePayload, context: PluginContext) -> ToolPreInvokeResult:
        """Plugin hook run before a tool is invoked."""
        logger.info(f"Hello from the HelloWorldPlugin! The tool '{payload.name}' is about to be invoked.")
        return ToolPreInvokeResult(continue_processing=True)

    # ... (other hooks)
```

## Step 4: Install the Plugin

To install the plugin, you need to tell the gateway to load it. This is done by adding the plugin's configuration to the main `plugins/config.yaml` file.

Open the `plugins/config.yaml` file. You will see a `plugins` section. You need to merge the content of your plugin's `config.yaml` file into this main configuration file.

For our "Hello World" plugin, you would add the following to `plugins/config.yaml`:

```yaml
# In plugins/config.yaml

plugins:
  # ... (other plugins)
  - name: "Hello World Plugin"
    kind: "hello_world_plugin.plugin.HelloWorldPlugin"
    description: "A simple hello world plugin."
    version: "0.1.0"
    author: "Your Name"
    hooks: ["tool_pre_invoke"]
    tags: ["example", "tutorial"]
    mode: "permissive"
    priority: 200
```

You also need to tell the gateway to scan your new plugin's directory:

```yaml
# In plugins/config.yaml

plugin_dirs:
  # ... (other plugin directories)
  - "hello_world_plugin"
```

## Step 5: Test Your Plugin

Now, restart the MCP Gateway. When you invoke any tool, you should see your "Hello World" message in the gateway's logs.

Congratulations! You have successfully created and installed a new native plugin for the MCP Gateway.

## Advanced Topics

### Using the PluginContext

The `PluginContext` object is passed to each hook method and allows you to share state between hooks for a single request. For example, you could store a value in the `tool_pre_invoke` hook and then access it in the `tool_post_invoke` hook.

```python
# In plugins/hello_world_plugin/plugin.py

class HelloWorldPlugin(Plugin):
    # ...

    async def tool_pre_invoke(self, payload: ToolPreInvokePayload, context: PluginContext) -> ToolPreInvokeResult:
        context.set_state("my_custom_value", "Hello from pre_invoke!")
        return ToolPreInvokeResult(continue_processing=True)

    async def tool_post_invoke(self, payload: ToolPostInvokePayload, context: PluginContext) -> ToolPostInvokeResult:
        my_value = context.get_state("my_custom_value")
        self.logger.info(f"Retrieved from state: {my_value}")
        return ToolPostInvokeResult(continue_processing=True)
```

### Handling Errors and Violations

Your plugin can block a request by returning a `PluginResult` with `continue_processing=False`. You can also include a `PluginViolation` object to provide more information about why the request was blocked.

```python
# In plugins/hello_world_plugin/plugin.py

from mcpgateway.plugins.framework import PluginViolation

class HelloWorldPlugin(Plugin):
    # ...

    async def tool_pre_invoke(self, payload: ToolPreInvokePayload, context: PluginContext) -> ToolPreInvokeResult:
        if payload.name == "a_blocked_tool":
            violation = PluginViolation(
                reason="This tool is blocked by the HelloWorldPlugin.",
                description="This is a test violation.",
                code="TOOL_BLOCKED",
                details={"tool_name": payload.name}
            )
            return ToolPreInvokeResult(continue_processing=False, violation=violation)
        return ToolPreInvokeResult(continue_processing=True)
```

### Writing Tests for Your Plugin

It's highly recommended to write unit tests for your plugins. You can create a new test file in the `tests/unit/mcpgateway/plugins/plugins` directory.

Here's an example of a simple test for our "Hello World" plugin:

```python
# In tests/unit/mcpgateway/plugins/plugins/test_hello_world_plugin.py

import pytest
from unittest.mock import MagicMock
from mcpgateway.plugins.hello_world_plugin.plugin import HelloWorldPlugin
from mcpgateway.plugins.framework import ToolPreInvokePayload, PluginContext

@pytest.mark.asyncio
async def test_hello_world_plugin():
    # Arrange
    config = MagicMock()
    plugin = HelloWorldPlugin(config)
    payload = ToolPreInvokePayload(name="test_tool", args={})
    context = PluginContext(request_id="test_request")

    # Act
    result = await plugin.tool_pre_invoke(payload, context)

    # Assert
    assert result.continue_processing is True
```
