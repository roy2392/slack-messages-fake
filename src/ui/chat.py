"""
Chat Interface Component
Handles chat display and message interactions
"""

import streamlit as st
from .response import display_response


def send_message(user_input):
    """Send a message to the agent"""
    try:
        response = st.session_state.agent_manager.send_message(user_input)
        return response
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def render_chat_interface():
    """Render the main chat interface"""
    st.title("💬 Slack AI Assistant")
    st.caption("Ask questions about your Slack workspace using natural language")

    if st.session_state.agent:
        st.success("🎉 Ready! Ask me anything about your Slack workspace.")

        _display_chat_history()
        _handle_pending_query()
        _handle_chat_input()

    else:
        _display_error_state()

    _render_footer()


def _display_chat_history():
    """Display existing chat messages"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)
            if role == "assistant" and message.get("tool_calls", 0) > 0:
                st.caption(f"🔧 {message['tool_calls']} tool call(s)")


def _handle_pending_query():
    """Handle queries from sample buttons"""
    if hasattr(st.session_state, 'pending_query'):
        prompt = st.session_state.pending_query
        del st.session_state.pending_query

        _process_user_message(prompt)
        st.rerun()


def _handle_chat_input():
    """Handle direct chat input"""
    if prompt := st.chat_input("Ask about your Slack workspace...", key="chat_input"):
        _process_user_message(prompt)


def _process_user_message(prompt):
    """Process and display user message and response"""
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get and display agent response
    with st.spinner("🤔 Thinking..."):
        response = send_message(prompt)
        display_response(response)


def _display_error_state():
    """Display error message when agent fails to initialize"""
    st.error("❌ Failed to initialize agent. Please check your configuration.")
    st.info("""
**Troubleshooting:**
1. Verify `.env` file has all required credentials
2. Check MCP server is running
3. Ensure Azure credentials are valid
4. Review logs for error details
""")


def _render_footer():
    """Render chat interface footer"""
    st.divider()
    st.caption("""
**Status:** Integration Active ✅ | **Protocol:** MCP HTTP | **Tools:** Auto-Approved
[Documentation](https://github.com/roy2392/slack-messages-fake) • Azure AI Foundry + Slack MCP
""")
