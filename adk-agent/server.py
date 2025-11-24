# TODO: Complete this file
import os
import uuid
import csv
import io
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from production_agent.agent import production_agent

# Load environment variables
load_dotenv()

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app_args = {"agents_dir": AGENT_DIR, "web": True}

# Create FastAPI app with ADK integration
# We wrap the ADK app to add our custom endpoints
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
app.version = "1.0.0"

# In-memory storage for uploaded logs (for prototype only)
UPLOADED_LOGS: Dict[str, str] = {}

class AnalyzeRequest(BaseModel):
    uploadId: str

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
    return {"status": "healthy", "service": "production-adk-agent"}

@app.post("/api/upload-log")
async def upload_log(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # Simple validation - check if it looks like CSV
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Empty file")
            
        upload_id = str(uuid.uuid4())
        UPLOADED_LOGS[upload_id] = text_content
        
        return {"uploadId": upload_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_logs(request: AnalyzeRequest):
    upload_id = request.uploadId
    if upload_id not in UPLOADED_LOGS:
        raise HTTPException(status_code=404, detail="Log file not found")
        
    log_content = UPLOADED_LOGS[upload_id]
    
    # Take a sample of the logs to avoid context window limits
    # The dataset has IP, Time, URL, Status
    # We'll take the first 50 lines + header
    lines = log_content.splitlines()
    header = lines[0]
    sample_lines = lines[1:51] if len(lines) > 1 else []
    sample_text = "\n".join([header] + sample_lines)
    
    prompt = f"""Analyze the following server log sample and identify any incidents.
    
    LOG DATA:
    {sample_text}
    
    Return the response as a JSON object with a key 'incidents' containing a list of incidents.
    Each incident should have: incidentId, createdAt, status, severity, service, summary, rootCause, runbookSteps, lastUpdatedAt.
    """
    
    try:
        # Call the agent
        # Note: In a real ADK setup, we might use a specific method to invoke the agent programmatically
        # Here we simulate the agent invocation or use the model directly if exposed
        # For this lab, we'll use the agent's model directly to get the JSON
        
        response = production_agent.model.prompt(prompt)
        
        # The response might be a string, we need to parse it or ensure it's JSON
        # For this prototype, we'll assume the model follows instructions well or we'd add a parser
        # If the model returns markdown code blocks, strip them
        
        import json
        import re
        from datetime import datetime
        
        text_response = response.text if hasattr(response, 'text') else str(response)
        
        # Clean up markdown
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
                return data
            except:
                pass
                
        # Fallback if parsing fails or model didn't return JSON
        # Return a generic incident based on the text
        return {
            "incidents": [
                {
                    "incidentId": str(uuid.uuid4()),
                    "createdAt": datetime.now().isoformat(),
                    "status": "open",
                    "severity": "medium",
                    "service": "web-server",
                    "summary": "Automated Analysis Result",
                    "rootCause": "See analysis details.",
                    "runbookSteps": text_response, # Put the full text here
                    "lastUpdatedAt": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")