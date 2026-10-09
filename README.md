# NexCord

**A voice-first, human-in-the-loop incident commander for live events.**

NexCord helps event teams respond to operational problems such as room conflicts, equipment failures, unavailable staff, and overcrowding. It gathers operational context, evaluates possible responses, simulates candidate plans, asks a human for approval, executes approved actions through tools, and verifies the result.

> **Project status:** The local Docker Compose stack and core approval-to-execution workflow are working. AWS deployment and observability are the current next phase; AWS services listed in the roadmap below should not be considered deployed until explicitly configured and tested.

## Contents

- [Why NexCord?](#why-nexcord)
- [Core workflow](#core-workflow)
- [Architecture](#architecture)
- [Technology stack](#technology-stack)
- [Example scenario](#example-scenario)
- [Run locally](#run-locally)
- [Useful Docker commands](#useful-docker-commands)
- [Data and persistence](#data-and-persistence)
- [Security notes](#security-notes)
- [Roadmap](#roadmap)

## Why NexCord?

Live events involve tightly connected resources: rooms, people, vendors, equipment, and schedules. A single incident can cause multiple downstream problems. NexCord is designed to help an operator make a decision with operational context instead of blindly running an autonomous action.

The guiding principle is **propose → simulate → approve → execute → verify**. A plan is not executed simply because an agent generated it: a human approval step is part of the workflow.

## Core workflow

1. **Observe** — collect event and operational state.
2. **Detect and assess** — identify an incident and estimate its risk or impact.
3. **Retrieve context** — use stored operational information and knowledge to ground the response.
4. **Generate candidate plans** — propose possible actions for the incident.
5. **Simulate** — evaluate candidate plans against available resources and constraints.
6. **Select a plan** — choose from successfully simulated plans using the current risk, delay, and cost ranking.
7. **Request human approval** — pause before taking operational action.
8. **Execute through MCP** — invoke the approved action through the MCP server.
9. **Verify and recover** — check the resulting state and handle failures or recovery paths where supported.
10. **Audit** — persist plans, executions, and operational history for inspection.

## Architecture

```text
┌─────────────────────────────┐
│      Next.js Frontend       │
│ Incident / Plan / Approval  │
└──────────────┬──────────────┘
               │ HTTP API
┌──────────────▼──────────────┐
│        FastAPI Backend      │
│ API · Agent orchestration   │
│ Simulation · Verification   │
└───────┬────────┬────────────┘
        │        │
        │        ├────────────────────┐
        ▼        ▼                    ▼
┌────────────┐ ┌────────────┐  ┌─────────────┐
│ PostgreSQL │ │ MCP Server │  │ ML Service  │
│ + pgvector │ │ Tool calls │  │ Risk / CV   │
└────────────┘ └────────────┘  └─────────────┘
        │
        ▼
 Durable data, knowledge,
 audit history and checkpoints
```

The local system runs with Docker Compose. The frontend calls the backend through the host URL; the backend, MCP server, ML service, and database communicate over the Docker network.

## Technology stack

| Area | Technology | Purpose |
|---|---|---|
| Frontend | Next.js, React, TypeScript | Operator interface for incidents, plans, simulation results, and approval |
| API | Python, FastAPI, Uvicorn | REST API and application services |
| Agent | LangGraph | Stateful incident-response workflow and approval/resume flow |
| Checkpointing | LangGraph PostgreSQL checkpointer | Durable agent state across backend restarts |
| Database | PostgreSQL | Events, incidents, resources, plans, executions, and audit records |
| Vector search | pgvector | Store and retrieve knowledge embeddings |
| ORM / migrations | SQLAlchemy, Alembic | Database access and schema migrations |
| Tool integration | Model Context Protocol (MCP), Streamable HTTP | Route approved operations through the MCP server |
| ML / computer vision | Python; Faster R-CNN ResNet-50 FPN v2 | Risk analysis and people/occupancy-related visual analysis |
| Local deployment | Docker, Docker Compose | Reproducible multi-service development setup |
| Planned cloud services | Amazon RDS for PostgreSQL, S3, Bedrock, CloudWatch | Managed database, object storage, model access, logging, and metrics |

**LLM configuration note:** The current local Compose configuration passes `GEMINI_API_KEY`. Amazon Bedrock is part of the AWS deployment phase and should be treated as a planned integration until it has been configured and verified in the deployed environment.

## Example scenario

Imagine a robotics final with 120 expected attendees in a room with a capacity of 60. During the event, NexCord may need to account for crowding, a projector failure, a room conflict, or an unavailable judge.

For an equipment incident, the workflow can generate a candidate action such as allocating a backup projector. It simulates the proposed resource change, waits for the operator's approval, executes through MCP, then checks whether the equipment assignment changed as expected.

The exact response depends on the live database state, constraints, and available tools; example incidents and plans are illustrative rather than guarantees of a particular result.

## Run locally

### Prerequisites

- Git
- Docker Engine or Docker Desktop with the Docker Compose plugin
- A valid `.env` file for the configuration required by your checkout

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd NexCord
```

Replace `<YOUR_REPOSITORY_URL>` with the repository URL.

### 2. Configure environment variables

If the repository contains `.env.example`, copy it and edit the new file:

```bash
cp .env.example .env
```

At minimum, configure the values required by your current `docker-compose.yml`. The hardened local setup uses a database password and can include an LLM API key. For example:

```dotenv
POSTGRES_PASSWORD=replace_with_a_strong_local_password
GEMINI_API_KEY=replace_with_your_key_if_needed
```

Use the exact variable names referenced by your Compose file and application settings. Do not commit `.env` or real API keys to Git.

### 3. Build and start the services

```bash
docker compose up --build -d
```

Inspect the services:

```bash
docker compose ps
```

The backend container applies Alembic migrations before starting FastAPI.

### 4. Verify the API

```bash
curl -i http://127.0.0.1:8000/health
```

A healthy API returns HTTP `200 OK` with a response similar to:

```json
{"status":"ok","service":"nexcord-api"}
```

Open the frontend at <http://127.0.0.1:3000>.

### Local service addresses

| Service | Local address | Notes |
|---|---|---|
| Frontend | <http://127.0.0.1:3000> | Operator UI |
| Backend API | <http://127.0.0.1:8000> | FastAPI service |
| Health check | <http://127.0.0.1:8000/health> | API health endpoint |
| MCP server | `127.0.0.1:8001` | Streamable HTTP MCP endpoint is `/mcp`; a bare browser/curl request may return a session-related error because MCP expects the protocol handshake |
| ML service | `127.0.0.1:8100` | Internal prediction/vision service, also published locally in development |
| PostgreSQL | `127.0.0.1:5432` | Local development database |

The current Compose setup binds published ports to `127.0.0.1`. Keep that restriction for local development; do not expose the development database or unauthenticated service ports directly to the public internet.

## Useful Docker commands

```bash
# Follow all service logs
docker compose logs -f

# Follow backend logs
docker compose logs -f backend

# Restart after a configuration change
docker compose up -d --build

# Stop the services (keeps the named database volume)
docker compose down

# Show running services and health status
docker compose ps
```

> **Data-loss warning:** `docker compose down -v` removes Compose-managed volumes and can delete the local PostgreSQL data. Use it only when you intentionally want to reset local state and have a backup.

## Data and persistence

The PostgreSQL schema covers the event operations domain, including:

- Events, venues, rooms, people, teams, vendors, and equipment
- Reservations and event-to-resource assignments
- Incidents, plans, plan actions, executions, and notifications
- Audit logs and operational observations
- Knowledge documents and chunks for retrieval-augmented workflows
- LangGraph checkpoint tables for persistent agent state

The local database uses a named Docker volume, so ordinary container recreation should not delete its data. Before database migrations, major changes, or moving to another database host, create and verify a backup.

A local SQL backup can be created with:

```bash
mkdir -p backups
docker compose exec -T postgres \
  pg_dump -U nexcord -d nexcord --no-owner --no-privileges \
  > backups/nexcord.sql
```

Confirm the database name and user in your Compose configuration before using this command. Treat database backups as sensitive data and keep them out of public repositories.

## Security notes

NexCord is designed around explicit operator approval for operational actions, but a local development setup is not automatically production-secure.

- Keep `.env`, API keys, database credentials, and database backups out of version control.
- Use strong, unique credentials for cloud resources; do not reuse the local database password in production.
- Keep PostgreSQL private and allow inbound access only from the application resources that need it.
- Use TLS/HTTPS and authentication before exposing the application publicly.
- Apply least-privilege IAM policies and managed secret storage for AWS deployment.
- Preserve audit records and test execution failures, partial actions, and recovery behavior.
- Do not treat model output as authorization. Tool execution should remain constrained by application checks and approval state.

