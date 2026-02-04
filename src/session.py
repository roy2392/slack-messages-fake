"""
Session State Management
Handles Streamlit session state initialization and management
"""

import streamlit as st
from config import AppConfig
from agent import SlackAgent


def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = None


def initialize_agent():
    """Initialize the Azure AI Foundry agent with Slack MCP tools"""
    if st.session_state.agent is not None:
        return st.session_state.agent

    with st.spinner("🔌 Connecting to Azure AI Foundry..."):
        try:
            config = AppConfig.from_env()
            agent_manager = SlackAgent(config)
            agent = agent_manager.initialize()

            st.session_state.agent_manager = agent_manager
            st.session_state.agent = agent

            return agent

        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            return None


def reset_agent():
    """Reset agent and clear session state"""
    if st.session_state.agent_manager:
        st.session_state.agent_manager.cleanup()
    st.session_state.agent = None
    st.session_state.agent_manager = None
    st.session_state.messages = []


def clear_chat_history():
    """Clear chat message history"""
    st.session_state.messages = []
