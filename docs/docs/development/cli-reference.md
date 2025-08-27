# CLI Reference

The `mcpgateway` command-line interface (CLI) provides a set of tools for managing the MCP Gateway. This page provides a detailed reference for each command and subcommand.

## Global Options

-   `--version`, `-V`: Show the version of the `mcpgateway` CLI and exit.
-   `--help`: Show help text for a command.

## `run`

The `run` command starts the MCP Gateway server. It is a wrapper around the `uvicorn` server.

**Usage:**

```bash
mcpgateway run [OPTIONS]
```

**Options:**

-   `--host`, `-h`: The host to bind the server to. Defaults to `127.0.0.1`.
-   `--port`, `-p`: The port to bind the server to. Defaults to `4444`.
-   `--reload`: Enable auto-reload. When this is enabled, the server will automatically restart when it detects changes to the source code.
-   `--workers`, `-w`: The number of worker processes to run. Defaults to `1`.

**Example:**

```bash
# Run the server on the default host and port
mcpgateway run

# Run the server on all interfaces on port 8000 with auto-reload
mcpgateway run --host 0.0.0.0 --port 8000 --reload
```

## `plugin`

The `plugin` command provides a set of subcommands for managing plugins.

### `plugin create`

The `plugin create` command creates a new plugin from the Plugin Development Kit (PDK) template.

**Usage:**

```bash
mcpgateway plugin create <NAME>
```

**Arguments:**

-   `NAME`: The name of the new plugin.

**Example:**

```bash
mcpgateway plugin create "My New Plugin"
```

This will create a new plugin directory `my_new_plugin` inside the `plugins` directory.

### `plugin enable`

The `plugin enable` command enables a plugin by setting its `mode` to `enforce` in the `plugins/config.yaml` file.

**Usage:**

```bash
mcpgateway plugin enable <NAME>
```

**Arguments:**

-   `NAME`: The name of the plugin to enable.

### `plugin disable`

The `plugin disable` command disables a plugin by setting its `mode` to `disabled` in the `plugins/config.yaml` file.

**Usage:**

```bash
mcpgateway plugin disable <NAME>
```

**Arguments:**

-   `NAME`: The name of the plugin to disable.

## `config`

The `config` command provides a set of subcommands for managing the gateway's configuration.

### `config wizard`

The `config wizard` command runs an interactive wizard to create a `.env` file. This is the easiest way to get started with configuring the gateway.

**Usage:**

```bash
mcpgateway config wizard
```

The wizard will prompt you for the key configuration values and create a `.env` file in the current directory.

## `logs`

The `logs` command provides a set of subcommands for viewing the gateway's logs.

### `logs tail`

The `logs tail` command tails the gateway logs in real-time.

**Usage:**

```bash
mcpgateway logs tail [OPTIONS]
```

**Options:**

-   `--level`, `-l`: The minimum log level to show.
-   `--entity-type`: Filter by entity type.
-   `--entity-id`: Filter by entity ID.

**Example:**

```bash
# Tail all logs
mcpgateway logs tail

# Tail only error logs for a specific tool
mcpgateway logs tail --level error --entity-type tool --entity-id my-tool
```

## `export`

The `export` command exports the gateway's configuration to a JSON file.

**Usage:**

```bash
mcpgateway export [OPTIONS]
```

**Options:**

-   `--output`, `-o`: The output file path.
-   `--types`: Comma-separated list of entity types to include.
-   `--exclude-types`: Comma-separated list of entity types to exclude.
-   `--tags`: Comma-separated list of tags to filter by.
-   `--include-inactive`: Include inactive entities.
-   `--no-dependencies`: Don't include dependent entities.
-   `--verbose`, `-v`: Verbose output.

## `import`

The `import` command imports a gateway configuration from a JSON file.

**Usage:**

```bash
mcpgateway import <INPUT_FILE> [OPTIONS]
```

**Arguments:**

-   `INPUT_FILE`: The input file containing the export data.

**Options:**

-   `--conflict-strategy`: How to handle naming conflicts (`skip`, `update`, `rename`, `fail`).
-   `--dry-run`: Validate but don't make changes.
-   `--rekey-secret`: New encryption secret for cross-environment imports.
-   `--include`: Selective import (`entity_type:name1,name2;entity_type2:name3`).
-   `--verbose`, `-v`: Verbose output.
```
