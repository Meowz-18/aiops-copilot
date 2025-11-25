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
        
        return {"uploadId": upload_id}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_logs(request: AnalyzeRequest):
    """Analyze logs from either uploaded file or direct text input"""
    try:
        # Get log content from either uploadId or direct text
        if request.logText:
            log_content = request.logText
        elif request.uploadId:
            if not db:
                 raise HTTPException(status_code=503, detail="Database unavailable")
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
        text_response = "AI Agent unavailable. Performing heuristic analysis."
        if production_agent:
            try:
                response = production_agent.model.prompt(prompt)
                text_response = response.text if hasattr(response, 'text') else str(response)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")
                text_response = f"AI Analysis failed: {str(e)}"
        else:
             logger.warning("Production agent not initialized. Using fallback/mock response.")

        # Parse JSON from response
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
                
                # Store incidents in Firestore
                if data.get('incidents') and incidents_collection:
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
                
        # Fallback if parsing fails or agent is missing
        fallback_incident = {
            "incidentId": str(uuid.uuid4()),
            "createdAt": datetime.now().isoformat(),
            "status": "open",
            "severity": "medium",
            "service": "web-server",
            "summary": "Log Analysis (Fallback)",
            "rootCause": "AI Agent unavailable or failed to parse response. Check server logs.",
            "runbookSteps": "1. Verify backend logs.\n2. Check AI agent initialization.\n3. Ensure Cloud Run configuration is correct.",
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