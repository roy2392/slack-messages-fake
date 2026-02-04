#!/bin/bash
# Script to download and run Slack MCP server locally

set -e

echo "=============================================="
echo "Slack MCP Server Local Setup"
echo "=============================================="

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed!"
    echo ""
    echo "Please install Go first:"
    echo "  brew install go"
    echo ""
    echo "Or download from: https://go.dev/dl/"
    exit 1
fi

echo "✓ Go is installed: $(go version)"

# Create directory for MCP server
MCP_DIR="$HOME/.slack-mcp-server"
mkdir -p $MCP_DIR
cd $MCP_DIR

# Clone or update repository
if [ -d "slack-mcp-server" ]; then
    echo ""
    echo "Slack MCP server directory exists. Updating..."
    cd slack-mcp-server
    git pull
else
    echo ""
    echo "Cloning Slack MCP server..."
    git clone https://github.com/korotovsky/slack-mcp-server.git
    cd slack-mcp-server
fi

# Build the server
echo ""
echo "Building Slack MCP server..."
go build -o slack-mcp-server

echo "✓ Build complete"

# Create run script
cat > run.sh << 'RUNSCRIPT'
#!/bin/bash
# Load environment variables from the project .env file
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Set MCP server configuration
export SLACK_MCP_PORT=13080

# Optional: Enable message posting (disabled by default for safety)
# export SLACK_MCP_ADD_MESSAGE_TOOL=1

# Optional: Enable reactions
# export SLACK_MCP_ADD_REACTION_TOOL=1

# Optional: Set cache locations for better performance
export SLACK_MCP_USERS_CACHE="$HOME/.slack-mcp-server/users-cache.json"
export SLACK_MCP_CHANNELS_CACHE="$HOME/.slack-mcp-server/channels-cache.json"

echo "=============================================="
echo "Starting Slack MCP Server"
echo "=============================================="
echo "Port: $SLACK_MCP_PORT"
echo "Workspace: $SLACK_WORKSPACE"
echo "Bot Token: ${SLACK_BOT_TOKEN:0:20}..."
echo "=============================================="
echo ""
echo "Server will be available at: http://localhost:$SLACK_MCP_PORT"
echo "Press Ctrl+C to stop"
echo ""

# Run the server
./slack-mcp-server
RUNSCRIPT

chmod +x run.sh

echo ""
echo "=============================================="
echo "Setup Complete! ✓"
echo "=============================================="
echo ""
echo "Slack MCP Server installed at:"
echo "  $MCP_DIR/slack-mcp-server"
echo ""
echo "To start the server, run:"
echo "  cd $MCP_DIR/slack-mcp-server"
echo "  PROJECT_DIR=$(pwd) ./run.sh"
echo ""
