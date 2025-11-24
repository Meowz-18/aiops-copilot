#!/bin/bash
# Deploy script for ADK Agent and Ollama Backend

# Fail on any error
set -e

echo "🚀 Starting deployment process..."

# 1. Deploy Ollama Backend
echo "📦 Deploying Ollama Backend (Gemma 270m GPU)..."
if [ -d "ollama-backend" ]; then
  cd ollama-backend
  gcloud run deploy ollama-gemma3-270m-gpu \
    --source . \
    --region europe-west1 \
    --concurrency 7 \
    --cpu 8 \
    --set-env-vars OLLAMA_NUM_PARALLEL=4 \
    --gpu 1 \
    --gpu-type nvidia-l4 \
    --max-instances 1 \
    --memory 16Gi \
    --allow-unauthenticated \
    --no-cpu-throttling \
    --no-gpu-zonal-redundancy \
    --timeout 600 \
    --labels dev-tutorial=codelab-agent-gpu
  cd ..
else
  echo "❌ Error: ollama-backend directory not found!"
  exit 1
fi

# 2. Get Ollama URL
echo "🔍 Retrieving Ollama Service URL..."
export OLLAMA_URL=$(gcloud run services describe ollama-gemma3-270m-gpu \
    --region=europe-west1 \
    --format='value(status.url)')

echo "🎉 Gemma backend deployed at: $OLLAMA_URL"

# 3. Create .env file for ADK Agent
echo "📝 Creating .env file for ADK Agent..."
PROJECT_ID=$(gcloud config get-value project)

# Ensure adk-agent directory exists
if [ ! -d "adk-agent" ]; then
  echo "❌ Error: adk-agent directory not found!"
  exit 1
fi

cat << EOF > adk-agent/.env
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=europe-west1
GEMMA_MODEL_NAME=gemma3:270m
OLLAMA_API_BASE=$OLLAMA_URL
EOF

echo "✅ Created adk-agent/.env"

# 4. Deploy ADK Agent
echo "🤖 Deploying ADK Agent..."
cd adk-agent
gcloud run deploy production-adk-agent \
   --source . \
   --region europe-west1 \
   --allow-unauthenticated \
   --memory 4Gi \
   --cpu 2 \
   --max-instances 1 \
   --concurrency 50 \
   --timeout 300 \
   --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
   --set-env-vars GOOGLE_CLOUD_LOCATION=europe-west1 \
   --set-env-vars GEMMA_MODEL_NAME=gemma3:270m \
   --set-env-vars OLLAMA_API_BASE=$OLLAMA_URL \
   --labels dev-tutorial=codelab-agent-gpu
cd ..

# 5. Get Agent URL
export AGENT_URL=$(gcloud run services describe production-adk-agent \
    --region=europe-west1 \
    --format='value(status.url)')

echo "🎉 ADK Agent deployed at: $AGENT_URL"
echo "✅ Deployment complete!"
