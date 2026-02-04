#!/usr/bin/env python3
"""Test Azure AI Foundry agent with detailed response inspection"""

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
    agent_name="SlackDetailedTestAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a Slack assistant. Use the available Slack MCP tools to answer questions about the Slack workspace.",
        tools=[slack_mcp_tool],
    ),
    description="Test agent with detailed logging"
)

print(f"✓ Agent created: {agent.name} (version {agent.version})")

print("\nAsking: 'List all available tools and their capabilities'")
print("-" * 60)

try:
    response = openai_client.responses.create(
        input="List all available tools and their capabilities",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )

    print(f"\nResponse type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    print(f"\nOutput text: {response.output_text}")

    # Check all response attributes
    if hasattr(response, 'output'):
        print(f"\nOutput: {response.output}")

    if hasattr(response, 'usage'):
        print(f"\nUsage: {response.usage}")

    if hasattr(response, 'model_dump'):
        print(f"\nFull response dump:")
        print(json.dumps(response.model_dump(), indent=2, default=str))

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("-" * 60)

print("\nCleaning up...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done")
