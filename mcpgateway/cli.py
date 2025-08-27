# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/cli.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

mcpgateway CLI ─ a thin wrapper around Uvicorn
This module is exposed as a **console-script** via:

    [project.scripts]
    mcpgateway = "mcpgateway.cli:main"

so that a user can simply type `mcpgateway ...` instead of the longer
`uvicorn mcpgateway.main:app ...`.

Features
─────────
* Injects the default FastAPI application path (``mcpgateway.main:app``)
  when the user doesn't supply one explicitly.
* Adds sensible default host/port (127.0.0.1:4444) unless the user passes
  ``--host``/``--port`` or overrides them via the environment variables
  ``MCG_HOST`` and ``MCG_PORT``.
* Forwards *all* remaining arguments verbatim to Uvicorn's own CLI, so
  `--reload`, `--workers`, etc. work exactly the same.

Typical usage
─────────────
```console
$ mcpgateway --reload                 # dev server on 127.0.0.1:4444
$ mcpgateway --workers 4              # production-style multiprocess
$ mcpgateway 127.0.0.1:8000 --reload  # explicit host/port keeps defaults out
$ mcpgateway mypkg.other:app          # run a different ASGI callable
```
"""

# Future
from __future__ import annotations

# Standard
import os
import sys
from typing import List

# Third-Party
import uvicorn

# First-Party
from mcpgateway import __version__

# ---------------------------------------------------------------------------
# Configuration defaults (overridable via environment variables)
# ---------------------------------------------------------------------------
DEFAULT_APP = "mcpgateway.main:app"  # dotted path to FastAPI instance
DEFAULT_HOST = os.getenv("MCG_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("MCG_PORT", "4444"))

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _needs_app(arg_list: List[str]) -> bool:
    """Return *True* when the CLI invocation has *no* positional APP path.

    According to Uvicorn's argument grammar, the **first** non-flag token
    is taken as the application path. We therefore look at the first
    element of *arg_list* (if any) - if it *starts* with a dash it must be
    an option, hence the app path is missing and we should inject ours.

    Args:
        arg_list (List[str]): List of arguments

    Returns:
        bool: Returns *True* when the CLI invocation has *no* positional APP path

    Examples:
        >>> _needs_app([])
        True
        >>> _needs_app(["--reload"])
        True
        >>> _needs_app(["myapp.main:app"])
        False
    """

    return len(arg_list) == 0 or arg_list[0].startswith("-")


def _insert_defaults(raw_args: List[str]) -> List[str]:
    """Return a *new* argv with defaults sprinkled in where needed.

    Args:
        raw_args (List[str]): List of input arguments to cli

    Returns:
        List[str]: List of arguments

    Examples:
        >>> result = _insert_defaults([])
        >>> result[0]
        'mcpgateway.main:app'
        >>> result = _insert_defaults(["myapp.main:app", "--reload"])
        >>> result[0]
        'myapp.main:app'
    """

    args = list(raw_args)  # shallow copy - we'll mutate this

    # 1️⃣  Ensure an application path is present.
    if _needs_app(args):
        args.insert(0, DEFAULT_APP)

    # 2️⃣  Supply host/port if neither supplied nor UNIX domain socket.
    if "--uds" not in args:
        if "--host" not in args and "--http" not in args:
            args.extend(["--host", DEFAULT_HOST])
        if "--port" not in args:
            args.extend(["--port", str(DEFAULT_PORT)])

    return args


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------


# Third-Party
import typer
import uvicorn
from cookiecutter.main import cookiecutter

# Third-Party
import typer
import uvicorn
from cookiecutter.main import cookiecutter
import questionary

# ... (imports)

app = typer.Typer()
plugin_app = typer.Typer()
app.add_typer(plugin_app, name="plugin")
config_app = typer.Typer()
app.add_typer(config_app, name="config")
logs_app = typer.Typer()
app.add_typer(logs_app, name="logs")

@app.command()
def run(
    host: str = typer.Option(DEFAULT_HOST, "--host", "-h", help="Bind socket to this host."),
    port: int = typer.Option(DEFAULT_PORT, "--port", "-p", help="Bind socket to this port."),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload."),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of worker processes."),
):
    """Run the MCP Gateway server."""
    uvicorn.run(
        DEFAULT_APP,
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )

@app.command()
def export(
    output_file: str = typer.Option(None, "--output", "-o", help="Output file path"),
    types: str = typer.Option(None, "--types", help="Comma-separated entity types to include"),
    exclude_types: str = typer.Option(None, help="Comma-separated entity types to exclude"),
    tags: str = typer.Option(None, help="Comma-separated tags to filter by"),
    include_inactive: bool = typer.Option(False, "--include-inactive", help="Include inactive entities"),
    no_dependencies: bool = typer.Option(False, "--no-dependencies", help="Don't include dependent entities"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
):
    """Export gateway configuration."""
    from mcpgateway.services.cli_service import export_configuration, CLIError
    import asyncio
    try:
        include_dependencies = not no_dependencies
        asyncio.run(export_configuration(output_file, types, exclude_types, tags, include_inactive, include_dependencies, verbose))
    except CLIError as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)

@plugin_app.command()
def create(
    name: str = typer.Argument(..., help="The name of the new plugin."),
):
    """Create a new plugin from a template."""
    try:
        cookiecutter(
            "plugin_templates/native_pdk",
            no_input=True,
            extra_context={"plugin_name": name},
            output_dir="plugins",
        )
        print(f"Plugin '{name}' created successfully in 'plugins/{name.lower().replace(' ', '_').replace('-', '_')}'")
    except Exception as e:
        print(f"Error creating plugin: {e}")
        raise typer.Exit(code=1)


@plugin_app.command()
def enable(
    name: str = typer.Argument(..., help="The name of the plugin to enable."),
):
    """Enable a plugin."""
    try:
        import yaml
        from pathlib import Path

        config_path = Path("plugins/config.yaml")
        if not config_path.exists():
            print("Error: plugins/config.yaml not found.")
            raise typer.Exit(code=1)

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        found = False
        for plugin in config.get("plugins", []):
            if plugin.get("name") == name:
                plugin["mode"] = "enforce"
                found = True
                break

        if not found:
            print(f"Error: Plugin '{name}' not found in plugins/config.yaml.")
            raise typer.Exit(code=1)

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        print(f"Plugin '{name}' enabled.")
    except Exception as e:
        print(f"Error enabling plugin: {e}")
        raise typer.Exit(code=1)

@plugin_app.command()
def disable(
    name: str = typer.Argument(..., help="The name of the plugin to disable."),
):
    """Disable a plugin."""
    try:
        import yaml
        from pathlib import Path

        config_path = Path("plugins/config.yaml")
        if not config_path.exists():
            print("Error: plugins/config.yaml not found.")
            raise typer.Exit(code=1)

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        found = False
        for plugin in config.get("plugins", []):
            if plugin.get("name") == name:
                plugin["mode"] = "disabled"
                found = True
                break

        if not found:
            print(f"Error: Plugin '{name}' not found in plugins/config.yaml.")
            raise typer.Exit(code=1)

        with open(config_path, "w") as f:
            yaml.dump(config, f)

        print(f"Plugin '{name}' disabled.")
    except Exception as e:
        print(f"Error disabling plugin: {e}")
        raise typer.Exit(code=1)


@config_app.command()
def wizard():
    """Run an interactive wizard to create a .env file."""
    from pathlib import Path

    env_file = Path(".env")
    if env_file.exists():
        overwrite = questionary.confirm("A .env file already exists. Do you want to overwrite it?").ask()
        if not overwrite:
            print("Aborted.")
            raise typer.Exit()

    print("Welcome to the MCP Gateway configuration wizard!")
    print("I'll ask you a few questions to generate a .env file for you.")

    config = {}
    config["DATABASE_URL"] = questionary.text("Database URL:", default="sqlite:///./mcp.db").ask()
    config["JWT_SECRET_KEY"] = questionary.text("JWT Secret Key:", default="a-very-secret-key").ask()
    config["BASIC_AUTH_USER"] = questionary.text("Admin Username:", default="admin").ask()
    config["BASIC_AUTH_PASSWORD"] = questionary.password("Admin Password:").ask()
    config["MCPGATEWAY_UI_ENABLED"] = str(questionary.confirm("Enable Admin UI?", default=True).ask()).lower()
    config["MCPGATEWAY_ADMIN_API_ENABLED"] = str(questionary.confirm("Enable Admin API?", default=True).ask()).lower()
    config["PLUGINS_ENABLED"] = str(questionary.confirm("Enable Plugins?", default=True).ask()).lower()
    config["PLUGIN_HOT_RELOAD"] = str(questionary.confirm("Enable Plugin Hot-Reloading?", default=False).ask()).lower()

    with open(env_file, "w") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")

    print("\n✅ .env file created successfully!")
    print("You can now start the gateway with `mcpgateway run`.")


@logs_app.command()
def tail(
    level: str = typer.Option(None, "--level", "-l", help="Minimum log level to show."),
    entity_type: str = typer.Option(None, "--entity-type", help="Filter by entity type."),
    entity_id: str = typer.Option(None, "--entity-id", help="Filter by entity ID."),
):
    """Tail logs from the gateway in real-time."""
    import asyncio
    from mcpgateway.services.cli_service import get_auth_token, CLIError
    import aiohttp
    import json

    async def tail_logs():
        token = await get_auth_token()
        if not token:
            print("Error: Authentication token not found.")
            return

        headers = {"Authorization": token}
        params = {}
        if level:
            params["level"] = level
        if entity_type:
            params["entity_type"] = entity_type
        if entity_id:
            params["entity_id"] = entity_id

        url = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/admin/logs/stream"

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        print(f"Error connecting to log stream: {response.status}")
                        return

                    async for line in response.content:
                        if line.startswith(b"data:"):
                            try:
                                data = json.loads(line[5:])
                                print(json.dumps(data, indent=2))
                            except json.JSONDecodeError:
                                pass
        except aiohttp.ClientConnectorError as e:
            print(f"Connection error: {e}")
        except KeyboardInterrupt:
            print("\nStopped tailing logs.")

    try:
        asyncio.run(tail_logs())
    except CLIError as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command(name="import")
def import_command(
    input_file: str = typer.Argument(..., help="Input file containing export data"),
    conflict_strategy: str = typer.Option("update", help="How to handle naming conflicts (skip, update, rename, fail)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate but don't make changes"),
    rekey_secret: str = typer.Option(None, help="New encryption secret for cross-environment imports"),
    include: str = typer.Option(None, help="Selective import: entity_type:name1,name2;entity_type2:name3"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose output"),
):
    """Import gateway configuration."""
    from mcpgateway.services.cli_service import import_configuration
    import asyncio
    try:
        asyncio.run(import_configuration(input_file, conflict_strategy, dry_run, rekey_secret, include, verbose))
    except CLIError as e:
        print(f"Error: {e}")
        raise typer.Exit(code=1)

def version_callback(value: bool):
    if value:
        print(f"mcpgateway {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-V", callback=version_callback, is_eager=True),
):
    """MCP Gateway CLI"""


if __name__ == "__main__":  # pragma: no cover - executed only when run directly
    main()
