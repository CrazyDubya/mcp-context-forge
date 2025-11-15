# -*- coding: utf-8 -*-
"""Location: ./mcpgateway/services/cli_service.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Your Name

CLI Service.
This module provides the business logic for the CLI commands.
"""

# Standard
import base64
from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, List

# Third-Party
import aiohttp

# First-Party
from mcpgateway.config import settings

logger = logging.getLogger(__name__)


class CLIError(Exception):
    """Base class for CLI-related errors."""


class AuthenticationError(CLIError):
    """Raised when authentication fails."""


async def get_auth_token() -> Optional[str]:
    """Get authentication token from environment or config."""
    token = os.getenv("MCPGATEWAY_BEARER_TOKEN")
    if token:
        return token

    if settings.basic_auth_user and settings.basic_auth_password:
        creds = base64.b64encode(f"{settings.basic_auth_user}:{settings.basic_auth_password}".encode()).decode()
        return f"Basic {creds}"

    return None


async def make_authenticated_request(method: str, url: str, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Make an authenticated HTTP request to the gateway API."""
    token = await get_auth_token()
    if not token:
        raise AuthenticationError("No authentication configured. Set MCPGATEWAY_BEARER_TOKEN or BASIC_AUTH_USER/PASSWORD.")

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


async def export_configuration(
    output_file: Optional[str] = None,
    types: Optional[str] = None,
    exclude_types: Optional[str] = None,
    tags: Optional[str] = None,
    include_inactive: bool = False,
    include_dependencies: bool = True,
    verbose: bool = False,
) -> None:
    """Export gateway configuration."""
    print(f"Exporting configuration from gateway at http://{settings.host}:{settings.port}")

    params = {}
    if types:
        params["types"] = types
    if exclude_types:
        params["exclude_types"] = exclude_types
    if tags:
        params["tags"] = tags
    if include_inactive:
        params["include_inactive"] = "true"
    if not include_dependencies:
        params["include_dependencies"] = "false"

    export_data = await make_authenticated_request("GET", "/export", params=params)

    if output_file:
        output_path = Path(output_file)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = Path(f"mcpgateway-export-{timestamp}.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    metadata = export_data.get("metadata", {})
    entity_counts = metadata.get("entity_counts", {})
    total_entities = sum(entity_counts.values())

    print("✅ Export completed successfully!")
    print(f"📁 Output file: {output_path}")
    print(f"📊 Exported {total_entities} total entities:")
    for entity_type, count in entity_counts.items():
        if count > 0:
            print(f"   • {entity_type}: {count}")

    if verbose:
        print("\n🔍 Export details:")
        print(f"   • Version: {export_data.get('version')}")
        print(f"   • Exported at: {export_data.get('exported_at')}")
        print(f"   • Exported by: {export_data.get('exported_by')}")
        print(f"   • Source: {export_data.get('source_gateway')}")


async def import_configuration(
    input_file: str,
    conflict_strategy: str = "update",
    dry_run: bool = False,
    rekey_secret: Optional[str] = None,
    include: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Import gateway configuration."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise CLIError(f"Input file not found: {input_path}")

    print(f"Importing configuration from {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        import_data = json.load(f)

    request_data = {
        "import_data": import_data,
        "conflict_strategy": conflict_strategy,
        "dry_run": dry_run,
    }

    if rekey_secret:
        request_data["rekey_secret"] = rekey_secret

    if include:
        selected_entities = {}
        for selection in include.split(";"):
            if ":" in selection:
                entity_type, entity_list = selection.split(":", 1)
                entities = [e.strip() for e in entity_list.split(",") if e.strip()]
                selected_entities[entity_type] = entities
        request_data["selected_entities"] = selected_entities

    result = await make_authenticated_request("POST", "/import", json_data=request_data)

    status = result.get("status", "unknown")
    progress = result.get("progress", {})

    if dry_run:
        print("🔍 Dry-run validation completed!")
    else:
        print(f"✅ Import {status}!")

    print("📊 Results:")
    print(f"   • Total entities: {progress.get('total', 0)}")
    print(f"   • Processed: {progress.get('processed', 0)}")
    print(f"   • Created: {progress.get('created', 0)}")
    print(f"   • Updated: {progress.get('updated', 0)}")
    print(f"   • Skipped: {progress.get('skipped', 0)}")
    print(f"   • Failed: {progress.get('failed', 0)}")

    warnings = result.get("warnings", [])
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings[:5]:
            print(f"   • {warning}")
        if len(warnings) > 5:
            print(f"   • ... and {len(warnings) - 5} more warnings")

    errors = result.get("errors", [])
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors[:5]:
            print(f"   • {error}")
        if len(errors) > 5:
            print(f"   • ... and {len(errors) - 5} more errors")

    if verbose:
        print("\n🔍 Import details:")
        print(f"   • Import ID: {result.get('import_id')}")
        print(f"   • Started at: {result.get('started_at')}")
        print(f"   • Completed at: {result.get('completed_at')}")

    if progress.get("failed", 0) > 0:
        raise CLIError("Import finished with errors.")
