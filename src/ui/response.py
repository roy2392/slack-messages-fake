"""
Response Formatting and Display
Handles agent response formatting and rendering
"""

import streamlit as st


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

    tool_calls = []

    # Process output items
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

    # Display tool calls
    if tool_calls:
        with st.expander("🔄 Tool Calls", expanded=False):
            for i, tool_call in enumerate(tool_calls, 1):
                st.markdown(f"{i}. {tool_call}")

    # Display main response
    if response.output_text:
        with st.chat_message("assistant"):
            st.markdown(response.output_text)

            # Add trace metadata
            if hasattr(response, 'id'):
                with st.expander("📊 Trace Information", expanded=False):
                    st.caption(f"Response ID: `{response.id}`")
                    if hasattr(response, 'usage'):
                        st.caption(f"Tokens: {response.usage.total_tokens} total "
                                 f"({response.usage.input_tokens} input, "
                                 f"{response.usage.output_tokens} output)")

        # Store in session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.output_text,
            "tool_calls": len(tool_calls)
        })
