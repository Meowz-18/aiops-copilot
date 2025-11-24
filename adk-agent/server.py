# Production ADK Agent Server with Firestore and Gemini
import os
import uuid
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from production_agent.agent import production_agent
from google.cloud import firestore

# Load environment variables
load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app_args = {"agents_dir": AGENT_DIR, "web": True}

# Create FastAPI app with ADK integration
app: FastAPI = get_fast_api_app(**app_args)

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
db = firestore.Client()
incidents_collection = db.collection('incidents')

# Pydantic Models
class AnalyzeRequest(BaseModel):
    uploadId: Optional[str] = None
    logText: Optional[str] = None

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
        db.collection('uploads').document(upload_id).set({
            'content': text_content,
            'filename': file.filename,
            'uploadedAt': datetime.now().isoformat(),
        })
        
        return {"uploadId": upload_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_logs(request: AnalyzeRequest):
    """Analyze logs from either uploaded file or direct text input"""
    try:
        # Get log content from either uploadId or direct text
        if request.logText:
            log_content = request.logText
        elif request.uploadId:
            doc = db.collection('uploads').document(request.uploadId).get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Log file not found")
            log_content = doc.to_dict()['content']
        else:
            raise HTTPException(status_code=400, detail="Either uploadId or logText must be provided")
        
        # Take a sample of the logs to avoid context window limits
        lines = log_content.splitlines()
        
        # Check if it's CSV format (has headers)
        if len(lines) > 0 and ',' in lines[0]:
            header = lines[0]
            sample_lines = lines[1:51] if len(lines) > 1 else []
            sample_text = "\n".join([header] + sample_lines)
        else:
            # Plain text logs - take first 50 lines
            sample_text = "\n".join(lines[:50])
        
        prompt = f"""Analyze the following server log sample and identify any incidents.
        
        LOG DATA:
        {sample_text}
        
        Return the response as a JSON object with a key 'incidents' containing a list of incidents.
        Each incident should have: incidentId, createdAt, status, severity, service, summary, rootCause, runbookSteps, lastUpdatedAt.
        Severity must be one of: low, medium, high, critical
        Status must be: open
        If no incidents found, return an empty incidents array.
        """
       
        # Call the Gemini agent
        response = production_agent.model.prompt(prompt)
        text_response = response.text if hasattr(response, 'text') else str(response)
        
        # Parse JSON from response
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
                
                # Store incidents in Firestore
                if data.get('incidents'):
                    for incident in data['incidents']:
                        incident_id = incident.get('incidentId', str(uuid.uuid4()))
                        incidents_collection.document(incident_id).set({
                            **incident,
                            'createdAt': incident.get('createdAt', datetime.now().isoformat()),
                            'lastUpdatedAt': datetime.now().isoformat(),
                        })
                
                return data
            except json.JSONDecodeError:
                pass
                
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
        incidents_collection.document(fallback_incident['incidentId']).set(fallback_incident)
        
        return {"incidents": [fallback_incident]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/incidents")
async def get_incidents(status: Optional[str] = None, severity: Optional[str] = None):
    """Retrieve all incidents from Firestore with optional filters"""
    try:
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
        print(f"Error fetching incidents: {e}")
        return {"incidents": []}

@app.patch("/api/incidents/{incident_id}")
async def update_incident(incident_id: str, status: str):
    """Update incident status"""
    try:
        incidents_collection.document(incident_id).update({
            'status': status,
            'lastUpdatedAt': datetime.now().isoformat()
        })
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")