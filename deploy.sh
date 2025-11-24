#!/bin/bash
# Updated Deploy script for AIOps Dashboard with Gemini + Firestore
# This deploys: ADK Agent (with Gemini) + Dashboard (React UI)

# Fail on any error
set -e

echo "🚀 Starting deployment process..."
echo "================================"

# Get project info
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

echo "📋 Project: $PROJECT_ID"
echo "📍 Region: $REGION"
echo ""

# 1. Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$PROJECT_ID

echo "✅ APIs enabled"
echo ""

# 2. Initialize Firestore (if not already done)
echo "🔥 Setting up Firestore..."
# This command is idempotent - won't fail if Firestore is already initialized
gcloud firestore databases create --location=$REGION --type=firestore-native 2>/dev/null || echo "Firestore already initialized"
echo "✅ Firestore ready"
echo ""

# 3. Deploy ADK Agent with Gemini
echo "🤖 Deploying ADK Agent (with Gemini 1.5 Flash)..."
if [ -d "adk-agent" ]; then
  cd adk-agent
  
  gcloud run deploy aiops-agent \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --max-instances 5 \
    --concurrency 50 \
    --timeout 300 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --set-env-vars GOOGLE_CLOUD_LOCATION=$REGION \
    --labels app=aiops,component=agent
    
  cd ..
  echo "✅ ADK Agent deployed"
else
  echo "❌ Error: adk-agent directory not found!"
  exit 1
fi
echo ""

# 4. Get Agent URL
echo "🔍 Retrieving Agent Service URL..."
AGENT_URL=$(gcloud run services describe aiops-agent \
    --region=$REGION \
    --format='value(status.url)')

echo "✅ Agent URL: $AGENT_URL"
echo ""

# 5. Deploy Dashboard
echo "🎨 Deploying AIOps Dashboard..."
if [ -d "aiops-dashboard" ]; then
  cd aiops-dashboard
  
  gcloud run deploy aiops-dashboard \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 60 \
    --set-env-vars API_URL=$AGENT_URL \
    --labels app=aiops,component=dashboard
    
  cd ..
  echo "✅ Dashboard deployed"
else
  echo "❌ Error: aiops-dashboard directory not found!"
  exit 1
fi
echo ""

# 6. Get Dashboard URL
echo "🔍 Retrieving Dashboard URL..."
DASHBOARD_URL=$(gcloud run services describe aiops-dashboard \
    --region=$REGION \
    --format='value(status.url)')

echo ""
echo "================================"
echo "✅ Deployment complete!"
echo "================================"
echo ""
echo "🎯 Your AIOps Dashboard is live at:"
echo "   $DASHBOARD_URL"
echo ""
echo "🤖 Agent API endpoint:"
echo "   $AGENT_URL"
echo ""
echo "📊 Firestore Database:"
echo "   https://console.cloud.google.com/firestore/databases/-default-/data/panel?project=$PROJECT_ID"
echo ""
echo "💡 Next steps:"
echo "   1. Open the dashboard URL in your browser"
echo "   2. Upload a log file or paste log text"
echo "   3. View AI-detected incidents in real-time"
echo ""
