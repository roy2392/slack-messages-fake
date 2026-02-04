#!/bin/bash
# Start Slack MCP Server locally

# Load environment variables
source .env

# Set MCP server configuration - use the correct variable names
export SLACK_MCP_PORT=13080
export SLACK_MCP_XOXB_TOKEN=$SLACK_BOT_TOKEN  # Bot token
export SLACK_MCP_WORKSPACE=${SLACK_WORKSPACE:-"your-workspace"}

# Optional: Enable caching for better performance (requires users:read scope)
# export SLACK_MCP_USERS_CACHE="$HOME/.slack-mcp-server/users-cache.json"
# export SLACK_MCP_CHANNELS_CACHE="$HOME/.slack-mcp-server/channels-cache.json"

# Optional: Enable message posting (disabled by default for safety)
# export SLACK_MCP_ADD_MESSAGE_TOOL=1

# Optional: Enable reactions
# export SLACK_MCP_ADD_REACTION_TOOL=1

echo "=============================================="
echo "Starting Slack MCP Server"
echo "=============================================="
echo "Port: $SLACK_MCP_PORT"
echo "Workspace: $SLACK_WORKSPACE"
echo "Bot Token: ${SLACK_BOT_TOKEN:0:20}..."
echo "Cache Users: $SLACK_MCP_USERS_CACHE"
echo "Cache Channels: $SLACK_MCP_CHANNELS_CACHE"
echo "=============================================="
echo ""
echo "Server will be available at: http://localhost:$SLACK_MCP_PORT/mcp"
echo "Press Ctrl+C to stop"
echo ""

# Run the server in HTTP mode (for Azure AI Foundry compatibility)
~/.slack-mcp-server/slack-mcp-server/build/slack-mcp-server --transport http
