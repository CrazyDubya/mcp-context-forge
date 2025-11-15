# -*- coding: utf-8 -*-
"""Location: ./tests/unit/mcpgateway/test_cli.py
Copyright 2025
SPDX-License-Identifier: Apache-2.0
Authors: Mihai Criveti

Tests for the mcpgateway CLI module (cli.py).
"""

# Future
from __future__ import annotations

# Standard
import sys
from typing import Any, Dict, List
from unittest.mock import patch, AsyncMock

# Third-Party
import pytest
from typer.testing import CliRunner

# First-Party
import mcpgateway.cli as cli
from mcpgateway import __version__

runner = CliRunner()


def test_version():
    """Test the --version flag."""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"mcpgateway {__version__}" in result.stdout


def test_run_command(monkeypatch):
    """Test the run command."""
    mock_uvicorn_run = lambda *args, **kwargs: None
    monkeypatch.setattr(cli.uvicorn, "run", mock_uvicorn_run)
    result = runner.invoke(cli.app, ["run"])
    assert result.exit_code == 0


def test_export_command(monkeypatch):
    """Test the export command."""
    with patch("mcpgateway.services.cli_service.export_configuration", new_callable=AsyncMock) as mock_export:
        result = runner.invoke(cli.app, ["export"])
        assert result.exit_code == 0
        mock_export.assert_called_once()


def test_import_command(monkeypatch):
    """Test the import command."""
    with patch("mcpgateway.services.cli_service.import_configuration", new_callable=AsyncMock) as mock_import:
        result = runner.invoke(cli.app, ["import", "dummy_file.json"])
        assert result.exit_code == 0
        mock_import.assert_called_once()


def test_plugin_create_command(monkeypatch):
    """Test the plugin create command."""
    mock_cookiecutter = lambda *args, **kwargs: None
    monkeypatch.setattr(cli, "cookiecutter", mock_cookiecutter)
    result = runner.invoke(cli.app, ["plugin", "create", "My Test Plugin"])
    assert result.exit_code == 0
    assert "Plugin 'My Test Plugin' created successfully" in result.stdout
