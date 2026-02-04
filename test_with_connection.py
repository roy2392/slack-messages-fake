#!/usr/bin/env python3
"""Test Azure AI Foundry agent with MCP using project connection"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, ConnectionType

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

print("Step 1: Creating a project connection for MCP...")
try:
    # Try to create a connection for the MCP server
    connection = project_client.connections.create_or_update(
        connection_name="slack-mcp-connection",
        properties={
            "category": "MCP",
            "target": os.environ["SLACK_MCP_SERVER_URL"],
            "authType": "None",  # Unauthenticated
            "isSharedToAll": True,
        }
    )
    print(f"✓ Connection created: {connection.name}")
    connection_id = connection.id
except Exception as e:
    print(f"Note: {e}")
    # If connection already exists or creation fails, try to get it
    try:
        connections = list(project_client.connections.list())
        slack_conn = [c for c in connections if "slack" in c.name.lower()]
        if slack_conn:
            connection_id = slack_conn[0].id
            print(f"✓ Using existing connection: {slack_conn[0].name}")
        else:
            print("⚠️ No Slack connection found, will use server_url directly")
            connection_id = None
    except:
        connection_id = None

print("\nStep 2: Creating agent with MCP tool...")
# Create MCP tool
if connection_id:
    mcp_tool = MCPTool(
        server_label="slack",
        project_connection_id=connection_id,
    )
    print(f"Using connection ID: {connection_id}")
else:
    mcp_tool = MCPTool(
        server_label="slack",
        server_url=os.environ["SLACK_MCP_SERVER_URL"],
    )
    print(f"Using server URL: {os.environ['SLACK_MCP_SERVER_URL']}")

# Get OpenAI client
openai_client = project_client.get_openai_client()

# Create agent
agent = project_client.agents.create_version(
    agent_name="SlackDebugAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a Slack assistant. List available tools and answer questions.",
        tools=[mcp_tool],
    ),
    description="Debug agent for Slack MCP with connection",
)

print(f"✓ Agent created: {agent.name} (version {agent.version})")

print("\nStep 3: Testing agent with simple query...")
print("-" * 60)

try:
    response = openai_client.responses.create(
        input="What tools do you have available?",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )

    print(f"Response: {response.output_text}")

    # Check for any consent or approval requests
    if hasattr(response, 'output'):
        for item in (response.output or []):
            print(f"\nOutput item type: {item.type}")
            if item.type == "oauth_consent_request":
                print(f"OAuth consent needed: {item.consent_link}")
            elif item.type == "mcp_approval_request":
                print(f"MCP approval needed")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("-" * 60)

print("\nStep 4: Cleanup...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done")
