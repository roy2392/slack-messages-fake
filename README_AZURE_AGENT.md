# Azure AI Foundry Slack Agent with MCP

An intelligent agent powered by Azure AI Foundry that can answer questions about your Slack workspace using the Model Context Protocol (MCP) to connect to Slack.

## Overview

This project demonstrates how to build an AI agent that can:
- Query Slack channels and messages
- Search for specific information in Slack
- Analyze conversations and threads
- List users and channels
- Provide intelligent insights about your Slack workspace

## Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Azure AI Foundry Agent │
│    (GPT-4o)             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   MCP Protocol          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Slack MCP Server       │
│  (Go service)           │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Slack API             │
│  (Your Workspace)       │
└─────────────────────────┘
```

## Features

- **Natural Language Queries**: Ask questions in plain English about your Slack workspace
- **Real-Time Data**: Fetches live data from Slack via MCP
- **Streaming Responses**: Get responses as they're generated for better UX
- **Interactive Mode**: Chat with the agent in a conversational interface
- **Demo Mode**: Run predefined queries to showcase capabilities
- **Secure**: Uses Azure credentials and Slack tokens for authentication

## Prerequisites

1. **Azure AI Foundry Project**
   - Active Azure subscription
   - Azure AI Foundry project with agent service enabled
   - Model deployment (GPT-4o or similar)

2. **Slack Workspace**
   - Slack workspace where you're an admin or have appropriate permissions
   - Slack bot token with necessary scopes

3. **Slack MCP Server**
   - Go runtime (to run the MCP server)
   - Or access to a deployed instance

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-azure-agent.txt
```

### 2. Set Up Slack MCP Server

See `setup_slack_mcp_server.md` for detailed instructions.

Quick start:
```bash
# Clone and build Slack MCP server
git clone https://github.com/korotovsky/slack-mcp-server.git
cd slack-mcp-server
go build

# Run the server
export SLACK_BOT_TOKEN=xoxb-your-token
export SLACK_WORKSPACE=your-workspace
./slack-mcp-server
```

### 3. Configure Environment Variables

Copy `.env.azure` to `.env` and fill in your values:

```bash
cp .env.azure .env
# Edit .env with your actual credentials
```

Required variables:
- `FOUNDRY_PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `FOUNDRY_MODEL_DEPLOYMENT_NAME`: Your model deployment name (e.g., gpt-4o)
- `SLACK_MCP_SERVER_URL`: URL where Slack MCP server is running
- `SLACK_BOT_TOKEN`: Your Slack bot token

### 4. Authenticate with Azure

```bash
az login
az account set --subscription your-subscription-id
```

### 5. Run the Agent

```bash
python azure_foundry_slack_agent.py
```

Choose between:
- **Interactive mode**: Ask your own questions
- **Demo mode**: See predefined examples

## Usage Examples

### Interactive Mode

```
🤔 Your question: What channels are available in the workspace?

Response:
There are 5 channels in the workspace:
- #general (Public, 12 members)
- #tech (Public, 8 members)
- #random (Public, 15 members)
- #announcements (Public, 20 members)
- #dev-private (Private, 5 members)
```

```
🤔 Your question: Find messages about deployment in #tech

Response:
I found 3 recent messages about deployment in #tech:

