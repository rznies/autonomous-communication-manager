# Operations Guide

## Production Baseline

This project now supports a basic production split between local development and deployed environments.

### Runtime configuration

Set configuration through environment variables only.

| Variable | Purpose | Default |
|---|---|---|
| `ACM_ENV` | Runtime mode: `development`, `staging`, `production` | `development` |
| `ACM_DB_PATH` | SQLite database path | temp dir in dev, `./data/acm_api_state.db` in staging/prod |
| `ACM_CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:5173` |
| `ACM_MUTATION_API_KEY` | Required for state-changing API routes when set | unset |
| `ACM_HAS_WRITE_SCOPE` | Enables live write actions when true | `false` |
| `ACM_ENABLE_DOCS` | Enables `/docs` and `/openapi.json` | true in dev, false in prod |
| `ACM_RELEASE_VERSION` | Human-readable release version | `0.1.0` |
| `ACM_BUILD_SHA` | Build or git SHA surfaced in readiness | unset |

Copy `.env.example` to `.env` for local development. Do not commit `.env`.

## Auth model

The app is still prototype-grade, so the auth model is intentionally narrow and explicit.

### Current model

- `GET` routes are read-only and intended for internal dashboards or trusted networks.
- Mutating routes must be protected with `X-ACM-API-Key` when `ACM_MUTATION_API_KEY` is set.
- Live side effects stay disabled unless `ACM_HAS_WRITE_SCOPE=true`.

### Recommended deployment model

1. Put the API behind your platform auth layer or private network.
2. Require `X-ACM-API-Key` for mutating routes.
3. Keep `ACM_HAS_WRITE_SCOPE=false` until Gmail and Slack write flows are end-to-end verified.
4. Add user-level OAuth only when a real operator dashboard exists.

## Health checks

Use these endpoints in deploy orchestration.

- `GET /health/live` checks that the process is up.
- `GET /health/ready` checks that SQLite is reachable and returns deploy metadata.

Recommended checks:

```bash
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
```

Treat readiness as the gate for rollout completion.

## Deployment checklist

1. `uv sync`
2. `uv run pytest`
3. `cd frontend && npm install && npm run lint && npm run build`
4. Set `ACM_ENV=production`
5. Set `ACM_CORS_ORIGINS` to the real frontend origin
6. Set `ACM_MUTATION_API_KEY` to a secret value stored in the deploy platform
7. Keep `ACM_ENABLE_DOCS=false`
8. Verify `/health/live` and `/health/ready`

## Rollback path

This app does not have database migrations yet, so rollback is simple.

1. Re-deploy the previous application image or commit.
2. Keep the same `ACM_DB_PATH` and secrets.
3. Re-run `/health/ready`.
4. If the new release wrote bad state, restore the SQLite file from the last backup snapshot.

Recommended operational rule: take a file-level backup of `ACM_DB_PATH` before every production deploy.

## Logging and secrets

- Never commit `.env`.
- Do not store production secrets in repo files.
- Agent runtime logs may contain prompt and model output content. Keep `logs_agent/` and `logs_runtime/` off persistent shared disks unless log redaction is added.
