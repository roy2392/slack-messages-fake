# Slack AI Assistant

Azure AI Foundry + Slack MCP integration with Streamlit UI. Query your Slack workspace using natural language through an AI agent.

## Features

- 🤖 **Azure AI Foundry Integration** - GPT-4o powered agent
- 🔧 **MCP Protocol** - Model Context Protocol for Slack
- 💬 **Streamlit UI** - Clean, modern chat interface
- 🐳 **Docker Support** - Containerized deployment
- 📊 **Enhanced Tracing** - Proper Azure AI Foundry trace formatting
- ⚡ **Auto-Approval** - Seamless tool execution

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/roy2392/slack-messages-fake.git
cd slack-messages-fake

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start with Docker Compose
docker-compose up -d

# 4. Open in browser
open http://localhost:8501
```

### Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MCP server
bash scripts/start_mcp_server.sh &

# 3. Run Streamlit app
streamlit run src/app.py
```

## Configuration

Create a `.env` file with your credentials:

```bash
# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
FOUNDRY_API_KEY=your-api-key
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o

# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_WORKSPACE=your-workspace-name

# MCP Server (for local development)
SLACK_MCP_SERVER_URL=http://localhost:13080/mcp
```

## Required Slack Scopes

Add these scopes in your Slack App configuration:

**Bot Token Scopes:**
- `chat:write` - Post messages
- `chat:write.customize` - Customize message appearance
- `users:read` - View users
- `channels:read` - View public channels
- `groups:read` - View private channels
- `im:read` - View DMs
- `mpim:read` - View group DMs
- `channels:history` - Read public channel messages
- `groups:history` - Read private channel messages  
- `im:history` - Read DM messages
- `mpim:history` - Read group DM messages

**After adding scopes, reinstall the app to your workspace!**

## Architecture

```
┌─────────────────┐
│  Streamlit UI   │  :8501
│   (Frontend)    │
└────────┬────────┘
         │ Azure SDK
         ▼
┌─────────────────┐
│ Azure AI Foundry│  Model: gpt-4o
│     Agent       │  Auto-Approval: ON
└────────┬────────┘
         │ MCP/HTTP
         ▼
┌─────────────────┐
│ Slack MCP Server│  :13080/mcp
│   (Container)   │
└────────┬────────┘
         │ Slack API
         ▼
┌─────────────────┐
│ Slack Workspace │
└─────────────────┘
```

## Usage

### Sample Queries

- "What channels are available?"
- "Show recent messages from #tech"
- "What did Alice say about errors?"
- "List all public channels"
- "Search for messages about deployment"

### Features

- **Tool Discovery** - Automatically finds 7 Slack tools
- **Message History** - Read channel conversations
- **Thread Replies** - Access message threads
- **Channel Management** - List and search channels
- **File Access** - Download attachments
- **Reactions** - Add/remove emoji reactions

## Development

### Project Structure

```
├── src/
│   ├── __init__.py            # Package initialization
│   ├── app.py                 # Main Streamlit application
│   ├── config.py              # Configuration management
│   └── agent.py               # Azure AI agent wrapper
├── docker/
│   ├── frontend/
│   │   └── Dockerfile         # Frontend container
│   └── mcp-server/
│       └── Dockerfile         # MCP server container
├── scripts/
│   ├── send_fake_messages.py  # Test data generator
│   └── start_mcp_server.sh    # MCP server launcher
├── data/
│   ├── eval_dataset.json      # Evaluation dataset
│   └── eval_dataset.csv       # Evaluation dataset (CSV)
├── docs/
│   └── INTEGRATION_SUCCESS.md # Integration documentation
├── tests/                     # Test files (empty)
├── docker-compose.yml         # Docker orchestration
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

### Key Files

- **src/app.py** - Main Streamlit application with enhanced trace formatting
- **src/config.py** - Configuration management using dataclasses
- **src/agent.py** - SlackAgent class encapsulating Azure AI Foundry logic
- **docker-compose.yml** - Multi-container orchestration
- **requirements.txt** - All Python dependencies

## Trace Formatting

The app includes enhanced Azure AI Foundry trace formatting:

- **Conversation IDs** - Organized trace sessions
- **Metadata** - Timestamped queries for searchability  
- **Tool Call Tracking** - Visibility into MCP tool execution
- **Response IDs** - Linkable trace references
- **Token Usage** - Cost tracking per query

## Troubleshooting

### MCP Server Connection Issues
```bash
# Check if MCP server is running
docker ps | grep slack-mcp-server

# View MCP server logs
docker logs slack-mcp-server
```

### Missing Scopes
```bash
# Test token scopes
python send_fake_messages.py --test-scopes
```

### Azure Authentication
```bash
# Login to Azure
az login

# Verify credentials
az account show
```

## Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Clean up everything
docker-compose down -v
```

## License

MIT

## Contributing

Pull requests welcome! Please ensure:
1. No secrets in commits
2. Docker builds successfully
3. Code follows existing style
4. Tests pass (if applicable)

## Support

- **Issues**: https://github.com/roy2392/slack-messages-fake/issues
- **Docs**: See `INTEGRATION_SUCCESS.md`

---

Built with Azure AI Foundry + MCP | Containerized with Docker | v1.1.0
