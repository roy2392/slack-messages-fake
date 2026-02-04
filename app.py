#!/usr/bin/env python3
"""
Slack AI Assistant - Streamlit UI
Azure AI Foundry + Slack MCP Integration

This is the main application with improved trace formatting for Azure AI Foundry.
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Slack AI Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "project_client" not in st.session_state:
    st.session_state.project_client = None
if "openai_client" not in st.session_state:
    st.session_state.openai_client = None
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

def initialize_agent():
    """Initialize the Azure AI Foundry agent with Slack MCP tools"""
    if st.session_state.agent is not None:
        return st.session_state.agent

    with st.spinner("🔌 Connecting to Azure AI Foundry..."):
        try:
            # Initialize clients
            project_client = AIProjectClient(
                endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                credential=DefaultAzureCredential(),
            )
            openai_client = project_client.get_openai_client()

            # Create MCP tool with auto-approval
            slack_mcp_tool = MCPTool(
                server_label="slack",
                server_url=os.environ["SLACK_MCP_SERVER_URL"],
                require_approval="never"  # Auto-approve for seamless execution
            )

            # Create agent with enhanced instructions for better tracing
            agent = project_client.agents.create_version(
                agent_name="SlackAssistant",
                definition=PromptAgentDefinition(
                    model=os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o"),
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

            # Create a conversation for better trace organization
            conversation = project_client.agents.create_conversation()

            # Store in session state
            st.session_state.project_client = project_client
            st.session_state.openai_client = openai_client
            st.session_state.agent = agent
            st.session_state.conversation_id = conversation.id

            return agent

        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            return None

def send_message(user_input):
    """Send a message to the agent with proper trace formatting"""
    try:
        # Add metadata for better trace organization
        response = st.session_state.openai_client.responses.create(
            input=user_input,
            extra_body={
                "agent": {
                    "name": st.session_state.agent.name,
                    "type": "agent_reference"
                },
                "metadata": {
                    "session_id": st.session_state.conversation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_query": user_input[:100]  # First 100 chars for trace search
                }
            }
        )
        return response

    except Exception as e:
        st.error(f"Error: {e}")
        return None

def format_tool_call(item):
    """Format tool call information for display"""
    if hasattr(item, 'tool_name'):
        tool_info = f"**Tool:** `{item.tool_name}`"
        if hasattr(item, 'server_label'):
            tool_info += f" (Server: `{item.server_label}`)"
        return tool_info
    return None

def display_response(response):
    """Display the agent's response with enhanced formatting"""
    if response is None:
        return

    # Track tool calls for trace information
    tool_calls = []

    # Check output items first
    if hasattr(response, 'output') and response.output:
        for item in response.output:
            if item.type == 'mcp_list_tools':
                st.info(f"🔧 **Tool Discovery:** Found {len(item.tools)} Slack tools")

            elif item.type == 'mcp_call':
                tool_info = format_tool_call(item)
                if tool_info:
                    tool_calls.append(tool_info)

            elif item.type == 'mcp_approval_request':
                st.warning("⚠️ **Approval Required:** The agent needs permission to execute this tool.")

    # Display tool calls if any
    if tool_calls:
        with st.expander("🔄 Tool Calls", expanded=False):
            for i, tool_call in enumerate(tool_calls, 1):
                st.markdown(f"{i}. {tool_call}")

    # Display main text response
    if response.output_text:
        with st.chat_message("assistant"):
            st.markdown(response.output_text)

            # Add trace metadata in collapsed section
            if hasattr(response, 'id'):
                with st.expander("📊 Trace Information", expanded=False):
                    st.caption(f"Response ID: `{response.id}`")
                    if hasattr(response, 'usage'):
                        st.caption(f"Tokens: {response.usage.total_tokens} total "
                                 f"({response.usage.input_tokens} input, "
                                 f"{response.usage.output_tokens} output)")

        st.session_state.messages.append({
            "role": "assistant",
            "content": response.output_text,
            "tool_calls": len(tool_calls)
        })

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")

    # Show agent status
    if st.session_state.agent:
        st.success("✅ Agent Connected")
        st.info(f"""
**Agent:** {st.session_state.agent.name}
**Version:** {st.session_state.agent.version}
**Model:** {os.environ.get('FOUNDRY_MODEL_DEPLOYMENT_NAME', 'gpt-4o')}
**Auto-Approval:** ✅ ENABLED
""")
        if st.session_state.conversation_id:
            st.caption(f"Conversation: `{st.session_state.conversation_id[:8]}...`")
    else:
        st.warning("⚠️ Agent Not Initialized")

    st.divider()

    # MCP Server status
    st.subheader("🔌 MCP Server")
    mcp_url = os.environ.get('SLACK_MCP_SERVER_URL', 'Not configured')
    st.code(mcp_url, language=None)

    # Check if localhost or remote
    if 'localhost' in mcp_url or '127.0.0.1' in mcp_url:
        st.caption("⚠️ Using local server")
    elif 'ngrok' in mcp_url:
        st.caption("🌐 Using ngrok tunnel")
    else:
        st.caption("☁️ Using remote server")

    st.divider()

    # Sample queries
    st.subheader("💡 Sample Queries")
    samples = [
        "What channels are available?",
        "Show recent messages from #tech",
        "What did Alice say about errors?",
        "List all public channels",
        "Search for messages about deployment"
    ]

    for sample in samples:
        if st.button(f"💬 {sample}", key=sample, use_container_width=True):
            # Trigger query
            st.session_state.pending_query = sample
            st.rerun()

    st.divider()

    # Controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button("🔄 Reset", use_container_width=True, help="Reset agent connection"):
            if st.session_state.agent and st.session_state.project_client:
                try:
                    st.session_state.project_client.agents.delete_version(
                        agent_name=st.session_state.agent.name,
                        agent_version=st.session_state.agent.version
                    )
                except:
                    pass
            st.session_state.agent = None
            st.session_state.project_client = None
            st.session_state.openai_client = None
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

    st.divider()

    # Footer
    st.caption("Built with Azure AI Foundry + MCP")
    st.caption("v1.0.0")

# Main content
st.title("💬 Slack AI Assistant")
st.caption("Ask questions about your Slack workspace using natural language")

# Initialize agent
agent = initialize_agent()

if agent:
    st.success("🎉 Ready! Ask me anything about your Slack workspace.")

    # Display chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)
            # Show tool call badge if any
            if role == "assistant" and message.get("tool_calls", 0) > 0:
                st.caption(f"🔧 {message['tool_calls']} tool call(s)")

    # Handle pending query from sample buttons
    if hasattr(st.session_state, 'pending_query'):
        prompt = st.session_state.pending_query
        del st.session_state.pending_query

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and display response
        with st.spinner("🤔 Thinking..."):
            response = send_message(prompt)
            display_response(response)
        st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask about your Slack workspace...", key="chat_input"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and display response
        with st.spinner("🤔 Thinking..."):
            response = send_message(prompt)
            display_response(response)

else:
    st.error("❌ Failed to initialize agent. Please check your configuration.")
    st.info("""
**Troubleshooting:**
1. Verify `.env` file has all required credentials
2. Check MCP server is running
3. Ensure Azure credentials are valid
4. Review logs for error details
""")

# Footer
st.divider()
st.caption("""
**Status:** Integration Active ✅ | **Protocol:** MCP HTTP | **Tools:** Auto-Approved
[Documentation](https://github.com/roy2392/slack-messages-fake) • Azure AI Foundry + Slack MCP
""")
