# Diet & Meal Assistant - Portfolio

A complete assistant portfolio project demonstrating multi-agent architecture for a diet and meal assistant. This project uses the Google Agent Development Kit (ADK) with an orchestrator and specialized backend agents, configurable limits, and two run modes. All data is mock; no Firebase or BigQuery are configured.

## Problem Statement

The system acts as a diet and meal assistant: users ask for recommendations, stats, or diet summaries. An orchestrator delegates to backend agents (recommender, stats, content verifier). The design supports optional wiring to Firebase Auth and Firestore/BigQuery for persistence and real user data; for this portfolio, only mock tools and in-memory sessions are used so the project runs without credentials.

## Architecture Overview

**Orchestrator (entry point)**  
- Single entry for user messages.  
- Does not access user data or backend tools directly; delegates via agent tools.  
- Uses: `healthy_recommender_agent`, `health_stats_agent`, `content_verifier_agent`, and `get_current_date`.

**Backend agents**  
- **healthy_recommender_agent:** Meal and diet recommendations (mock data).  
- **health_stats_agent:** User stats such as meals, water, steps, sleep (mock data).  
- **content_verifier_agent:** Checks draft responses for inappropriate content; does not generate user-facing text.

**Run modes**  
- **Mode 1** (`api_server.py`): Runner + SessionService. Optional Vertex AI for persistent sessions; otherwise in-memory.  
- **Mode 2** (`api_server_adk_client.py`): ADK built-in api_server as subprocess; proxy forwards `/create-session` and `/run`. Sessions in-memory only.

## Key Features

- **Multi-agent:** Orchestrator plus three specialized agents with clear separation of concerns.  
- **Configurable limits:** Per-tool defaults and caps via env (recommendations count, period days, breakdown size).  
- **Content safety:** Optional verification of draft responses before surfacing to the user.  
- **Two run modes:** Runner + SessionService or ADK as server; same API surface.  
- **Mock-only data:** No Firebase, BigQuery, or Firestore; runs without GCP credentials.  
- **i18n:** Default English; Spanish via `LANGUAGE=ES` and `agents/prompts/translations/ES/`.

## Technology Stack

| Area | Technology |
|------|-------------|
| Agents | Google ADK (Agent Development Kit), Gemini |
| API | FastAPI |
| Sessions | In-memory or Vertex AI (Mode 1, optional) |
| Auth | Stub; optional. Dev user when `DISABLE_AUTH=TRUE`. |
| Data | Mock tools only; no Firebase/BigQuery in this repo |

## Project Structure

```
.
├── agents/
│   ├── orchestrator/              # Entry; delegates to recommender, stats, verifier
│   ├── healthy_recommender_agent/ # Meal/diet recommendations
│   ├── health_stats_agent/        # User stats: meals, water, steps, sleep
│   ├── content_verifier_agent/    # Content safety check
│   └── prompts/                   # English default; translations/ES/
├── tools/
│   ├── agent_tools.py             # Orchestrator agent tools
│   ├── limit_cap.py               # Configurable limits per tool
│   ├── mock_health_tools.py       # Recommendations, stats, diet summary, verify_content_safety
│   ├── date_tools.py
│   ├── logged_tool.py
│   └── logged_agent_tool.py
├── src/
│   └── prompt_loader.py
├── auth/
│   └── auth_stub.py               # Optional auth; dev user when DISABLE_AUTH=TRUE
├── api_server.py                 # Mode 1: Runner + SessionService
├── api_server_adk_client.py      # Mode 2: ADK as server
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud Project and Vertex AI (only if using persistent sessions in Mode 1)

### Setup

```bash
cd health-assistant-portfolio
pip install -r requirements.txt
```

Optional: copy `.env.example` to `.env` and set `PORT`, `LANGUAGE`, `DISABLE_AUTH`, or Vertex-related variables.

### Run

**Mode 1 (recommended)**  
```bash
python api_server.py
```

**Mode 2**  
```bash
python api_server_adk_client.py
```

Endpoints: `POST /create-session`, `POST /run`, `GET /healthz` (and `GET /health` in Mode 2).

### Quick test

```bash
curl -X POST http://localhost:8080/create-session -H "Content-Type: application/json" -d "{}"
curl -X POST http://localhost:8080/run -H "Content-Type: application/json" -d '{
  "userId": "portfolio-dev",
  "sessionId": "<sessionId from create-session>",
  "newMessage": { "parts": [{ "text": "What should I eat for breakfast?" }] }
}'
```

## Environment (optional)

| Variable | Description | Default |
|----------|-------------|--------|
| `PORT` | Server port | `8080` |
| `LANGUAGE` | Prompt language: `EN` or `ES` | `EN` |
| `DISABLE_AUTH` | If `TRUE`, no auth; use dev user | `TRUE` |
| `REASONING_ENGINE_NAME` | Vertex Reasoning Engine (Mode 1) | none, in-memory |
| `GOOGLE_CLOUD_PROJECT` | GCP project (only if using Vertex) | - |
| `GOOGLE_CLOUD_LOCATION` | GCP region (only if using Vertex) | `europe-west1` |
| `ADK_INTERNAL_PORT` | Internal ADK server port (Mode 2) | `9000` |
| `ADK_APP_NAME` | App name for ADK (Mode 2) | `orchestrator` |

**Configurable limits (tools)**  
`RECOMMENDATIONS_DEFAULT_ITEMS`, `RECOMMENDATIONS_TOOL_LIMIT`, `HEALTH_STATS_DEFAULT_DAYS`, `HEALTH_STATS_MAX_DAYS`, `DIET_SUMMARY_DEFAULT_DAYS`, `DIET_SUMMARY_MAX_DAYS`, `DIET_SUMMARY_BREAKDOWN_MAX_DAYS`. See `.env.example` or code for defaults.

## Data and backends

This project uses **mock data only** so it runs without credentials. The architecture is prepared so that real backends can be wired later: auth abstraction and parameterized tools keep the same interface. As examples only, options include Google (Firebase, Firestore, BigQuery), AWS (Cognito, DynamoDB, RDS), or Microsoft (Azure AD, Cosmos DB). None are configured in this repo; the demo uses in-memory sessions and mock tool responses.

## License

This is a portfolio project. Provided for educational and portfolio purposes only.
