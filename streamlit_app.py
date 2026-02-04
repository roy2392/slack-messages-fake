#!/usr/bin/env python3
"""
Streamlit UI for Azure AI Foundry Slack Agent
==============================================

A simple chat interface to interact with Slack via Azure AI Foundry MCP integration.

Usage:
    streamlit run streamlit_app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Slack AI Assistant",
    page_icon="💬",
    layout="wide"
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

def initialize_agent():
    """Initialize the Azure AI Foundry agent with Slack MCP tools"""
    if st.session_state.agent is not None:
        return st.session_state.agent

    with st.spinner("🔌 Connecting to Azure AI Foundry..."):
        # Initialize clients
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
        agent = project_client.agents.create_version(
            agent_name="SlackStreamlitAgent",
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_DEPLOYMENT_NAME"],
                instructions="""You are a helpful Slack workspace assistant.
                Use the available Slack MCP tools to help users query and interact
                with their Slack workspace. Be concise and friendly.""",
                tools=[slack_mcp_tool],
            ),
        )

        # Store in session state
        st.session_state.project_client = project_client
        st.session_state.openai_client = openai_client
        st.session_state.agent = agent

        return agent

def send_message(user_input):
    """Send a message to the agent and get response"""
    try:
        response = st.session_state.openai_client.responses.create(
            input=user_input,
            extra_body={
                "agent": {
                    "name": st.session_state.agent.name,
                    "type": "agent_reference"
                }
            }
        )
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def display_response(response):
    """Display the agent's response with proper formatting"""
    if response is None:
        return

    # Display text response
    if response.output_text:
        with st.chat_message("assistant"):
            st.markdown(response.output_text)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.output_text
        })

    # Check for additional output items
    if hasattr(response, 'output') and response.output:
        # Check for tool discoveries
        for item in response.output:
            if item.type == 'mcp_list_tools':
                with st.chat_message("assistant"):
                    st.info(f"🔧 Discovered {len(item.tools)} Slack tools")

            elif item.type == 'mcp_approval_request':
                with st.chat_message("assistant"):
                    st.warning("""
                    ⚠️ **Tool Approval Required**

                    The agent wants to call a Slack API tool but requires approval.
                    This is a safety feature in Azure AI Foundry.

                    **What's happening:**
                    - The agent identified it needs to use a Slack MCP tool
                    - Azure requires manual approval before executing external API calls
                    - This prevents unauthorized actions

                    **Next steps:**
                    - In production, you would implement an approval workflow
                    - For now, the agent understands your intent but cannot execute
                    """)

                st.session_state.messages.append({
                    "role": "system",
                    "content": "Tool approval required (MCP safety feature)"
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
        **Model:** {os.environ['FOUNDRY_MODEL_DEPLOYMENT_NAME']}
        """)
    else:
        st.warning("⚠️ Agent Not Initialized")

    st.divider()

    # MCP Server status
    st.subheader("🔌 MCP Server")
    st.code(os.environ.get('SLACK_MCP_SERVER_URL', 'Not configured'))

    st.divider()

    # Sample queries
    st.subheader("💡 Sample Queries")
    st.markdown("""
    Try asking:
    - "What tools do you have?"
    - "List all channels"
    - "Show recent messages from #tech"
    - "What can you do?"
    """)

    st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Reset agent button
    if st.button("🔄 Reset Agent", use_container_width=True):
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
        st.rerun()

# Main content
st.title("💬 Slack AI Assistant")
st.caption("Chat with your Slack workspace using Azure AI Foundry + MCP")

# Initialize agent
agent = initialize_agent()

if agent:
    st.success("🎉 Connected! The Azure AI Foundry agent is ready to help with your Slack workspace.")

    # Display chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(content)
        elif role == "system":
            with st.chat_message("assistant"):
                st.info(content)

    # Chat input
    if prompt := st.chat_input("Ask me about your Slack workspace..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and display response
        with st.spinner("🤔 Thinking..."):
            response = send_message(prompt)
            display_response(response)
else:
    st.error("Failed to initialize agent. Please check your configuration.")

# Footer
st.divider()
st.caption("""
**Status:** Integration Working ✅
**MCP Protocol:** HTTP mode
**Tools:** 7 Slack tools available
**Approval:** Manual approval required for tool execution
""")
