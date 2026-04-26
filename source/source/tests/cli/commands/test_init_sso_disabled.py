# ABOUTME: Test suite for init command with SSO disabled
# ABOUTME: Ensures proper handling of config when sso_enabled is False

"""Test suite for init command with SSO disabled."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Imports after path setup
# ruff: noqa: E402
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from claude_code_with_bedrock.cli.commands.init import InitCommand


class TestInitCommandSSODisabled:
    """Test InitCommand when SSO is disabled."""

    @pytest.fixture
    def init_command(self):
        """Create InitCommand instance."""
        return InitCommand()

    @pytest.fixture
    def config_with_sso_disabled(self):
        """Sample config with SSO disabled."""
        return {
            "sso_enabled": False,
            "credential_storage": "keyring",
            "aws": {
                "region": "us-east-1",
                "identity_pool_name": "claude-code-auth",
                "selected_model": "anthropic.claude-sonnet-4-5-20250929-v1:0",
            },
            "monitoring": {
                "enabled": True,
            },
            "quota": {
                "enabled": True,
                "monthly_limit": 225000000,
                "monthly_enforcement_mode": "block",
                "check_interval": 30,
            },
        }

    @pytest.fixture
    def config_with_sso_enabled(self):
        """Sample config with SSO enabled."""
        return {
            "sso_enabled": True,
            "okta": {
                "domain": "example.okta.com",
                "client_id": "abc123def456ghi789jkl",
            },
            "credential_storage": "keyring",
            "aws": {
                "region": "us-east-1",
                "identity_pool_name": "claude-code-auth",
                "selected_model": "anthropic.claude-sonnet-4-5-20250929-v1:0",
            },
            "monitoring": {
                "enabled": True,
            },
            "quota": {
                "enabled": True,
                "monthly_limit": 225000000,
                "monthly_enforcement_mode": "block",
                "check_interval": 30,
            },
        }

    @patch("claude_code_with_bedrock.cli.commands.init.Console")
    @patch("claude_code_with_bedrock.cli.commands.init.questionary")
    def test_review_configuration_sso_disabled(self, mock_questionary, mock_console_class, init_command, config_with_sso_disabled):
        """Test _review_configuration when SSO is disabled."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        mock_questionary.confirm.return_value.ask.return_value = True

        # This should not raise KeyError
        result = init_command._review_configuration(config_with_sso_disabled)

        # Verify it returns True
        assert result is True

        # Verify console.print was called with a table
        assert mock_console.print.called

    @patch("claude_code_with_bedrock.cli.commands.init.Console")
    @patch("claude_code_with_bedrock.cli.commands.init.questionary")
    def test_review_configuration_sso_enabled(self, mock_questionary, mock_console_class, init_command, config_with_sso_enabled):
        """Test _review_configuration when SSO is enabled."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console
        mock_questionary.confirm.return_value.ask.return_value = True

        # This should work with SSO enabled
        result = init_command._review_configuration(config_with_sso_enabled)

        # Verify it returns True
        assert result is True

        # Verify console.print was called with a table
        assert mock_console.print.called

    @patch("claude_code_with_bedrock.cli.commands.init.Console")
    def test_show_existing_deployment_sso_disabled(self, mock_console_class, init_command, config_with_sso_disabled):
        """Test _show_existing_deployment when SSO is disabled."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        # This should not raise KeyError
        init_command._show_existing_deployment(config_with_sso_disabled)

        # Verify console.print was called
        assert mock_console.print.called

        # Verify it shows AWS SSO message
        calls = mock_console.print.call_args_list
        auth_calls = [call for call in calls if "Authentication" in str(call) or "OIDC" in str(call) or "AWS SSO" in str(call)]
        assert len(auth_calls) > 0, "Should display authentication info"

    @patch("claude_code_with_bedrock.cli.commands.init.Console")
    def test_show_existing_deployment_sso_enabled(self, mock_console_class, init_command, config_with_sso_enabled):
        """Test _show_existing_deployment when SSO is enabled."""
        mock_console = MagicMock()
        mock_console_class.return_value = mock_console

        # This should work with SSO enabled
        init_command._show_existing_deployment(config_with_sso_enabled)

        # Verify console.print was called
        assert mock_console.print.called

        # Verify it shows OIDC provider
        calls = mock_console.print.call_args_list
        oidc_calls = [call for call in calls if "example.okta.com" in str(call)]
        assert len(oidc_calls) > 0, "Should display OIDC provider domain"

    def test_config_without_okta_key(self, init_command):
        """Test that config without 'okta' key is handled correctly."""
        config = {
            "sso_enabled": False,
            "aws": {
                "region": "us-east-1",
                "identity_pool_name": "test-pool",
            },
            "monitoring": {"enabled": False},
        }

        # Verify okta key doesn't exist
        assert "okta" not in config

        # These should not raise KeyError
        with patch("claude_code_with_bedrock.cli.commands.init.Console"):
            with patch("claude_code_with_bedrock.cli.commands.init.questionary.confirm") as mock_confirm:
                mock_confirm.return_value.ask.return_value = True
                init_command._review_configuration(config)

        with patch("claude_code_with_bedrock.cli.commands.init.Console"):
            init_command._show_existing_deployment(config)
