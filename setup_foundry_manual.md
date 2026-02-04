# Manual Azure AI Foundry Setup Guide

If the automated script doesn't work, follow these manual steps to set up Azure AI Foundry.

## Prerequisites

- Azure subscription with appropriate permissions
- Azure CLI installed and configured

## Step 1: Login to Azure

```bash
az login
az account set --subscription "your-subscription-name-or-id"
```

## Step 2: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="rg-slack-agent"
LOCATION="eastus"
PROJECT_NAME="slack-agent-project"

# Create resource group
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION
```

## Step 3: Create AI Foundry Resources via Portal

### Option A: Using Azure Portal (Recommended for First Time)

1. **Go to Azure AI Foundry Portal**
   - Visit: https://ai.azure.com/
   - Sign in with your Azure credentials

2. **Create a New Project**
   - Click **"+ New project"**
   - Enter project details:
     - **Project name**: `slack-agent-project`
     - **Hub**: Create new or select existing
     - **Subscription**: Select your subscription
     - **Resource group**: Select `rg-slack-agent`
     - **Location**: Select your preferred region (e.g., East US)
   - Click **"Create"**

3. **Wait for Deployment**
   - This creates:
     - AI Hub resource
     - AI Project resource
     - Azure OpenAI service (if needed)
     - Storage account
     - Key Vault
     - Application Insights

4. **Get Project Endpoint**
   - Once created, go to your project
   - Click **"Overview"** in left menu
   - Under **"Project details"**, copy the **Project endpoint**
   - Format: `https://your-hub.services.ai.azure.com/api/projects/your-project`

### Option B: Using Azure CLI (Advanced)

If you prefer CLI, use the extension:

```bash
# Install Azure ML CLI extension
az extension add --name ml

# Create hub
HUB_NAME="slack-agent-hub"
az ml workspace create \
    --kind hub \
    --resource-group $RESOURCE_GROUP \
    --name $HUB_NAME \
    --location $LOCATION

# Create project
az ml workspace create \
    --kind project \
    --resource-group $RESOURCE_GROUP \
    --name $PROJECT_NAME \
    --hub-id /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.MachineLearningServices/workspaces/$HUB_NAME \
    --location $LOCATION

# Get project endpoint
az ml workspace show \
    --name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query discoveryUrl -o tsv
```

## Step 4: Deploy a Model

### Via Azure AI Foundry Portal

1. **Navigate to Your Project**
   - Go to https://ai.azure.com/
   - Open your project: `slack-agent-project`

2. **Deploy a Model**
   - In the left menu, click **"Deployments"** or **"Models + endpoints"**
   - Click **"+ Deploy model"** → **"Deploy base model"**
   - Select **"GPT-4o"** (recommended) or **"GPT-4"**
   - Click **"Confirm"**

3. **Configure Deployment**
   - **Deployment name**: `gpt-4o` (remember this!)
   - **Model version**: Select latest
   - **Deployment type**: Standard
   - Click **"Deploy"**

4. **Wait for Deployment**
   - This takes 2-5 minutes
   - Status will change from "Creating" to "Succeeded"

5. **Note the Deployment Name**
   - You'll need this for `FOUNDRY_MODEL_DEPLOYMENT_NAME` in .env
   - Example: `gpt-4o`

### Via Azure CLI

```bash
# List available models
az ml model list \
    --workspace-name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP

# Deploy GPT-4o (requires Azure OpenAI access)
az ml online-deployment create \
    --name gpt-4o \
    --model azureml://registries/azureml/models/gpt-4o/versions/latest \
    --workspace-name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP
```

## Step 5: Enable Agent Service

1. **In Azure AI Foundry Portal**
   - Go to your project
   - Click **"Settings"** in left menu
   - Under **"Features"**, enable **"Agent Service"**
   - Click **"Save"**

2. **Verify Agent Service**
   - Go to **"Agent"** in the left menu
   - You should see the Agent playground
   - If not available, wait a few minutes and refresh

## Step 6: Configure Permissions

### Assign Yourself Azure AI User Role

```bash
# Get your user object ID
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

# Get workspace ID
WORKSPACE_ID=$(az ml workspace show \
    --name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query id -o tsv)

# Assign Azure AI User role
az role assignment create \
    --role "Azure AI Developer" \
    --assignee $USER_OBJECT_ID \
    --scope $WORKSPACE_ID
```

## Step 7: Get Configuration Values

### Project Endpoint

```bash
az ml workspace show \
    --name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query discoveryUrl -o tsv | sed 's/\/discovery$//'
```

### Model Deployment Name

In the portal:
1. Go to your project
2. Click **"Deployments"** or **"Models + endpoints"**
3. Copy the deployment name (e.g., `gpt-4o`)

## Step 8: Update .env File

Update your `.env` file with the values:

```bash
# Azure AI Foundry Configuration
FOUNDRY_PROJECT_ENDPOINT=https://your-hub.services.ai.azure.com/api/projects/your-project
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o

# Slack MCP Server Configuration
SLACK_MCP_SERVER_URL=http://localhost:13080

# Slack Authentication
SLACK_BOT_TOKEN=xoxb-YOUR-BOT-TOKEN-HERE
SLACK_WORKSPACE=your-workspace-name
```

## Verification

Test your setup:

```bash
# Verify Azure login
az account show

# Verify project exists
az ml workspace show \
    --name $PROJECT_NAME \
    --resource-group $RESOURCE_GROUP

# Test API access
az account get-access-token --resource https://ai.azure.com
```

## Troubleshooting

### "Workspace not found"

```bash
# List all workspaces
az ml workspace list --resource-group $RESOURCE_GROUP -o table
```

### "Model deployment failed"

1. Check Azure OpenAI quota in your subscription
2. Try a different region
3. Request quota increase if needed

### "Permission denied"

```bash
# Check your role assignments
az role assignment list \
    --assignee $(az ad signed-in-user show --query id -o tsv) \
    --all -o table
```

### "Agent Service not available"

1. Verify you're using a supported region (East US, West Europe, etc.)
2. Check that Agent Service is enabled in project settings
3. Wait 5-10 minutes after enabling

## Next Steps

Once setup is complete:
1. ✅ Azure AI Foundry project created
2. ✅ Model deployed
3. ✅ Configuration values obtained
4. → Proceed to set up Slack MCP server locally

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [Agent Service Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart)
- [Model Deployment Guide](https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/deploy-models)
