# AIOps Incident Co-Pilot

An AI-powered incident detection and analysis system for server logs, built with Google Cloud ADK and React.

## 🏗️ Architecture

This project consists of three main components:

1. **Ollama Backend** - GPU-accelerated Gemma 270m model for log analysis
2. **ADK Agent** - Python backend with FastAPI for incident detection
3. **AIOps Dashboard** - React TypeScript frontend for visualization

## 📁 Project Structure

```
accelerate-ai-lab3-starter/
├── ollama-backend/          # Ollama + Gemma model deployment
│   └── Dockerfile
├── adk-agent/               # ADK Agent backend
│   ├── production_agent/
│   │   ├── __init__.py
│   │   └── agent.py        # AI agent configuration
│   ├── server.py           # FastAPI server
│   ├── Dockerfile
│   └── pyproject.toml
├── aiops-dashboard/         # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Dashboard & Login pages
│   │   ├── services/       # API client
│   │   └── types.ts        # TypeScript interfaces
│   └── package.json
├── deploy.sh               # Deployment automation script
└── generate_sample_logs.py # Sample log generator
```

## 🚀 Quick Start

### Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and configured
- Python 3.13+
- Node.js 18+

### Local Development

#### 1. Generate Sample Logs

```bash
pip install faker
python generate_sample_logs.py
```

This creates `sample-server-logs.log` with 10,000 synthetic Apache-format log entries.

#### 2. Run the Dashboard Locally

```bash
cd aiops-dashboard
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### Cloud Deployment

#### Option 1: Automated Deployment (Recommended)

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Deploy the Ollama backend with GPU support
2. Deploy the ADK agent
3. Configure environment variables automatically
4. Output the service URLs

#### Option 2: Manual Deployment

**Deploy Ollama Backend:**

```bash
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
  --timeout 600
```

**Deploy ADK Agent:**

```bash
cd adk-agent
export OLLAMA_URL=$(gcloud run services describe ollama-gemma3-270m-gpu \
    --region=europe-west1 \
    --format='value(status.url)')

gcloud run deploy production-adk-agent \
   --source . \
   --region europe-west1 \
   --allow-unauthenticated \
   --memory 4Gi \
   --cpu 2 \
   --max-instances 1 \
   --concurrency 50 \
   --timeout 300 \
   --set-env-vars GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) \
   --set-env-vars GOOGLE_CLOUD_LOCATION=europe-west1 \
   --set-env-vars GEMMA_MODEL_NAME=gemma3:270m \
   --set-env-vars OLLAMA_API_BASE=$OLLAMA_URL
```

## 📊 Dataset

The project uses the [Server Logs dataset](https://www.kaggle.com/datasets/vishnu0399/server-logs) from Kaggle, which contains synthetic Apache server logs with the following columns:

- **IP**: Client IP address
- **Time**: Request timestamp
- **URL**: Requested endpoint
- **Status**: HTTP response status code (200, 404, 500, etc.)

The AI agent analyzes these logs to detect:
- Error spikes (500, 404 status codes)
- Security threats (SQL injection, repeated failed requests)
- Performance anomalies

## 🎯 Features

### Backend (ADK Agent)
- ✅ Log file upload via REST API
- ✅ AI-powered incident detection using Gemma 270m
- ✅ Automatic root cause analysis
- ✅ Runbook generation for incident resolution
- ✅ GPU-accelerated inference

### Frontend (Dashboard)
- ✅ Drag-and-drop log file upload
- ✅ Real-time incident visualization
- ✅ Filtering by severity and status
- ✅ Search functionality
- ✅ Detailed incident drawer with:
  - Summary
  - Root cause analysis
  - Recommended runbook steps
- ✅ Responsive design (desktop, tablet, mobile)

## 🔧 API Endpoints

### POST `/api/upload-log`
Upload a log file for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (log file)

**Response:**
```json
{
  "uploadId": "uuid-string"
}
```

### POST `/api/analyze`
Trigger analysis on uploaded logs.

**Request:**
```json
{
  "uploadId": "uuid-string"
}
```

**Response:**
```json
{
  "incidents": [
    {
      "incidentId": "uuid",
      "createdAt": "2025-11-24T12:00:00Z",
      "status": "open",
      "severity": "critical",
      "service": "web-server",
      "summary": "High rate of 500 errors detected",
      "rootCause": "Database connection pool exhausted",
      "runbookSteps": "1. Check DB connections...",
      "lastUpdatedAt": "2025-11-24T12:05:00Z"
    }
  ]
}
```

### GET `/api/incidents`
Retrieve all detected incidents.

**Query Parameters:**
- `status` (optional): Filter by status (open/resolved)
- `severity` (optional): Filter by severity (low/medium/high/critical)

## 🛠️ Tech Stack

### Backend
- **Python 3.13**
- **FastAPI** - Web framework
- **Google ADK** - Agent Development Kit
- **LiteLLM** - Model integration
- **Ollama** - Model serving
- **Gemma 3 270m** - Language model

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Infrastructure
- **Google Cloud Run** - Serverless deployment
- **NVIDIA L4 GPU** - Model acceleration
- **Docker** - Containerization

## 📝 Development Notes

### Building the Dashboard

```bash
cd aiops-dashboard
npm run build
```

### Linting

```bash
npm run lint
```

## 🤝 Contributing

This project was developed as part of the Google Cloud Accelerate AI hackathon.

## 📄 License

MIT License

## 🔗 Links

- [Google ADK Documentation](https://cloud.google.com/agent-development-kit)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Kaggle Server Logs Dataset](https://www.kaggle.com/datasets/vishnu0399/server-logs)
