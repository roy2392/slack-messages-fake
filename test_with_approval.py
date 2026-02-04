#!/usr/bin/env python3
"""Test Azure AI Foundry agent with MCP approval handling"""

import os
import json
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
    agent_name="SlackApprovalAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a Slack assistant. Use the Slack MCP tools to answer questions.",
        tools=[slack_mcp_tool],
    ),
)

print(f"✓ Agent created: {agent.name} (version {agent.version})")

print("\nAsking: 'List all public channels'")
print("-" * 60)

try:
    response = openai_client.responses.create(
        input="List all public channels",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )

    print(f"Response text: {response.output_text}")

    # Check for approval requests
    if hasattr(response, 'output'):
        for item in response.output:
            if item.type == 'mcp_approval_request':
                print(f"\n📋 MCP Approval Request Detected!")
                print(f"Full approval request: {json.dumps(item.model_dump(), indent=2, default=str)}")

                # Try to extract approval details
                if hasattr(item, 'tool_call_id'):
                    print(f"Tool call ID: {item.tool_call_id}")
                if hasattr(item, 'server_label'):
                    print(f"Server label: {item.server_label}")
                if hasattr(item, 'tool_name'):
                    print(f"Tool name: {item.tool_name}")
                if hasattr(item, 'arguments'):
                    print(f"Arguments: {item.arguments}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("-" * 60)

print("\nCleaning up...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done")
