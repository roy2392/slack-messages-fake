#!/usr/bin/env python3
"""Test the auto-approval agent directly"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

load_dotenv()

print("="*60)
print("Testing Auto-Approval Agent")
print("="*60)

# Initialize clients
print("\n1. Initializing Azure AI Foundry client...")
project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# Create MCP tool with auto-approval
print("2. Creating MCP tool with require_approval='never'...")
slack_mcp_tool = MCPTool(
    server_label="slack",
    server_url=os.environ["SLACK_MCP_SERVER_URL"],
    require_approval="never"  # Auto-approve all tool calls
)

# Create agent
print("3. Creating agent...")
agent = project_client.agents.create_version(
    agent_name="TestAutoApprovalAgent",
    definition=PromptAgentDefinition(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
        instructions="""You are a helpful Slack workspace assistant.
        When users ask about messages or information from Slack, actively use
        the available tools to fetch real data. Always specify channel names
        when searching for messages.""",
        tools=[slack_mcp_tool],
    ),
)

print(f"✓ Agent created: {agent.name} v{agent.version}")

# Test query
print("\n" + "="*60)
print("Test Query")
print("="*60)
query = "What was the error rate that Alice reported in the #tech channel?"
print(f"\nAsking: '{query}'")
print("\n" + "-"*60)

try:
    response = openai_client.responses.create(
        input=query,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )

    print("\n📋 Response Text:")
    print("-"*60)
    print(response.output_text if response.output_text else "(No text response)")
    print("-"*60)

    # Check output items
    if hasattr(response, 'output') and response.output:
        print(f"\n📦 Output Items: {len(response.output)}")
        for i, item in enumerate(response.output, 1):
            print(f"\n{i}. Type: {item.type}")

            if item.type == 'mcp_call_tool':
                print(f"   ✓ Tool Called: {item.tool_name}")
                print(f"   ✓ Server: {item.server_label}")
                if hasattr(item, 'arguments'):
                    print(f"   ✓ Arguments: {item.arguments}")

            elif item.type == 'mcp_approval_request':
                print("   ⚠️ Approval request (shouldn't happen with auto-approval!)")

            elif item.type == 'mcp_list_tools':
                print(f"   ✓ Discovered {len(item.tools)} tools")

    # Check usage
    if hasattr(response, 'usage'):
        print(f"\n💰 Token Usage:")
        print(f"   Input: {response.usage.input_tokens}")
        print(f"   Output: {response.usage.output_tokens}")
        print(f"   Total: {response.usage.total_tokens}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Cleaning up...")
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("✓ Done!")
print("="*60)
