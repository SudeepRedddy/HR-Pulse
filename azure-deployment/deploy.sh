#!/bin/bash
# HRPulse Azure Deployment Script (Student Free Tier)

# Configuration
RG_NAME="rg-hrpulse-capstone"
LOCATION="eastus"
APP_PLAN_NAME="plan-hrpulse-free"
WEB_APP_NAME="app-hrpulse"
DB_SERVER_NAME="psql-hrpulse-base"

echo "Deploying HRPulse infrastructure to Azure..."

# 1. Resource Group
az group create --name $RG_NAME --location $LOCATION

# 2. Database (PostgreSQL Flexible Server - Burstable B1ms)
az postgres flexible-server create \
  --location $LOCATION \
  --resource-group $RG_NAME \
  --name $DB_SERVER_NAME \
  --admin-user hrpulseadmin \
  --admin-password 'HRPulseP@ssw0rd!' \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 32 \
  --yes

# 3. App Service Plan (F1 Free)
az appservice plan create \
  --name $APP_PLAN_NAME \
  --resource-group $RG_NAME \
  --sku F1 \
  --is-linux

# 4. Web App
az webapp create \
  --resource-group $RG_NAME \
  --plan $APP_PLAN_NAME \
  --name $WEB_APP_NAME \
  --runtime "PYTHON|3.11"

# 5. Connect App Settings
az webapp config appsettings set \
  --resource-group $RG_NAME \
  --name $WEB_APP_NAME \
  --settings \
  DATABASE_URL="postgresql://hrpulseadmin:HRPulseP@ssw0rd!@$DB_SERVER_NAME.postgres.database.azure.com/postgres" \
  ENVIRONMENT="production"

echo "Complete! Please configure GitHub actions next."
