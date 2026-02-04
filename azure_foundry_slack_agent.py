#!/usr/bin/env python3
"""
Azure AI Foundry Slack Agent with MCP
An agent that can answer questions about Slack channels, messages, and users
using the Slack MCP server
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# Load environment variables
load_dotenv()


def create_slack_agent():
    """
    Create an Azure AI Foundry agent with Slack MCP server integration

    Returns:
        tuple: (project_client, agent, openai_client)
    """
    # Initialize Azure AI Foundry project client
    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Get OpenAI client for responses
    openai_client = project_client.get_openai_client()

    # Configure the Slack MCP tool
    slack_mcp_tool = MCPTool(
        server_label="slack",
        server_url=os.environ["SLACK_MCP_SERVER_URL"],  # URL to your running Slack MCP server
        # Optional: Add authentication headers if needed
        # These can be passed during run time for security
    )

    # Create the agent with Slack MCP capabilities
    agent = project_client.agents.create_version(
        agent_name="SlackAgent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
            instructions="""You are a helpful Slack assistant that can answer questions about Slack workspaces.

You have access to the following Slack capabilities:
- List channels (public, private, DMs)
- Search for messages in channels
- View conversation history
- Get thread replies
- List users in the workspace

When answering questions:
1. Use the Slack MCP tools to retrieve real-time data from Slack
2. Provide clear, concise answers with relevant context
3. If you find multiple results, summarize them clearly
4. Always cite which channel or user information came from

Examples of questions you can answer:
- "What channels are available in the workspace?"
- "Find recent messages about 'deployment' in #tech channel"
- "Who are the users in this workspace?"
- "Show me the conversation history from #tech channel"
- "What's being discussed in the recent threads?"
""",
            tools=[slack_mcp_tool],
        ),
        description="Agent for querying and analyzing Slack workspace data via MCP",
    )

    print(f"✓ Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
    return project_client, agent, openai_client


def query_slack(openai_client, agent_name, question, slack_token=None):
    """
    Query Slack data through the agent

    Args:
        openai_client: OpenAI client instance
        agent_name: Name of the agent to use
        question: Question to ask about Slack
        slack_token: Optional Slack token to pass as header for authentication

    Returns:
        Response from the agent
    """
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)

    # Prepare extra body for agent reference
    extra_body = {
        "agent": {
            "name": agent_name,
            "type": "agent_reference"
        }
    }

    # Query the agent (MCP server uses env vars for auth, not runtime headers)
    response = openai_client.responses.create(
        input=question,
        extra_body=extra_body
    )

    print(f"\nResponse:")
    print(response.output_text)
    print('='*60)

    return response


def query_slack_streaming(openai_client, agent_name, question, slack_token=None):
    """
    Query Slack data through the agent with streaming response

    Args:
        openai_client: OpenAI client instance
        agent_name: Name of the agent to use
        question: Question to ask about Slack
        slack_token: Optional Slack token to pass as header for authentication
    """
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)
    print("\nStreaming response:")

    # Prepare extra body for agent reference
    extra_body = {
        "agent": {
            "name": agent_name,
            "type": "agent_reference"
        }
    }

    # Stream the response (MCP server uses env vars for auth, not runtime headers)
    stream_response = openai_client.responses.create(
        stream=True,
        input=question,
        extra_body=extra_body
    )

    full_response = ""
    for event in stream_response:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            full_response += event.delta
        elif event.type == "response.completed":
            print("\n" + '='*60)

    return full_response


def interactive_mode(openai_client, agent_name, slack_token=None):
    """
    Start an interactive session with the Slack agent

    Args:
        openai_client: OpenAI client instance
        agent_name: Name of the agent to use
        slack_token: Optional Slack token for authentication
    """
    print("\n" + "="*60)
    print("SLACK AGENT - INTERACTIVE MODE")
    print("="*60)
    print("Ask questions about your Slack workspace!")
    print("Type 'quit' or 'exit' to end the session")
    print("="*60)

    while True:
        try:
            question = input("\n🤔 Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not question:
                continue

            # Query with streaming for better UX
            query_slack_streaming(openai_client, agent_name, question, slack_token)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_queries(openai_client, agent_name, slack_token=None):
    """
    Run demo queries to showcase the agent's capabilities

    Args:
        openai_client: OpenAI client instance
        agent_name: Name of the agent to use
        slack_token: Optional Slack token for authentication
    """
    demo_questions = [
        "What channels are available in this Slack workspace?",
        "Show me recent messages from the #tech channel",
        "Who are the users in this workspace?",
        "Find messages mentioning 'deployment' or 'production' in #tech",
        "What was discussed in the recent conversation threads?",
    ]

    print("\n" + "="*60)
    print("RUNNING DEMO QUERIES")
    print("="*60)

    for question in demo_questions:
        query_slack(openai_client, agent_name, question, slack_token)
        input("\nPress Enter to continue to next question...")


def main():
    """Main function"""
    print("="*60)
    print("Azure AI Foundry Slack Agent with MCP")
    print("="*60)

    # Validate required environment variables
    required_vars = [
        "FOUNDRY_PROJECT_ENDPOINT",
        "FOUNDRY_MODEL_DEPLOYMENT_NAME",
        "SLACK_MCP_SERVER_URL",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("\n❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file")
        return

    # Optional: Get Slack token for authentication
    slack_token = os.getenv("SLACK_BOT_TOKEN") or os.getenv("SLACK_USER_TOKEN")
    if not slack_token:
        print("\n⚠️  Warning: No Slack token found. MCP server may need authentication.")
        print("  Set SLACK_BOT_TOKEN or SLACK_USER_TOKEN in .env file")

    try:
        # Create the agent
        print("\n📝 Creating Slack agent with MCP integration...")
        project_client, agent, openai_client = create_slack_agent()

        # Choose mode
        print("\n" + "="*60)
        print("Select mode:")
        print("  1. Interactive mode (ask your own questions)")
        print("  2. Demo mode (run predefined queries)")
        print("="*60)

        mode = input("\nEnter choice (1 or 2): ").strip()

        if mode == "1":
            interactive_mode(openai_client, agent.name, slack_token)
        elif mode == "2":
            demo_queries(openai_client, agent.name, slack_token)
        else:
            print("Invalid choice. Exiting.")
            return

        # Cleanup
        print("\n🧹 Cleaning up...")
        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version
        )
        print("✓ Agent deleted")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
