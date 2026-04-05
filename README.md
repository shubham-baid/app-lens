# AppLens

Intelligent microservice dependency mapping and incident analysis.

AppLens helps engineering teams understand service-to-service relationships, visualize architecture, and investigate failures with graph-aware AI assistance.

## Core Capabilities

- GitHub OAuth authentication
- Repository discovery and scan orchestration
- Multi-repository dependency graph extraction
- Interactive service graph visualization
- AI-assisted error analysis
- AI-assisted what-if impact analysis
- Natural-language architecture queries

## Architecture

AppLens is organized as a full-stack monorepo:

- Backend API for authentication, scanning, graph construction, and analysis routes
- Frontend web app for login, repository selection, graph exploration, and chat workflows
- Documentation, scripts, and infrastructure assets for local development and deployment

## Repository Layout

```text
AppLens/
  backend/   FastAPI application, domain model, services, and tests
  frontend/  Next.js application, UI components, and client integrations
  docs/      Project and architecture documentation
  scripts/   Developer workflow scripts
  infra/     Local and deployment infrastructure assets
```

## Technology Direction

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: Next.js + TypeScript
- Integrations: GitHub APIs and LLM-powered analysis flows

## Development

Project setup and runtime commands are added under the following directories as the platform evolves:

- `docs/` for setup and operational guidance
- `scripts/` for local workflow commands
- `infra/` for compose and deployment assets

## Mission

Enable teams to answer three operational questions quickly and confidently:

1. What depends on this service?
2. What is the likely blast radius of this failure or change?
3. What should we do next to reduce risk?
