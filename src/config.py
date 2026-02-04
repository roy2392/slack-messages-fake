"""
Configuration management for Slack AI Assistant
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AzureConfig:
    """Azure AI Foundry configuration"""
    endpoint: str
    api_key: str
    model: str = "gpt-4o"

    @classmethod
    def from_env(cls) -> "AzureConfig":
        """Load configuration from environment variables"""
        return cls(
            endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            api_key=os.environ["FOUNDRY_API_KEY"],
            model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o")
        )


@dataclass
class SlackConfig:
    """Slack configuration"""
    bot_token: str
    workspace: str
    mcp_server_url: str

    @classmethod
    def from_env(cls) -> "SlackConfig":
        """Load configuration from environment variables"""
        return cls(
            bot_token=os.environ["SLACK_BOT_TOKEN"],
            workspace=os.environ.get("SLACK_WORKSPACE", "default"),
            mcp_server_url=os.environ.get("SLACK_MCP_SERVER_URL", "http://localhost:13080/mcp")
        )


@dataclass
class AppConfig:
    """Application configuration"""
    azure: AzureConfig
    slack: SlackConfig
    debug: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load full configuration from environment"""
        return cls(
            azure=AzureConfig.from_env(),
            slack=SlackConfig.from_env(),
            debug=os.environ.get("DEBUG", "false").lower() == "true"
        )
