"""
Azure AI Foundry Agent Management
"""

from typing import Optional
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

from config import AppConfig


class SlackAgent:
    """Manages Azure AI Foundry agent with Slack MCP integration"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.project_client = None
        self.openai_client = None
        self.agent = None
        self.conversation_id = None

    def initialize(self):
        """Initialize Azure AI Foundry agent"""
        # Initialize clients with Azure credentials
        self.project_client = AIProjectClient(
            endpoint=self.config.azure.endpoint,
            credential=DefaultAzureCredential(),
        )
        self.openai_client = self.project_client.get_openai_client()

        # Create MCP tool with auto-approval
        slack_mcp_tool = MCPTool(
            server_label="slack",
            server_url=self.config.slack.mcp_server_url,
            require_approval="never"
        )

        # Create agent
        self.agent = self.project_client.agents.create_version(
            agent_name="SlackAssistant",
            definition=PromptAgentDefinition(
                model=self.config.azure.model,
                instructions="""You are a helpful Slack workspace assistant.

Use the available Slack MCP tools to help users query and interact with their workspace.

When responding:
1. Be clear and concise
2. Use markdown formatting for better readability
3. Cite specific messages or channels when relevant
4. Provide actionable information

Available actions:
- List channels
- Read message history
- Search for specific messages
- Get channel information
- Read thread replies
""",
                tools=[slack_mcp_tool],
            ),
            description="Slack workspace AI assistant with MCP integration"
        )

        # Set conversation ID for trace organization (optional)
        self.conversation_id = f"session-{self.agent.name}-{self.agent.version}"

        return self.agent

    def send_message(self, user_input: str):
        """Send message to agent with trace metadata"""
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        response = self.openai_client.responses.create(
            input=user_input,
            extra_body={
                "agent": {
                    "name": self.agent.name,
                    "type": "agent_reference"
                },
                "metadata": {
                    "session_id": self.conversation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_query": user_input[:100]
                }
            }
        )
        return response

    def cleanup(self):
        """Clean up resources"""
        if self.agent and self.project_client:
            try:
                self.project_client.agents.delete_version(
                    agent_name=self.agent.name,
                    agent_version=self.agent.version
                )
            except:
                pass
