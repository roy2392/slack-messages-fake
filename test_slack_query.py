#!/usr/bin/env python3
"""Test Azure AI Foundry agent calling Slack MCP tools"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

# Create MCP tool
slack_mcp_tool = MCPTool(
    server_label="slack",
    server_url=os.environ["SLACK_MCP_SERVER_URL"],
)

# Create agent
print("Creating agent...")
agent = project_client.agents.create_version(
    agent_name="SlackQueryAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a Slack assistant. Use the Slack MCP tools to answer questions about the Slack workspace.",
        tools=[slack_mcp_tool],
    ),
)

print(f"✓ Agent created: {agent.name} (version {agent.version})")

print("\nAsking: 'List all public channels in the workspace'")
print("-" * 60)

try:
    response = openai_client.responses.create(
        input="List all public channels in the workspace",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )

    print(f"Response: {response.output_text}")

    # Check if any tool calls were made
    if hasattr(response, 'output'):
        print(f"\nNumber of output items: {len(response.output)}")
        for i, item in enumerate(response.output):
            print(f"Item {i+1} type: {item.type}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("-" * 60)

print("\nCleaning up...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done")
