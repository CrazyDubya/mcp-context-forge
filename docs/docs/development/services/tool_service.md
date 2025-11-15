# Tool Service

The `ToolService` is a core component of the MCP Gateway, responsible for managing the entire lifecycle of tools. It handles everything from registration and invocation to metrics and event notifications. This service ensures that tools, whether they are native MCP tools or adapted from REST APIs, are handled in a consistent and reliable manner.

## Responsibilities

The `ToolService` has the following key responsibilities:

-   **Tool Registration**: Manages the registration of new tools, including validating their configuration and storing them in the database.
-   **Tool Invocation**: Handles the invocation of tools, including input schema validation, authentication, and forwarding requests to the appropriate backend (either a REST service or an MCP server).
-   **Plugin Integration**: Integrates with the plugin framework to allow for pre- and post-invocation hooks. This enables features like request modification, response filtering, and custom validation.
-   **A2A (Agent-to-Agent) Integration**: Works in conjunction with the `A2AService` to expose AI agents as tools within the gateway.
-   **Metrics and Monitoring**: Records detailed metrics for each tool invocation, including response time, success/failure status, and error messages.
-   **Event Notifications**: Publishes events for tool-related actions, such as `tool_added`, `tool_updated`, and `tool_deleted`. This allows other parts of the system to react to changes in the tool catalog.
-   **Federation Support**: Manages tools that are federated from other MCP gateways, ensuring they are correctly registered and invoked.

## Key Methods

Here are some of the most important methods in the `ToolService`:

-   `register_tool(db, tool, ...)`: Registers a new tool. It takes a `ToolCreate` schema, validates it, and creates a new `DbTool` record in the database.
-   `invoke_tool(db, name, arguments, ...)`: Invokes a tool by name. This is the main entry point for using a tool. It handles argument validation, authentication, plugin execution, and forwarding the request to the tool's endpoint.
-   `list_tools(db, ...)`: Lists all registered tools, with options to include inactive tools and filter by tags.
-   `get_tool(db, tool_id)`: Retrieves a single tool by its ID.
-   `update_tool(db, tool_id, tool_update, ...)`: Updates an existing tool.
-   `delete_tool(db, tool_id)`: Deletes a tool from the registry.
-   `toggle_tool_status(db, tool_id, activate)`: Activates or deactivates a tool.

## Interactions with Other Components

The `ToolService` is highly interconnected with other parts of the gateway:

-   **Database (`mcpgateway/db.py`)**: The `ToolService` uses SQLAlchemy to interact with the database, primarily the `Tool` and `ToolMetric` tables.
-   **Plugin Manager (`mcpgateway/plugins/framework/manager.py`)**: Before and after invoking a tool, the `ToolService` calls the `PluginManager` to execute any registered plugins.
-   **Gateway Service (`mcpgateway/services/gateway_service.py`)**: When a tool is federated from another gateway, the `GatewayService` calls the `ToolService` to register it locally.
-   **A2A Service (`mcpgateway/services/a2a_service.py`)**: For tools that are backed by A2A agents, the `ToolService` delegates the invocation to the `A2AService`.
-   **ResilientHttpClient (`mcpgateway/utils/retry_manager.py`)**: For invoking REST-based tools, the `ToolService` uses a resilient HTTP client that provides automatic retries and timeouts.
