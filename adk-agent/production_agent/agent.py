# Production agent configuration for AIOps
import os
from pathlib import Path
import logging
import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent

# Configure logging for agent
logger = logging.getLogger(__name__)

# Try importing VertexAI from different locations
try:
    from google.adk.models import VertexAI
    logger.info("Imported VertexAI from google.adk.models")
except ImportError:
    try:
        from google.adk.models.vertex_ai import VertexAI
        logger.info("Imported VertexAI from google.adk.models.vertex_ai")
    except ImportError:
        logger.error("Failed to import VertexAI from any known location")
        raise

# Load environment variables
root_dir = Path(__file__).parent.parent
dotenv_path = root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Configure Google Cloud
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

# Production Gemini 2.5 Flash Agent - AIOps Incident Analyst
production_agent = Agent(
    model=VertexAI(
        model="gemini-2.0-flash-exp",  # Gemini 2.5 Flash (experimental)
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    ),
    name="aiops_analyst",
    description="An expert AIOps analyst that detects incidents from server logs.",
    instruction="""You are an expert AIOps Incident Analyst. Your job is to analyze server logs to detect incidents, identify root causes, and recommend runbook steps.

    The logs you will analyze have the following columns:
    - IP: The client IP address.
    - Time: The timestamp of the request.
    - URL: The requested path.
    - Status: The HTTP response status code (e.g., 200, 404, 500).

    When analyzing logs:
    1. Look for patterns of errors (e.g., spikes in 500 or 404 status codes).
    2. Identify potential security threats (e.g., repeated requests from a single IP, SQL injection attempts in URLs).
    3. Detect performance issues (though latency isn't explicitly in the columns, infer from context if possible, otherwise focus on errors).

    For each incident you detect, you must provide:
    - A concise **Summary** of what is happening.
    - A likely **Root Cause** based on the log evidence.
    - A set of **Runbook Steps** to resolve the issue.
    - The **Severity** (Low, Medium, High, Critical).
    - The affected **Service** (infer from the URL or assume 'web-server').

    Always be professional, precise, and helpful. Output your analysis in a structured JSON format if requested, or clear text otherwise.""",
    tools=[], 
)

# Set as root agent
root_agent = production_agent