#!/usr/bin/env python3
"""Quick test of the Azure AI Foundry Slack Agent"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

load_dotenv()

# Initialize Azure AI Foundry project client
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Get OpenAI client
openai_client = project_client.get_openai_client()

# Configure the Slack MCP tool
slack_mcp_tool = MCPTool(
    server_label="slack",
    server_url=os.environ["SLACK_MCP_SERVER_URL"],
)

print("Creating agent...")
agent = project_client.agents.create_version(
    agent_name="SlackTestAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a Slack assistant. Answer questions about Slack channels and messages.",
        tools=[slack_mcp_tool],
    ),
    description="Test agent for Slack MCP",
)

print(f"✓ Agent created: {agent.name} (version {agent.version})")

# Test query
print("\nAsking: 'What channels are in this Slack workspace?'")
print("-" * 60)

response = openai_client.responses.create(
    input="What channels are in this Slack workspace?",
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
)

print(f"Response: {response.output_text}")
print("-" * 60)

# Cleanup
print("\nCleaning up...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done")
