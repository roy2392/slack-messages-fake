# Streamlit UI for Azure AI Foundry Slack Agent

## Quick Start

The Streamlit app is already running at:
- **Local URL**: http://localhost:8501
- **Network URL**: http://10.134.8.31:8501
- **External URL**: http://167.220.205.159:8501

Just open any of these URLs in your browser!

## Features

### 💬 Chat Interface
- Simple, clean chat UI
- Real-time conversation with the Azure AI Foundry agent
- Message history maintained during session

### 🔧 Tool Discovery
- Agent automatically discovers and lists available Slack MCP tools
- Shows when tools are being enumerated

### ⚠️ Approval Notifications
- Clear notifications when the agent wants to use Slack tools
- Explains the approval requirement (safety feature)

### ⚙️ Configuration Sidebar
- Shows agent status and connection info
- Displays MCP server URL
- Sample queries to get started
- Clear chat and reset agent buttons

## Usage

### 1. Open the App
Navigate to: http://localhost:8501

### 2. Wait for Connection
The app will automatically:
- Connect to Azure AI Foundry
- Initialize the Slack MCP agent
- Show "Agent Connected" status

### 3. Start Chatting!
Try these sample queries:
- "What tools do you have available?"
- "List all channels in the workspace"
- "Show me recent messages from #tech"
- "What can you do with Slack?"

### 4. Understanding Responses

**Text Responses:**
- The agent will provide helpful text explanations
- Descriptions of available tools and capabilities

**Tool Discovery:**
- Blue info box showing "🔧 Discovered X Slack tools"
- Happens when agent enumerates available MCP tools

**Approval Requests:**
- Yellow warning box with "⚠️ Tool Approval Required"
- Explains that Azure requires manual approval for tool execution
- This is a safety feature to prevent unauthorized API calls

## Managing the App

### Stop the App
```bash
# Find the Streamlit process
ps aux | grep streamlit

# Stop it
pkill -f streamlit
```

### Restart the App
```bash
streamlit run streamlit_app.py
```

### Clear Chat
Click the "🗑️ Clear Chat" button in the sidebar

### Reset Agent
Click the "🔄 Reset Agent" button to create a fresh agent instance

## Architecture

```
┌─────────────────┐
│  Your Browser   │
│  (localhost:    │
│      8501)      │
└────────┬────────┘
         │ HTTP
         │
┌────────▼────────┐
│   Streamlit     │
│      App        │
└────────┬────────┘
         │ Azure SDK
         │
┌────────▼────────┐
│ Azure AI        │
│  Foundry        │
└────────┬────────┘
         │ HTTPS/MCP
         │
┌────────▼────────┐
│  Slack MCP      │
│    Server       │
└────────┬────────┘
         │ Slack API
         │
    ┌────▼────┐
    │  Slack  │
    └─────────┘
```

## Technical Details

### Session State
The app maintains:
- `messages`: Chat history
- `agent`: Azure AI agent instance
- `project_client`: Azure AI Projects client
- `openai_client`: OpenAI-compatible client

### Agent Configuration
- **Name**: SlackStreamlitAgent
- **Model**: gpt-4o (from .env)
- **Tools**: Slack MCP tools
- **Instructions**: Helpful Slack workspace assistant

### MCP Server
- **URL**: From SLACK_MCP_SERVER_URL in .env
- **Mode**: HTTP
- **Tools**: 7 Slack tools available

## Troubleshooting

### "Failed to initialize agent"
- Check that .env file has correct Azure credentials
- Verify MCP server is running: `ps aux | grep slack-mcp-server`
- Ensure ngrok tunnel is active: `curl http://localhost:4040/api/tunnels`

### "Tool Approval Required" messages
- This is expected behavior
- Azure AI Foundry requires manual approval for MCP tool calls
- The agent understands your request but cannot execute without approval
- Future: Implement approval workflow for automatic execution

### Connection errors
- Verify all services are running:
  - MCP Server: `bash start_mcp_server.sh`
  - ngrok: `ngrok http 13080`
  - Streamlit: Should auto-start when you run the app

## Files

- `streamlit_app.py` - Main Streamlit application
- `requirements_streamlit.txt` - Streamlit dependencies
- `.env` - Configuration (credentials, URLs)

## Next Steps

1. **Implement Approval Workflow**
   - Add approval UI in Streamlit
   - Auto-approve trusted tools
   - Log all tool executions

2. **Enhanced UI**
   - Show tool call details
   - Display Slack message formatting
   - Add file/attachment support

3. **Production Deployment**
   - Deploy Streamlit to cloud
   - Remove ngrok dependency
   - Add authentication

Enjoy chatting with your Slack workspace! 🚀
