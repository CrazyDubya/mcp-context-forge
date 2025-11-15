# Server Service

The `ServerService` manages the concept of "virtual servers" within the MCP Gateway. A virtual server is a logical grouping of tools, resources, and prompts, which can be exposed as a single, cohesive unit to a client. This allows for the creation of domain-specific or application-specific collections of capabilities.

## Responsibilities

The `ServerService` has the following key responsibilities:

-   **Virtual Server Management**: Handles the creation, retrieval, updating, and deletion of virtual servers.
-   **Resource Association**: Manages the associations between virtual servers and their constituent tools, resources, and prompts. It ensures that when a virtual server is created or updated, the specified resources exist and are correctly linked.
-   **A2A Agent Integration**: Allows for the association of A2A (Agent-to-Agent) agents with a virtual server, providing a way to group and expose AI agents as part of a cohesive service.
-   **Metrics and Monitoring**: Tracks metrics related to virtual servers, although the primary invocation metrics are handled by the `ToolService`.
-   **Event Notifications**: Publishes events for server-related actions, such as `server_added`, `server_updated`, and `server_deleted`.

## Key Methods

Here are some of the most important methods in the `ServerService`:

-   `register_server(db, server_in)`: Creates a new virtual server. It takes a `ServerCreate` schema, which includes lists of IDs for the tools, resources, and prompts to be associated with the server.
-   `list_servers(db, ...)`: Lists all registered virtual servers.
-   `get_server(db, server_id)`: Retrieves a single virtual server by its ID, along with the details of its associated resources.
-   `update_server(db, server_id, server_update)`: Updates an existing virtual server, allowing for changes to its name, description, and associated resources.
-   `delete_server(db, server_id)`: Deletes a virtual server.
-   `toggle_server_status(db, server_id, activate)`: Activates or deactivates a virtual server.

## Interactions with Other Components

The `ServerService` primarily interacts with the database to manage the relationships between servers and other resources:

-   **Database (`mcpgateway/db.py`)**: The `ServerService` uses SQLAlchemy to interact with the `Server` table and the association tables that link servers to tools, resources, and prompts.
-   **ToolService, ResourceService, PromptService**: While the `ServerService` does not directly call these services, it relies on the data they manage. When creating or updating a server, it verifies that the associated tools, resources, and prompts exist in the database.
-   **A2AService (`mcpgateway/services/a2a_service.py`)**: Similar to the other resource services, the `ServerService` relies on the data managed by the `A2AService` when associating agents with a server.
