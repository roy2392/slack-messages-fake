# Setting Up Slack MCP Server for Azure AI Foundry Agent

This guide walks you through setting up the Slack MCP server to work with your Azure AI Foundry agent.

## Prerequisites

1. Go runtime installed (for running the Slack MCP server)
2. Azure AI Foundry project with agent service enabled
3. Slack workspace with appropriate permissions

## Step 1: Install and Configure Slack MCP Server

### 1.1 Install the Slack MCP Server

```bash
# Clone the Slack MCP server repository
git clone https://github.com/korotovsky/slack-mcp-server.git
cd slack-mcp-server

# Build the server (requires Go)
go build -o slack-mcp-server

# Or download a pre-built binary from releases
```

### 1.2 Configure Slack Authentication

The Slack MCP server supports multiple authentication methods:

**Option A: Bot Token (Recommended for agents)**
```bash
export SLACK_BOT_TOKEN=xoxb-your-bot-token
export SLACK_WORKSPACE=your-workspace-name
```

**Option B: User OAuth Token**
```bash
export SLACK_USER_TOKEN=xoxp-your-user-token
export SLACK_WORKSPACE=your-workspace-name
```

**Option C: Browser Tokens**
```bash
export SLACK_TOKEN_XOXC=xoxc-your-cookie-token
export SLACK_TOKEN_XOXD=xoxd-your-d-token
export SLACK_WORKSPACE=your-workspace-name
```

### 1.3 Configure Cache (Optional but Recommended)

For better performance and context enhancement:

```bash
export SLACK_MCP_USERS_CACHE=/path/to/users-cache.json
export SLACK_MCP_CHANNELS_CACHE=/path/to/channels-cache.json
```

### 1.4 Enable Additional Tools (Optional)

To enable message posting (disabled by default for safety):

```bash
# Enable for all channels
export SLACK_MCP_ADD_MESSAGE_TOOL=1

# Or enable only for specific channels
export SLACK_MCP_ADD_MESSAGE_TOOL="C01234567,C76543210"
```

To enable reactions:

```bash
export SLACK_MCP_ADD_REACTION_TOOL=1
```

## Step 2: Run the Slack MCP Server

### 2.1 Start the Server

```bash
# HTTP mode (recommended for Azure AI Foundry)
export SLACK_MCP_PORT=13080
./slack-mcp-server

# The server will be available at http://localhost:13080
```

### 2.2 Verify the Server is Running

```bash
curl http://localhost:13080/health
```

## Step 3: Deploy MCP Server to Azure (Production)

For production use, deploy the MCP server to Azure so it's publicly accessible:

### Option A: Azure Container Instances

```bash
# Build and push Docker image
docker build -t slack-mcp-server .
docker tag slack-mcp-server myregistry.azurecr.io/slack-mcp-server:latest
docker push myregistry.azurecr.io/slack-mcp-server:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name slack-mcp-server \
  --image myregistry.azurecr.io/slack-mcp-server:latest \
  --dns-name-label slack-mcp-unique \
  --ports 13080 \
  --environment-variables \
    SLACK_BOT_TOKEN=xoxb-your-token \
    SLACK_WORKSPACE=your-workspace \
    SLACK_MCP_PORT=13080
```

### Option B: Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name slack-mcp-plan \
  --resource-group myResourceGroup \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group myResourceGroup \
  --plan slack-mcp-plan \
  --name slack-mcp-server-unique \
  --deployment-container-image-name myregistry.azurecr.io/slack-mcp-server:latest

# Configure environment variables
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name slack-mcp-server-unique \
  --settings \
    SLACK_BOT_TOKEN=xoxb-your-token \
    SLACK_WORKSPACE=your-workspace \
    SLACK_MCP_PORT=13080
```

### Option C: Azure Functions (See azure-function-slack-mcp for template)

Follow the Azure Functions MCP server template for serverless deployment.

## Step 4: Configure Azure AI Foundry Project

### 4.1 Set Up Environment Variables

Create a `.env` file in your project:

```bash
# Azure AI Foundry configuration
FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o

# Slack MCP Server configuration
SLACK_MCP_SERVER_URL=http://localhost:13080  # Or your Azure deployment URL
# Or for Azure deployment:
# SLACK_MCP_SERVER_URL=https://slack-mcp-unique.azurewebsites.net

# Slack authentication (passed to MCP server at runtime)
SLACK_BOT_TOKEN=xoxb-your-bot-token
```

### 4.2 Azure Authentication

Ensure you're authenticated to Azure:

```bash
az login
az account set --subscription your-subscription-id
```

## Step 5: Install Python Dependencies

```bash
pip install azure-ai-projects azure-identity python-dotenv
```

## Step 6: Run the Agent

```bash
python azure_foundry_slack_agent.py
```

## Available Slack MCP Tools

The Slack MCP server provides these tools to the agent:

1. **conversations_history** - Retrieve channel messages
   - Supports pagination by date (1d, 7d, 30d) or message count

2. **conversations_replies** - Get thread messages
   - Uses thread timestamp parameter

3. **conversations_search_messages** - Search messages
   - Filter by channels, users, dates
   - Note: Unavailable with bot tokens

4. **conversations_add_message** - Post messages (if enabled)
   - Can post to channels or threads

5. **channels_list** - List workspace channels
   - Returns public, private, DMs, group DMs

6. **reactions_add** - Add emoji reactions (if enabled)

## Resources Available

The MCP server also provides CSV directory resources:

- `slack://<workspace>/channels` - All channels with metadata
- `slack://<workspace>/users` - All workspace users

## Troubleshooting

### MCP Server Not Accessible

```bash
# Check if server is running
curl http://localhost:13080/health

# Check server logs
./slack-mcp-server  # Look for any errors in output
```

### Authentication Errors

```bash
# Verify your Slack token is valid
curl https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```

### Bot Missing Permissions

Ensure your Slack bot has these scopes:
- `channels:history`
- `channels:read`
- `groups:history`
- `groups:read`
- `im:history`
- `im:read`
- `mpim:history`
- `mpim:read`
- `users:read`
- `search:read` (for message search)
- `chat:write` (if posting messages)
- `reactions:write` (if adding reactions)

### Agent Not Finding Tools

Check that:
1. MCP server URL is correct and accessible
2. Server is running and responding
3. Slack authentication is properly configured
4. No firewall blocking the connection

## Security Considerations

1. **Never commit tokens** - Use `.env` files and `.gitignore`
2. **Use bot tokens** - Preferred over user tokens for agents
3. **Enable tools selectively** - Only enable message posting if needed
4. **Review MCP server logs** - Monitor what data is accessed
5. **Use HTTPS** - Always use HTTPS for production deployments
6. **Rotate tokens regularly** - Update Slack tokens periodically

## Example Questions for Your Agent

Once everything is set up, try asking:

- "What channels are in this workspace?"
- "Show me recent messages from #tech"
- "Find messages about 'deployment' in the last week"
- "Who are the members of this workspace?"
- "What's being discussed in the engineering channels?"

## Additional Resources

- [Slack MCP Server GitHub](https://github.com/korotovsky/slack-mcp-server)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Slack API Documentation](https://api.slack.com/)
