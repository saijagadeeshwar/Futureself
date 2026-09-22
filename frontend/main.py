"""FastAPI proxy for FutureSelf AI.

Supports both:
1. Local execution via ADK Runner (for local testing & debugging with Memory Bank).
2. Deployed execution over A2A protocol (when AGENT_ENGINE_RESOURCE_NAME is set).
"""

import os
import sys
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add parent directory to path to import app.agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PROJECT_ID = "qwiklabs-gcp-01-bb263000f5c6"
LOCATION_ID = "us-east1"
MEMORY_BANK_ID = "5526525872225386496"

# Ensure Vertex AI environment variables are configured
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ["GOOGLE_CLOUD_PROJECT"] = os.environ.get("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION", LOCATION_ID)

RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE_NAME", "")
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")

local_session_service = None
local_memory_service = None
local_runner = None
local_sessions: dict[str, str] = {}

if not RESOURCE:
    from google.adk.sessions import InMemorySessionService
    from google.adk.memory import VertexAiMemoryBankService
    from google.adk.runners import Runner
    from app.agent import root_agent

    local_session_service = InMemorySessionService()
    local_memory_service = VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION_ID,
        agent_engine_id=MEMORY_BANK_ID,
    )
    local_runner = Runner(
        agent=root_agent,
        app_name="app",
        session_service=local_session_service,
        memory_service=local_memory_service,
    )

if RESOURCE:
    LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]
    A2A_BASE = (
        f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
        f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
    )
    A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"
else:
    LOCATION = LOCATION_ID
    A2A_BASE = ""
    A2A_CARD_URL = ""

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI(title="FutureSelf AI Companion")


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}
_card = None


def _extract_parts(parts: list) -> list[dict]:
    out: list[dict] = []
    from a2a.types import TextPart
    for p in parts:
        root = getattr(p, "root", p)
        if isinstance(root, TextPart) and getattr(root, "text", None):
            out.append({"kind": "text", "text": root.text})
        elif getattr(root, "data", None) is not None:
            meta = getattr(root, "metadata", None) or {}
            mime = meta.get("mimeType") if isinstance(meta, dict) else None
            if mime == "application/json+a2ui":
                out.append({"kind": "a2ui", "data": root.data})
            else:
                s = str(root.data)
                out.append({"kind": "text", "text": s[:1000]})
    return out


async def _run_local_agent(user_id: str, message: str) -> list[dict]:
    """Runs the FutureSelf agent locally using ADK Runner and Memory Bank."""
    if user_id not in local_sessions:
        sess = await local_session_service.create_session(app_name="app", user_id=user_id)
        local_sessions[user_id] = sess.id
    session_id = local_sessions[user_id]

    user_msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part.from_text(text=message)],
    )

    events = []
    async for event in local_runner.run_async(
        user_id=user_id,
        session_id=session_id,
        user_message=user_msg,
    ):
        events.append(event)

    parts: list[dict] = []
    for ev in events:
        if hasattr(ev, "content") and ev.content and hasattr(ev.content, "parts"):
            for p in ev.content.parts:
                if hasattr(p, "text") and p.text:
                    parts.append({"kind": "text", "text": p.text})

    if not parts:
        parts = [{"kind": "text", "text": "I'm processing your roadmap and life goals!"}]

    return parts


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"

    if not RESOURCE:
        parts = await _run_local_agent(user_id, message)
        return JSONResponse({"parts": parts})

    from a2a.client import ClientConfig, ClientFactory
    from a2a.types import (
        AgentCard,
        Message,
        Part,
        Role,
        TaskArtifactUpdateEvent,
        TextPart,
        TransportProtocol,
    )

    parts: list[dict] = []
    got_artifact_update = False
    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        global _card
        if _card is None:
            resp = await client.get(A2A_CARD_URL)
            resp.raise_for_status()
            card = AgentCard(**resp.json())
            card.url = A2A_BASE
            _card = card

        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(_card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=_contexts.get(user_id),
        )

        last_task = None
        async for event in a2a_client.send_message(msg):
            if not isinstance(event, tuple):
                continue
            task, update = event
            if task is not None:
                last_task = task
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id
            if isinstance(update, TaskArtifactUpdateEvent):
                got_artifact_update = True
                parts.extend(_extract_parts(update.artifact.parts))

        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                parts.extend(_extract_parts(artifact.parts))

    if not parts:
        parts = [{"kind": "text", "text": "FutureSelf AI processed your request."}]
    return JSONResponse({"parts": parts})


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
