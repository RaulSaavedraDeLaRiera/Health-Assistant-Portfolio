"""
Mode 2: ADK as server.

This script starts a FastAPI proxy that launches Google ADK built-in api_server
as a subprocess: adk api_server agents. Sessions use in-memory storage by default;
they do not persist across restarts.

Use Mode 1, api_server.py, for:
- Vertex AI persistent sessions: set REASONING_ENGINE_NAME
- Or local in-memory sessions: no env needed

Use Mode 2, this file, for:
- Testing with ADK native server as backend
- Same API: POST /create-session, POST /run, GET /health
"""

import asyncio
import json
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

import os

PORT = int(os.getenv("PORT", "8080"))
ADK_INTERNAL_PORT = int(os.getenv("ADK_INTERNAL_PORT", "9000"))
ADK_APP_NAME = os.getenv("ADK_APP_NAME", "orchestrator")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("api-adk-client")

adk_client: Optional[httpx.AsyncClient] = None


def start_adk_server():
    project_root = BASE_DIR
    commands_to_try = [
        ["adk", "api_server", "agents", "--port", str(ADK_INTERNAL_PORT), "--host", "0.0.0.0"],
        ["adk", "serve", "agents", "--port", str(ADK_INTERNAL_PORT), "--host", "0.0.0.0"],
        ["python", "-m", "google.adk.cli", "api_server", "agents", "--port", str(ADK_INTERNAL_PORT), "--host", "0.0.0.0"],
    ]

    def run():
        for cmd in commands_to_try:
            try:
                logger.info(f"Starting ADK with: {' '.join(cmd)}")
                subprocess.run(cmd, cwd=project_root, check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                logger.warning(f"Command failed: {e}")
                continue
        logger.error("Could not start ADK server")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


async def wait_for_adk_ready(max_attempts: int = 30):
    url = f"http://127.0.0.1:{ADK_INTERNAL_PORT}/docs"
    for attempt in range(max_attempts):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(url)
            if resp.status_code < 400:
                logger.info("ADK server ready")
                return True
        except Exception:
            if attempt % 5 == 0:
                logger.info(f"Waiting for ADK... attempt {attempt + 1}/{max_attempts}")
            await asyncio.sleep(1)
    logger.error("ADK server did not become ready")
    return False


app = FastAPI(title="Health Assistant Portfolio - ADK Client", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def on_startup():
    global adk_client
    logger.info("Starting ADK server subprocess...")
    start_adk_server()
    await wait_for_adk_ready()
    adk_client = httpx.AsyncClient(
        base_url=f"http://127.0.0.1:{ADK_INTERNAL_PORT}",
        timeout=300.0,
    )
    logger.info("ADK client initialized")


@app.on_event("shutdown")
async def on_shutdown():
    global adk_client
    if adk_client is not None:
        await adk_client.aclose()
        adk_client = None


@app.post("/create-session")
async def create_session(request: Request):
    if adk_client is None:
        return JSONResponse(content={"detail": "ADK client not initialized"}, status_code=500)
    try:
        body = await request.json() if await request.body() else {}
    except Exception:
        body = {}
    app_name = body.get("appName") or body.get("app_name") or ADK_APP_NAME
    user_id = body.get("userId") or body.get("user_id") or f"user-{int(time.time() * 1000)}"
    url = f"/apps/{app_name}/users/{user_id}/sessions"
    resp = await adk_client.post(url, json={})
    if resp.status_code >= 400:
        return JSONResponse(content={"detail": resp.text}, status_code=502)
    data = resp.json()
    session_id = data.get("id") or data.get("sessionId")
    if not session_id:
        return JSONResponse(content={"detail": "Invalid session response"}, status_code=502)
    return JSONResponse(content={"sessionId": session_id, "userId": user_id}, status_code=200)


@app.post("/run")
async def run_message(request: Request):
    if adk_client is None:
        return JSONResponse(content={"detail": "ADK client not initialized"}, status_code=500)
    try:
        body_json = await request.json()
    except Exception:
        return JSONResponse(content={"detail": "Invalid JSON"}, status_code=400)
    app_name = body_json.get("appName") or body_json.get("app_name") or ADK_APP_NAME
    user_id = body_json.get("userId") or body_json.get("user_id")
    session_id = body_json.get("sessionId") or body_json.get("session_id")
    new_message = body_json.get("newMessage") or body_json.get("new_message")
    if not user_id or not session_id:
        return JSONResponse(content={"detail": "Missing userId or sessionId"}, status_code=400)
    if not new_message:
        return JSONResponse(content={"detail": "Missing newMessage"}, status_code=400)
    payload = {
        "appName": app_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": new_message,
        "streaming": body_json.get("streaming", False),
    }
    resp = await adk_client.post("/run", json=payload)
    if resp.status_code >= 400:
        return JSONResponse(content={"detail": resp.text}, status_code=502)
    return JSONResponse(content=resp.json(), status_code=200)


@app.get("/health")
@app.get("/healthz")
async def health():
    if adk_client is None:
        return JSONResponse(content={"status": "degraded", "adk": "not_initialized"})
    try:
        r = await adk_client.get("/docs")
        ok = r.status_code < 400
    except Exception:
        ok = False
    return JSONResponse(content={"status": "ok" if ok else "degraded", "adk": "ok" if ok else "unreachable"})


if __name__ == "__main__":
    logger.info(f"Starting Health Assistant Portfolio - ADK Client on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
