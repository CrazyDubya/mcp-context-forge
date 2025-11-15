# Gateway Service

The `GatewayService` is responsible for the federation capabilities of the MCP Gateway. It allows a single gateway instance to connect to other peer MCP gateways, effectively creating a distributed network of tools and resources.

## Responsibilities

The `GatewayService` has the following key responsibilities:

-   **Gateway Registration**: Manages the registration of peer MCP gateways. When a new gateway is registered, the `GatewayService` connects to it, performs a health check, and fetches its capabilities, tools, resources, and prompts.
-   **Federated Resource Management**: The tools, resources, and prompts fetched from a peer gateway are registered locally, making them available to clients connected to the current gateway. The `GatewayService` works with the `ToolService`, `ResourceService`, and `PromptService` to manage these federated resources.
-   **Health Checks**: Periodically checks the health of all registered peer gateways. This is done by a single "leader" instance in a multi-worker environment to avoid redundant checks.
-   **Failure Handling**: If a peer gateway fails its health check multiple times, the `GatewayService` can mark it as inactive, effectively removing its resources from the local catalog until it becomes available again.
-   **Authentication**: Handles various authentication mechanisms for connecting to peer gateways, including Basic Auth, Bearer tokens, and OAuth.
-   **Capability Aggregation**: Aggregates the capabilities of all connected peer gateways, providing a unified view of the entire federated network's capabilities.
-   **Event Notifications**: Publishes events for gateway-related actions, such as `gateway_added`, `gateway_updated`, and `gateway_deleted`.

## Key Methods

Here are some of the most important methods in the `GatewayService`:

-   `register_gateway(db, gateway, ...)`: Registers a new peer gateway. This method initiates the connection, fetches the remote resources, and stores them locally.
-   `list_gateways(db, ...)`: Lists all registered peer gateways.
-   `get_gateway(db, gateway_id)`: Retrieves a single peer gateway by its ID.
-   `update_gateway(db, gateway_id, gateway_update)`: Updates the configuration of a peer gateway.
-   `delete_gateway(db, gateway_id)`: De-registers a peer gateway and removes its associated resources from the local catalog.
-   `toggle_gateway_status(db, gateway_id, activate)`: Manually activates or deactivates a peer gateway.
-   `_run_health_checks()`: The background task that periodically checks the health of all registered gateways.

## Interactions with Other Components

The `GatewayService` is a central hub for federation and interacts with several other components:

-   **Database (`mcpgateway/db.py`)**: The `GatewayService` uses SQLAlchemy to store information about peer gateways and their federated resources in the `Gateway`, `Tool`, `Resource`, and `Prompt` tables.
-   **ToolService, ResourceService, PromptService**: When a new peer gateway is registered, the `GatewayService` uses these services to register the federated resources locally.
-   **ResilientHttpClient (`mcpgateway/utils/retry_manager.py`)**: For connecting to peer gateways and performing health checks, the `GatewayService` uses a resilient HTTP client that provides automatic retries and timeouts.
-   **Redis/FileLock**: For leader election in a multi-worker environment, the `GatewayService` uses either Redis or a file-based lock to ensure that only one instance is performing health checks.
