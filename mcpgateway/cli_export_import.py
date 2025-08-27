# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/cli_export_import.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Export/Import CLI Commands.
This module provides CLI commands for exporting and importing MCP Gateway configuration.
It implements the export/import CLI functionality according to the specification including:
- Complete configuration export with filtering options
- Configuration import with conflict resolution strategies
- Dry-run validation for imports
- Cross-environment key rotation support
- Progress reporting and status tracking
"""

# Standard
import argparse
import asyncio
import base64
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional

# Third-Party
import aiohttp

# First-Party
from mcpgateway import __version__
from mcpgateway.config import settings

logger = logging.getLogger(__name__)


class CLIError(Exception):
    """Base class for CLI-related errors."""


class AuthenticationError(CLIError):
    """Raised when authentication fails."""


async def get_auth_token() -> Optional[str]:
    """Get authentication token from environment or config.

    Returns:
        Authentication token string or None if not configured
    """
    # Try environment variable first
    token = os.getenv("MCPGATEWAY_BEARER_TOKEN")
    if token:
        return token

    # Fallback to basic auth if configured
    if settings.basic_auth_user and settings.basic_auth_password:
        creds = base64.b64encode(f"{settings.basic_auth_user}:{settings.basic_auth_password}".encode()).decode()
        return f"Basic {creds}"

    return None


async def make_authenticated_request(method: str, url: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make an authenticated HTTP request to the gateway API.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL path for the request
        json_data: Optional JSON data for request body
        params: Optional query parameters

    Returns:
        JSON response from the API

    Raises:
        AuthenticationError: If no authentication is configured
        CLIError: If the API request fails
    """
    token = await get_auth_token()
    if not token:
        raise AuthenticationError("No authentication configured. Set MCPGATEWAY_BEARER_TOKEN environment variable or configure BASIC_AUTH_USER/BASIC_AUTH_PASSWORD.")

    headers = {"Content-Type": "application/json"}
    if token.startswith("Basic "):
        headers["Authorization"] = token
    else:
        headers["Authorization"] = f"Bearer {token}"

    gateway_url = f"http://{settings.host}:{settings.port}"
    full_url = f"{gateway_url}{url}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method=method, url=full_url, json=json_data, params=params, headers=headers) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise CLIError(f"API request failed ({response.status}): {error_text}")

                return await response.json()

        except aiohttp.ClientError as e:
            raise CLIError(f"Failed to connect to gateway at {gateway_url}: {str(e)}")


# First-Party
from mcpgateway.services.cli_service import export_configuration, import_configuration, CLIError
# ... (rest of the imports)

async def export_command_wrapper(args: argparse.Namespace) -> None:
    """Wrapper for the export command to be called from argparse."""
    try:
        await export_configuration(
            output_file=args.output,
            types=args.types,
            exclude_types=args.exclude_types,
            tags=args.tags,
            include_inactive=args.include_inactive,
            include_dependencies=args.include_dependencies,
            verbose=args.verbose,
        )
    except CLIError as e:
        print(f"❌ Export failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

async def import_command_wrapper(args: argparse.Namespace) -> None:
    """Wrapper for the import command to be called from argparse."""
    try:
        await import_configuration(
            input_file=args.input_file,
            conflict_strategy=args.conflict_strategy,
            dry_run=args.dry_run,
            rekey_secret=args.rekey_secret,
            include=args.include,
            verbose=args.verbose,
        )
    except CLIError as e:
        print(f"❌ Import failed: {str(e)}", file=sys.stderr)
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for export/import commands.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(prog="mcpgateway", description="MCP Gateway configuration export/import tool")

    parser.add_argument("--version", "-V", action="version", version=f"mcpgateway {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export gateway configuration")
    export_parser.add_argument("--output", "--out", "-o", help="Output file path (default: mcpgateway-export-YYYYMMDD-HHMMSS.json)")
    export_parser.add_argument("--types", "--type", help="Comma-separated entity types to include (tools,gateways,servers,prompts,resources,roots)")
    export_parser.add_argument("--exclude-types", help="Comma-separated entity types to exclude")
    export_parser.add_argument("--tags", help="Comma-separated tags to filter by")
    export_parser.add_argument("--include-inactive", action="store_true", help="Include inactive entities in export")
    export_parser.add_argument("--no-dependencies", action="store_true", help="Don't include dependent entities")
    export_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    export_parser.set_defaults(func=export_command_wrapper, include_dependencies=True)

    # Import command
    import_parser = subparsers.add_parser("import", help="Import gateway configuration")
    import_parser.add_argument("input_file", help="Input file containing export data")
    import_parser.add_argument("--conflict-strategy", choices=["skip", "update", "rename", "fail"], default="update", help="How to handle naming conflicts (default: update)")
    import_parser.add_argument("--dry-run", action="store_true", help="Validate but don't make changes")
    import_parser.add_argument("--rekey-secret", help="New encryption secret for cross-environment imports")
    import_parser.add_argument("--include", help="Selective import: entity_type:name1,name2;entity_type2:name3")
    import_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    import_parser.set_defaults(func=import_command_wrapper)

    return parser


def main_with_subcommands() -> None:
    """Main CLI entry point with export/import subcommands support."""
    parser = create_parser()

    # Check if we have export/import commands
    if len(sys.argv) > 1 and sys.argv[1] in ["export", "import"]:
        args = parser.parse_args()

        if hasattr(args, "func"):
            # Handle no-dependencies flag
            if hasattr(args, "include_dependencies"):
                args.include_dependencies = not getattr(args, "no_dependencies", False)

            # Run the async command
            try:
                asyncio.run(args.func(args))
            except KeyboardInterrupt:
                print("\n❌ Operation cancelled by user", file=sys.stderr)
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
    else:
        # Fall back to the original uvicorn-based CLI
        # First-Party
        from mcpgateway.cli import main  # pylint: disable=import-outside-toplevel,cyclic-import

        main()


if __name__ == "__main__":
    main_with_subcommands()
