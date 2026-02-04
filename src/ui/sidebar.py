"""
Sidebar Component
Renders the Streamlit sidebar with configuration and controls
"""

import os
import streamlit as st
from session import reset_agent, clear_chat_history


def render_sidebar():
    """Render the application sidebar"""
    with st.sidebar:
        st.title("⚙️ Configuration")

        _render_agent_status()
        st.divider()

        _render_mcp_status()
        st.divider()

        _render_sample_queries()
        st.divider()

        _render_controls()
        st.divider()

        _render_footer()


def _render_agent_status():
    """Display agent connection status"""
    if st.session_state.agent:
        st.success("✅ Agent Connected")
        st.info(f"""
**Agent:** {st.session_state.agent.name}
**Version:** {st.session_state.agent.version}
**Model:** {os.environ.get('FOUNDRY_MODEL_DEPLOYMENT_NAME', 'gpt-4o')}
**Auto-Approval:** ✅ ENABLED
""")
        if st.session_state.agent_manager and st.session_state.agent_manager.conversation_id:
            st.caption(f"Conversation: `{st.session_state.agent_manager.conversation_id[:8]}...`")
    else:
        st.warning("⚠️ Agent Not Initialized")


def _render_mcp_status():
    """Display MCP server status"""
    st.subheader("🔌 MCP Server")
    mcp_url = os.environ.get('SLACK_MCP_SERVER_URL', 'Not configured')
    st.code(mcp_url, language=None)

    if 'localhost' in mcp_url or '127.0.0.1' in mcp_url:
        st.caption("⚠️ Using local server")
    elif 'ngrok' in mcp_url:
        st.caption("🌐 Using ngrok tunnel")
    else:
        st.caption("☁️ Using remote server")


def _render_sample_queries():
    """Display sample query buttons"""
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
            st.session_state.pending_query = sample
            st.rerun()


def _render_controls():
    """Display control buttons"""
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
            clear_chat_history()
            st.rerun()

    with col2:
        if st.button("🔄 Reset", use_container_width=True, help="Reset agent connection"):
            reset_agent()
            st.rerun()


def _render_footer():
    """Display sidebar footer"""
    st.caption("Built with Azure AI Foundry + MCP")
    st.caption("v1.1.0")
