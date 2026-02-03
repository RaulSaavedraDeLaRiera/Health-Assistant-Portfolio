"""
Health Assistant Portfolio - Main API server.

Mode 1 (this file): Runner + SessionService.
- If REASONING_ENGINE_NAME is set: uses VertexAiSessionService (Vertex AI).
- If not set: uses InMemorySessionService for local demo; no GCP needed.

Endpoints: POST /create-session, POST /run, GET /healthz
Auth: optional; set DISABLE_AUTH=TRUE for demo, by default.
"""

import sys
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime

import os
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any

from google import adk
from google.genai import types

load_dotenv()

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from agents.orchestrator.agent import root_agent
from auth import get_user_from_token

# ----- Config -----
log_file = project_root / "api_server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", "8080"))
REASONING_ENGINE_NAME = os.getenv("REASONING_ENGINE_NAME")

if REASONING_ENGINE_NAME:
    from google.adk.sessions import VertexAiSessionService
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")
    session_service = VertexAiSessionService(PROJECT_ID, LOCATION)
    logger.info(f"Using VertexAiSessionService (REASONING_ENGINE_NAME set)")
else:
    from google.adk.sessions import InMemorySessionService
    session_service = InMemorySessionService()
    logger.info("Using InMemorySessionService; no GCP. Set REASONING_ENGINE_NAME for Vertex.")

runner = adk.Runner(
    agent=root_agent,
    app_name=REASONING_ENGINE_NAME or "health-assistant-portfolio",
    session_service=session_service,
)

# ----- FastAPI -----
app = FastAPI(title="Health Assistant Portfolio API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize_part(part: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    fn_call = getattr(part, "function_call", None)
    if fn_call is not None:
        out["function_call"] = {
            "name": getattr(fn_call, "name", None),
            "args": getattr(fn_call, "args", None),
        }
        return out
    fn_resp = getattr(part, "function_response", None)
    if fn_resp is not None:
        out["function_response"] = {
            "name": getattr(fn_resp, "name", None),
            "response": getattr(fn_resp, "response", None),
        }
        return out
    if hasattr(part, "text") and getattr(part, "text") is not None:
        out["text"] = part.text
        return out
    out["raw"] = repr(part)
    return out


async def _get_user(request: Request) -> Dict[str, Any]:
    auth_header = request.headers.get("Authorization", "")
    return get_user_from_token(auth_header)


@app.post("/create-session")
async def create_session(request: Request, user_info: Dict[str, Any] = Depends(_get_user)):
    """Create a session. Body optional: { "userId": "optional-id" }."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    user_id = body.get("userId") or user_info["uid"]
    try:
        session = await session_service.create_session(
            app_name=REASONING_ENGINE_NAME or "health-assistant-portfolio",
            user_id=user_id,
        )
        return JSONResponse(
            content={"sessionId": session.id, "userId": session.user_id},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}\n{traceback.format_exc()}")
        return JSONResponse(
            content={"detail": str(e)},
            status_code=500,
        )


@app.post("/run")
async def run_message(request: Request, user_info: Dict[str, Any] = Depends(_get_user)):
    """Run orchestrator. Body: { userId?, sessionId, newMessage, streaming?: false }."""
    body = await request.body()
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(content={"detail": "Invalid JSON"}, status_code=400)
    user_id = body_json.get("userId") or body_json.get("user_id") or user_info["uid"]
    session_id = body_json.get("sessionId") or body_json.get("session_id")
    new_message = body_json.get("newMessage") or body_json.get("new_message")
    if not session_id:
        return JSONResponse(
            content={"detail": "Missing sessionId. Call /create-session first."},
            status_code=400,
        )
    if not new_message:
        return JSONResponse(content={"detail": "Missing newMessage"}, status_code=400)
    message_text = new_message.get("parts", [{}])[0].get("text", "") if isinstance(new_message, dict) else ""
    if not message_text and isinstance(new_message, dict):
        message_text = new_message.get("text", "")
    if not message_text:
        return JSONResponse(content={"detail": "Invalid newMessage format"}, status_code=400)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])
    try:
        events = runner.run(user_id=user_id, session_id=session_id, new_message=content)
        events_list = []
        for event in events:
            if hasattr(event, "content") and event.content:
                events_list.append({
                    "content": {
                        "parts": [_serialize_part(p) for p in (event.content.parts or [])],
                        "role": getattr(event.content, "role", "model"),
                    }
                })
        return JSONResponse(content=events_list, status_code=200)
    except Exception as e:
        logger.error(f"Error running agent: {e}\n{traceback.format_exc()}")
        return JSONResponse(content={"detail": str(e)}, status_code=500)


@app.get("/healthz")
async def healthz():
    return JSONResponse(
        content={"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"},
        status_code=200,
    )


@app.get("/health")
async def health():
    return JSONResponse(
        content={"status": "ok", "port": PORT},
        status_code=200,
    )


if __name__ == "__main__":
    print("Health Assistant Portfolio - API Server")
    print(f"  Log file: {log_file}")
    print(f"  Endpoints: POST /create-session, POST /run, GET /healthz")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
