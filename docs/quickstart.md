# Quickstart

Get AppLens running locally in five minutes.

## Prerequisites

| Requirement | Version |
|---|---|
| Docker Desktop | 4.x or later |
| Docker Compose | v2 (bundled with Docker Desktop) |
| GitHub OAuth App | [create one](#github-oauth-app) |
| OpenAI API key | — |

## 1. Clone and enter the project

```bash
git clone <repo-url> app-lens
cd app-lens
```

## 2. Bootstrap the environment

```bash
./scripts/bootstrap
```

This copies `.env.example` to `.env` and prompts you to fill in the required values before continuing.

### Required values in `.env`

| Key | Where to get it |
|---|---|
| `GITHUB_CLIENT_ID` | GitHub OAuth App settings |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App settings |
| `OPENAI_API_KEY` | platform.openai.com |
| `JWT_SECRET` | any long random string — run `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | choose any password |

## 3. Start services

If you ran `./scripts/bootstrap` it already started the stack. Otherwise:

```bash
./scripts/start
```

Services come up on:

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |

## 4. Run database migrations

After the backend is live, apply the schema:

```bash
./scripts/db-setup
```

## 5. Log in

Open http://localhost:3000, click **Sign in with GitHub**, and authorize the OAuth app.

---

## GitHub OAuth App

Create one at **GitHub → Settings → Developer settings → OAuth Apps → New OAuth App**:

| Field | Value |
|---|---|
| Application name | AppLens (local) |
| Homepage URL | `http://localhost:3000` |
| Authorization callback URL | `http://localhost:8000/auth/github/callback` |

Copy the generated **Client ID** and **Client Secret** into `.env`.

---

## Daily workflow

```bash
./scripts/start          # start services
./scripts/logs           # stream all logs
./scripts/logs backend   # stream backend logs only
./scripts/stop           # stop and remove containers
./scripts/stop --volumes # stop and wipe database
```

---

## Troubleshooting

**Port already in use**
```bash
./scripts/stop
./scripts/start
```

**Migrations fail — backend not ready**  
Wait ~10 s for the backend container to finish starting, then re-run `./scripts/db-setup`.

**OAuth callback mismatch**  
The callback URL registered in GitHub must be `http://localhost:8000/auth/github/callback` — note port **8000**, not 3000.
