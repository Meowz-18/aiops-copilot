# Production ADK Agent Server with Firestore and Gemini
import os
import uuid
import json
import re
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

logger.info("Starting ADK Agent Server...")

# Load environment variables
load_dotenv()

# Initialize production agent safely
production_agent = None
try:
    logger.info("Importing production agent...")
    from production_agent.agent import production_agent
    logger.info("Production agent imported successfully.")
except Exception as e:
    logger.error(f"Failed to import production agent: {e}")

# Create standard FastAPI app
# We are bypassing get_fast_api_app to avoid ADK auto-discovery issues
app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Update app metadata
app.title = "AIOps Incident Co-Pilot"
app.description = "AI-powered incident detection and analysis from server logs"
app.version = "2.0.0"

# Initialize Firestore
try:
    logger.info("Initializing Firestore client...")
    db = firestore.Client()
    incidents_collection = db.collection('incidents')
    logger.info("Firestore client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Firestore: {e}")
    db = None
    incidents_collection = None

class Incident(BaseModel):
    incidentId: str
    createdAt: str
    status: str
    severity: str
    service: str
    summary: str
    rootCause: str
    runbookSteps: str
    lastUpdatedAt: str

class AnalysisResponse(BaseModel):
    incidents: List[Incident]

class AnalyzeRequest(BaseModel):
    uploadId: Optional[str] = None
    logText: Optional[str] = None

@app.get("/")
def root():
    return {"status": "running", "service": "production-adk-agent"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "production-adk-agent", "version": "2.0.0"}

@app.post("/api/upload-log")
async def upload_log(file: UploadFile = File(...)):
    """Upload a log file for analysis"""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Empty file")
            
        upload_id = str(uuid.uuid4())
        
        # Store in Firestore
        if db:
            db.collection('uploads').document(upload_id).set({
                'content': text_content,
                'filename': file.filename,
                'uploadedAt': datetime.now().isoformat(),
            })
                
        # Fallback if parsing fails
        fallback_incident = {
            "incidentId": str(uuid.uuid4()),
            "createdAt": datetime.now().isoformat(),
            "status": "open",
            "severity": "medium",
            "service": "web-server",
            "summary": "Log Analysis Completed",
            "rootCause": "Automated analysis performed",
            "runbookSteps": text_response,
            "lastUpdatedAt": datetime.now().isoformat()
        }
        
        # Store in Firestore
        if incidents_collection:
            incidents_collection.document(fallback_incident['incidentId']).set(fallback_incident)
        
        return {"incidents": [fallback_incident]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/incidents")
async def get_incidents(status: Optional[str] = None, severity: Optional[str] = None):
    """Retrieve all incidents from Firestore with optional filters"""
    try:
        if not incidents_collection:
            return {"incidents": []}
            
        query = incidents_collection
        
        # Apply filters
        if status and status != 'all':
            query = query.where('status', '==', status)
        if severity and severity != 'all':
            query = query.where('severity', '==', severity)
        
        # Get all incidents
        docs = query.order_by('createdAt', direction=firestore.Query.DESCENDING).stream()
        
        incidents = []
        for doc in docs:
            incident_data = doc.to_dict()
            incident_data['incidentId'] = doc.id
            incidents.append(incident_data)
        
        return {"incidents": incidents}
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        return {"incidents": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)