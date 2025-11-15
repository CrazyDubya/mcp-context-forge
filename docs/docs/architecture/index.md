# Architecture Overview

The **MCP Gateway** acts as a unified entry point for tools, resources, prompts, and servers, federating local and remote nodes into a coherent MCP-compliant interface.

This gateway:

- Wraps REST/MCP tools and resources under JSON-RPC and streaming protocols
- Offers a pluggable backend (cache, auth, storage)
- Exposes multiple transports (HTTP, WS, SSE, StreamableHttp, stdio)
- Automatically discovers and merges federated peers

## System Architecture

```mermaid
graph TD
    subgraph "Client Tier"
        direction LR
        admin_ui["Admin UI (Browser)"]
        cli["MCP CLI / SDK"]
        agent["AI Agent / Tool User"]
    end

    subgraph "Gateway Tier (FastAPI)"
        direction TB
        router["Transport Router<br>(HTTP, WS, SSE, Stdio)"]
        auth["Auth Middleware<br>(JWT, Basic, OAuth)"]
        plugin_manager["Plugin Manager"]

        subgraph "Core Services"
            direction TB
            server_service["ServerService"]
            tool_service["ToolService"]
            gateway_service["GatewayService"]
            resource_service["ResourceService"]
            prompt_service["PromptService"]
        end

        db["Database<br>(SQLAlchemy)"]
        cache["Cache<br>(Redis/Memory)"]
    end

    subgraph "Backend Tier"
        direction TB
        rest_api["External REST API"]
        mcp_server["Peer MCP Server"]
        a2a_agent["A2A Agent"]
    end

    %% Client to Gateway
    admin_ui --> auth
    cli --> auth
    agent --> auth
    auth --> router

    %% Gateway Internals
    router --> plugin_manager
    plugin_manager --> server_service
    plugin_manager --> tool_service
    plugin_manager --> resource_service
    plugin_manager --> prompt_service

    server_service --> db
    tool_service --> db
    gateway_service --> db
    resource_service --> db
    prompt_service --> db

    server_service --> cache
    tool_service --> cache
    resource_service --> cache

    %% Service Interactions
    server_service -- manages associations --> tool_service
    server_service -- manages associations --> resource_service
    server_service -- manages associations --> prompt_service
    server_service -- manages associations --> gateway_service

    %% Gateway to Backend
    tool_service -- invokes --> rest_api
    tool_service -- invokes --> a2a_agent
    gateway_service -- federates with --> mcp_server

```

> Each service (ToolService, ResourceService, etc.) operates independently with unified auth/session/context layers.

## Additional Architecture Documentation

- [Export/Import System Architecture](export-import-architecture.md) - Technical design of configuration management system

## ADRs and Design Decisions

We maintain a formal set of [Architecture Decision Records](adr/index.md) documenting all major design tradeoffs and rationale.

📜 See the [full ADR Index →](adr/index.md)
