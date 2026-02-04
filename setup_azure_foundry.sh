#!/bin/bash
# Azure AI Foundry Project Setup Script

set -e

echo "=============================================="
echo "Azure AI Foundry Project Setup"
echo "=============================================="

# Check if user is logged in to Azure
echo "Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Not logged in to Azure. Running 'az login'..."
    az login
else
    echo "✓ Already logged in to Azure"
fi

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "Current subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"

# Prompt for resource group details
read -p "Enter resource group name (default: rg-slack-agent): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-rg-slack-agent}

read -p "Enter location (default: eastus): " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Enter AI Foundry project name (default: slack-agent-project): " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-slack-agent-project}

echo ""
echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Project Name: $PROJECT_NAME"
echo ""
read -p "Continue with this configuration? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create resource group
echo ""
echo "Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

echo "✓ Resource group created"

# Create AI Foundry hub (required for projects)
HUB_NAME="${PROJECT_NAME}-hub"
echo ""
echo "Creating AI Foundry hub: $HUB_NAME..."
echo "This may take a few minutes..."

az ml workspace create \
    --kind hub \
    --resource-group $RESOURCE_GROUP \
    --name $HUB_NAME \
    --location $LOCATION

echo "✓ AI Foundry hub created"

# Create AI Foundry project
echo ""
echo "Creating AI Foundry project: $PROJECT_NAME..."

az ml workspace create \
    --kind project \
    --resource-group $RESOURCE_GROUP \
    --name $PROJECT_NAME \
    --hub-id /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.MachineLearningServices/workspaces/$HUB_NAME \
    --location $LOCATION

echo "✓ AI Foundry project created"

# Get project endpoint
PROJECT_ENDPOINT=$(az ml workspace show \
    --name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query discoveryUrl -o tsv | sed 's/\/discovery$//')

echo ""
echo "=============================================="
echo "Setup Complete! ✓"
echo "=============================================="
echo ""
echo "Project Details:"
echo "  Name: $PROJECT_NAME"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Endpoint: $PROJECT_ENDPOINT"
echo ""
echo "Next Steps:"
echo "1. Deploy a model (GPT-4o recommended)"
echo "2. Update your .env file with:"
echo "   FOUNDRY_PROJECT_ENDPOINT=$PROJECT_ENDPOINT"
echo ""
echo "To deploy a model, visit:"
echo "https://ai.azure.com/"
echo ""
