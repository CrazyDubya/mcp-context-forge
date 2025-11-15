# -*- coding: utf-8 -*-
"""Location: ./tests/unit/mcpgateway/test_cli_export_import_coverage.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Tests for CLI export/import to improve coverage.
"""

# Standard
import argparse
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import json

# Third-Party
import pytest

# First-Party
from mcpgateway.services.cli_service import (
    get_auth_token, AuthenticationError, CLIError, export_configuration, import_configuration
)


@pytest.mark.asyncio
async def test_get_auth_token_from_env():
    """Test getting auth token from environment."""
    with patch.dict('os.environ', {'MCPGATEWAY_BEARER_TOKEN': 'test-token'}):
        token = await get_auth_token()
        assert token == 'test-token'


@pytest.mark.asyncio
async def test_get_auth_token_basic_fallback():
    """Test fallback to basic auth."""
    with patch.dict('os.environ', {}, clear=True):
        with patch('mcpgateway.services.cli_service.settings') as mock_settings:
            mock_settings.basic_auth_user = 'admin'
            mock_settings.basic_auth_password = 'secret'

            token = await get_auth_token()
            assert token.startswith('Basic ')


@pytest.mark.asyncio
async def test_get_auth_token_no_config():
    """Test when no auth is configured."""
    with patch.dict('os.environ', {}, clear=True):
        with patch('mcpgateway.services.cli_service.settings') as mock_settings:
            mock_settings.basic_auth_user = None
            mock_settings.basic_auth_password = None

            token = await get_auth_token()
            assert token is None


@pytest.mark.asyncio
async def test_authentication_error():
    """Test AuthenticationError exception."""
    error = AuthenticationError("Test auth error")
    assert str(error) == "Test auth error"
    assert isinstance(error, Exception)
    assert isinstance(error, CLIError)


@pytest.mark.asyncio
async def test_cli_error():
    """Test CLIError exception."""
    error = CLIError("Test CLI error")
    assert str(error) == "Test CLI error"
    assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_export_command_success():
    """Test successful export command execution."""
    export_data = {
        "metadata": {
            "entity_counts": {
                "tools": 5,
                "gateways": 2,
                "servers": 3
            }
        },
        "version": "1.0.0",
        "exported_at": "2023-01-01T00:00:00Z",
        "exported_by": "test_user",
        "source_gateway": "test-gateway"
    }

    with patch('mcpgateway.services.cli_service.make_authenticated_request', return_value=export_data):
        with patch('mcpgateway.services.cli_service.settings') as mock_settings:
            mock_settings.host = "localhost"
            mock_settings.port = 8000

            with patch('builtins.print') as mock_print:
                with tempfile.TemporaryDirectory() as temp_dir:
                    os.chdir(temp_dir)
                    await export_configuration(
                        types="tools,gateways",
                        tags="production",
                        include_inactive=True,
                        include_dependencies=False,
                        verbose=True,
                    )

                    # Verify print statements
                    mock_print.assert_any_call("Exporting configuration from gateway at http://localhost:8000")
                    mock_print.assert_any_call("✅ Export completed successfully!")
                    mock_print.assert_any_call("📊 Exported 10 total entities:")
                    mock_print.assert_any_call("   • tools: 5")
                    mock_print.assert_any_call("   • gateways: 2")
                    mock_print.assert_any_call("   • servers: 3")
                    mock_print.assert_any_call("\n🔍 Export details:")
                    mock_print.assert_any_call("   • Version: 1.0.0")
