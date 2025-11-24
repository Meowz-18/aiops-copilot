# TODO: Complete this file
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import google.auth

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

# TODO: Complete this file
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import google.auth

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

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1")

# Configure model connection
gemma_model_name = os.getenv("GEMMA_MODEL_NAME", "gemma3:270m")
api_base = os.getenv("OLLAMA_API_BASE", "localhost:10010")  # Location of Ollama server

# Production Gemma Agent - AIOps Incident Analyst
production_agent = Agent(
    model=LiteLlm(model=f"ollama_chat/{gemma_model_name}", api_base=api_base),
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