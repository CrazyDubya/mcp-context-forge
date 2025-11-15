# Plugin Hot-Reloading

The MCP Gateway includes a hot-reloading feature for plugins, which allows you to modify your plugin configuration and have the changes automatically applied without restarting the gateway. This is particularly useful during development, as it can significantly speed up the development and testing cycle.

## Enabling Hot-Reloading

Hot-reloading is disabled by default. To enable it, you need to set the `PLUGIN_HOT_RELOAD` option to `true` in your `.env` file:

```dotenv
# .env

# ... other settings

PLUGINS_ENABLED=true
PLUGIN_HOT_RELOAD=true
```

Alternatively, you can set the `MCPGATEWAY_PLUGIN_HOT_RELOAD` environment variable to `true`.

## How It Works

When hot-reloading is enabled, the `PluginManager` starts a file watcher that monitors the `plugins/config.yaml` file for changes. When a change is detected, the following sequence of events occurs:

1.  **Change Detected**: The file watcher detects a modification to `plugins/config.yaml`.
2.  **Shutdown Existing Plugins**: The `PluginManager` calls the `shutdown` method on all currently loaded plugins to allow them to clean up any resources they may be using.
3.  **Clear Plugin Registry**: The internal registry of plugins and hooks is cleared.
4.  **Re-initialize Plugins**: The `PluginManager` re-reads the `plugins/config.yaml` file and initializes the new set of plugins. This includes loading any new plugins, unloading any removed plugins, and reloading any modified plugins.

This entire process happens automatically in the background, allowing you to seamlessly continue your development workflow.

### Manual Reloading

In addition to automatic reloading, you can also manually trigger a reload of the plugins by sending a `POST` request to the `/admin/plugins/reload` endpoint:

```bash
curl -X POST http://localhost:4444/admin/plugins/reload \
-H "Authorization: Bearer YOUR_TOKEN"
```

This can be useful if you want to force a reload without modifying the configuration file.

## Limitations and Caveats

-   **Configuration Only**: Hot-reloading only applies to changes in the `plugins/config.yaml` file. If you make changes to the Python code of a plugin, you will still need to restart the gateway for those changes to take effect.
-   **Development Only**: This feature is intended for development environments only. It is not recommended to use hot-reloading in a production environment, as it can introduce instability.
-   **File-Based**: The current implementation watches a single configuration file (`plugins/config.yaml`). It does not watch for changes in individual plugin directories or other configuration files.
