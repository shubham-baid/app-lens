# Architecture

High-level overview of the AppLens system — how it is structured, how its components communicate, and why the key design decisions were made.

---

## System overview

AppLens is a full-stack monorepo composed of four runtime layers:

```
Browser
  └─ Next.js frontend (port 3000)
       └─ FastAPI backend (port 8000)
            ├─ PostgreSQL + pgvector (port 5432)
            └─ External APIs (GitHub, OpenAI)
```

In production, a Caddy reverse proxy sits in front of both services and handles TLS termination. The browser only ever talks to a single origin.

```
Browser ──► Caddy ──► /api/* ──► FastAPI backend
                  └──► /*    ──► Next.js frontend
```

---

## Repository layout

```
app-lens/
  backend/     FastAPI application, domain model, services, agents
  frontend/    Next.js application, UI components, API client
  docs/        Project documentation
  scripts/     Developer workflow scripts
  infra/       Compose and proxy configuration
```

---

## Backend

Language: **Python 3.12**  
Framework: **FastAPI** with async SQLAlchemy  
Package manager: **Poetry**

### Route groups

| Prefix | Responsibility |
|---|---|
| `/auth` | GitHub OAuth flow, JWT cookie issuance |
| `/repos` | Repository registration and listing |
| `/scan` | Scan job creation and status |
| `/graph` | Service graph reads |
| `/chat` | AI chat sessions (error analysis, what-if, NLQ) |
| `/nlq` | Natural-language architecture queries |

### Service layer

Business logic lives in `backend/app/services/`:

| Module | Responsibility |
|---|---|
| `scan_pipeline` | Orchestrates static analysis across a repository |
| `graph_builder` | Constructs inferred service graph from scan results |
| `code_fetch` | Downloads source files via GitHub API |
| `embeddings` | Generates and stores pgvector embeddings for NLQ |
| `normalize` | Normalises service names across detectors |
| `mcp_client` | MCP GitHub integration for extended API access |

### Detectors

Language-specific static analysers live in `backend/app/services/detectors/`:

| Detector | Covers |
|---|---|
| `http_python` | HTTP calls in Python (requests, httpx, aiohttp) |
| `http_javascript` | HTTP calls in JS/TS (fetch, axios) |
| `http_java` | HTTP calls in Java (RestTemplate, WebClient, OkHttp) |
| `kafka_python` | Kafka producers/consumers in Python |
| `kafka_node` | Kafka producers/consumers in Node.js |
| `kafka_java` | Kafka producers/consumers in Java |

### AI agents

CrewAI agents in `backend/app/agents/`:

| Agent | Task | Entry point |
|---|---|---|
| `orchestrator` | Routes user messages to the right agent | always runs first |
| `error_agent` | Root-cause analysis from error logs | when logs are pasted |
| `whatif_agent` | Blast-radius simulation | when a service/change is targeted |
| `nlq_agent` | Natural-language queries over the graph | when a question is asked |
| `scanner_agent` | Scan coordination | when a repo is submitted |
| `parser_agent` | Output parsing and cleanup | post-agent step |
| `graph_agent` | In-graph reasoning | when graph traversal is needed |

### Database

PostgreSQL 16 with the **pgvector** extension.  
Schema migrations are managed with **Alembic** (in `backend/alembic/`).

Core tables: `repositories`, `services`, `endpoints`, `interactions`, `scans`, `scan_targets`, `log_pastes`, `implications`, `doc_chunks`, `service_graphs`.

---

## Frontend

Language: **TypeScript**  
Framework: **Next.js 14** (App Router)  
Styling: **Tailwind CSS**

### Page routes

| Route | Content |
|---|---|
| `/` | Landing / login page |
| `/dashboard` | Repository management, scan trigger |
| `/graph` | 3-D interactive service graph |

### Key components

| Component | Responsibility |
|---|---|
| `Graph3D` | Interactive 3-D force graph (react-force-graph-3d) |
| `ChatDock` | Fixed sidebar chat for AI interactions |
| `RepoPicker` | Repository selector with scan controls |

### API client

`frontend/lib/api.ts` is the single module that issues all HTTP requests to the backend. All components import from here — no component fetches directly.

Authentication state is managed in `frontend/lib/auth.ts` via the `applens_token` JWT cookie set by the backend.

---

## Authentication flow

```
User → clicks "Sign in with GitHub"
  → frontend redirects to GET /auth/github/login
  → backend redirects to github.com/login/oauth/authorize
  → GitHub redirects to GET /auth/github/callback?code=...
  → backend exchanges code for access token
  → backend issues applens_token JWT cookie
  → browser is redirected to /dashboard
```

The JWT cookie is `HttpOnly` and `SameSite=Lax`. The frontend never reads the token directly; it is forwarded automatically by the browser on every API request.

---

## Infrastructure

### Local (docker-compose.yml)

Three services: `postgres`, `backend`, `frontend`. Ports 5432, 8000, and 3000 are exposed to the host for direct access.

### Production (docker-compose.prod.yml)

Four services: `postgres`, `backend`, `frontend`, `proxy` (Caddy). Only ports 80 and 443 are exposed. Postgres is internal-only.

Caddy configuration (`Caddyfile`):
- Routes `/api/*` to the backend, stripping the `/api` prefix.
- Routes everything else to the frontend.
- Handles TLS automatically via Let's Encrypt when `DOMAIN` is set to a real hostname.

---

## Key design decisions

**Single JWT cookie, no front-end token storage**  
Avoids XSS exposure. The backend is the single source of truth for session validity.

**Static analysis, no runtime agents/sidecars**  
Dependency graphs are inferred from source code, not from live traffic. No changes to production services are required.

**pgvector for NLQ**  
Service and endpoint descriptions are embedded and stored in the same Postgres instance. This keeps the infrastructure simple and avoids a separate vector store.

**Caddy as reverse proxy**  
Automatic TLS with zero configuration in production. Local development skips TLS by using direct port access.
