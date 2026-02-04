#!/usr/bin/env python3
"""
Slack AI Assistant - Main Application
Azure AI Foundry + Slack MCP Integration

Clean, modular entry point for the Streamlit application.
"""

import streamlit as st
from dotenv import load_dotenv

from session import initialize_session_state, initialize_agent
from ui import render_sidebar, render_chat_interface

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
initialize_session_state()

# Initialize agent
agent = initialize_agent()

# Render UI components
render_sidebar()
render_chat_interface()