1. Alice (2 hours ago): "The deployment to production went smoothly!"
2. Bob (4 hours ago): "Starting the deployment process now..."
3. Charlie (5 hours ago): "Are we ready for the deployment this afternoon?"
```

### Demo Mode

Runs predefined queries:
1. List all channels
2. Show recent messages from #tech
3. List workspace users
4. Search for specific topics
5. Analyze conversation threads

## Project Structure

```
slack-messages-fake/
├── azure_foundry_slack_agent.py    # Main agent implementation
├── setup_slack_mcp_server.md       # MCP server setup guide
├── requirements-azure-agent.txt     # Python dependencies
├── .env.azure                       # Environment template
└── README_AZURE_AGENT.md           # This file
```

## Agent Capabilities

The agent can answer questions about:

1. **Channels**
   - List all channels
   - Get channel information
   - Find specific channels

2. **Messages**
   - Search messages
   - Get conversation history
   - Analyze thread discussions
   - Find messages by date/user/topic

3. **Users**
   - List workspace members
   - Find user information
   - Analyze user activity

4. **Analysis**
   - Summarize discussions
   - Identify trends
   - Extract action items
   - Find relevant information

## Configuration Options

### Agent Instructions

Modify the `instructions` parameter in `create_slack_agent()` to customize agent behavior:

```python
instructions="""You are a Slack assistant that...
[Add your custom instructions here]
"""
```

### MCP Tool Configuration

Configure which Slack MCP tools to use:

```python
slack_mcp_tool = MCPTool(
    server_label="slack",
    server_url=os.environ["SLACK_MCP_SERVER_URL"],
    # Add custom configuration
)
```

### Slack Authentication

Pass Slack tokens securely at runtime:

```python
extra_body["tool_resources"] = {
    "slack": {
        "headers": {
            "Authorization": f"Bearer {slack_token}"
        }
    }
}
```

## Advanced Usage

### Custom Queries

```python
from azure_foundry_slack_agent import create_slack_agent, query_slack

# Create agent
project_client, agent, openai_client = create_slack_agent()

# Custom query
response = query_slack(
    openai_client,
    agent.name,
    "Find all messages from Alice about the Q2 roadmap"
)
```

### Streaming Responses

```python
from azure_foundry_slack_agent import query_slack_streaming

response = query_slack_streaming(
    openai_client,
    agent.name,
    "Summarize today's discussions in #engineering"
)
```

## Deployment

### Deploy MCP Server to Azure

For production, deploy the Slack MCP server to Azure:

#### Option 1: Azure Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name slack-mcp-server \
  --image myregistry.azurecr.io/slack-mcp-server:latest \
  --dns-name-label slack-mcp \
  --ports 13080
```

#### Option 2: Azure App Service
```bash
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name slack-mcp-server \
  --deployment-container-image-name myregistry.azurecr.io/slack-mcp-server:latest
```

See `setup_slack_mcp_server.md` for detailed deployment instructions.

## Troubleshooting

### Agent Can't Connect to MCP Server

1. Verify MCP server is running:
   ```bash
   curl http://localhost:13080/health
   ```

2. Check firewall/network settings
3. Verify `SLACK_MCP_SERVER_URL` in `.env`

### Authentication Errors

1. Verify Azure credentials:
   ```bash
   az account show
   ```

2. Check Slack token validity:
   ```bash
   curl https://slack.com/api/auth.test \
     -H "Authorization: Bearer $SLACK_BOT_TOKEN"
   ```

### Missing Slack Permissions

Ensure your Slack bot has these scopes:
- `channels:history`
- `channels:read`
- `groups:history`
- `groups:read`
- `users:read`
- `search:read`

## Security Best Practices

1. **Never commit credentials**
   - Use `.env` files
   - Add `.env` to `.gitignore`

2. **Use principle of least privilege**
   - Only grant necessary Slack scopes
   - Use bot tokens instead of user tokens

3. **Rotate credentials regularly**
   - Update Slack tokens periodically
   - Monitor token usage

4. **Use HTTPS in production**
   - Deploy MCP server with HTTPS
   - Use secure endpoints

5. **Audit access**
   - Review MCP server logs
   - Monitor agent queries

## Contributing

To add new capabilities:

1. Update agent instructions in `create_slack_agent()`
2. Add new MCP tools if needed
3. Test with demo queries
4. Update documentation

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Slack MCP Server](https://github.com/korotovsky/slack-mcp-server)
- [Slack API Documentation](https://api.slack.com/)

## License

MIT License - see LICENSE file for details

## Support

For issues:
1. Check `setup_slack_mcp_server.md` for setup problems
2. Review troubleshooting section
3. Open an issue on GitHub
