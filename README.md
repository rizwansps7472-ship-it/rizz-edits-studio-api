# Rizz Edits Studio API (Phase 6 — FastAPI backend)

Python backend for the Rizz Edits Studio website. Handles project-inquiry
submissions with server-side validation, rate limiting, database persistence,
and optional email notifications.

## Quick start (local)

```bash
cd rizz-edits-studio-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional; defaults work out of the box
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs

## Endpoints

| Method | Path              | Auth      | Description                              |
|--------|-------------------|-----------|------------------------------------------|
| GET    | `/api/health`     | none      | Health check                             |
| POST   | `/api/inquiries`  | rate-limited | Submit a project inquiry (validated)  |
| GET    | `/api/inquiries`  | `X-API-Key` header | List inquiries, newest first (admin) |

`POST /api/inquiries` body:

```json
{
  "name": "Ayesha Khan",
  "email": "ayesha@example.com",
  "service": "AI Chatbots",
  "message": "We need a WhatsApp support bot for our store...",
  "source_page": "contact"
}
```

Validation failures return `422` with per-field messages. More than
`RATE_LIMIT_PER_MINUTE` POSTs per IP per minute returns `429`.

## Configuration (`.env`)

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./rizz_studio.db` | Use `postgresql+psycopg2://...` in production (add `psycopg2-binary` to requirements) |
| `ALLOWED_ORIGINS` | _(empty)_ | Comma-separated site origins, e.g. `https://rizzedits.com`. `"*"` for local dev only |
| `ADMIN_API_KEY` | _(empty)_ | Required to use `GET /api/inquiries`; generate with `secrets.token_urlsafe(32)` |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM` | _(empty)_ | SMTP for new-inquiry emails; unset = logged only |
| `NOTIFY_TO` | _(empty)_ | Where inquiry notification emails go |
| `RATE_LIMIT_PER_MINUTE` | `20` | Per-IP POST limit |

## Connecting the website (Phase 7)

The static site reads `window.RIZZ_API_BASE` (set it before the site's
scripts load, e.g. `<script>window.RIZZ_API_BASE="https://api.rizzedits.com"</script>`).
When set, forms POST to `{base}/api/inquiries` with loading/error states;
when unset or unreachable, they fall back to composing the brief in-browser.

## Deploying (Phase 9 notes)

- **Render / Railway / Fly.io:** new Python service, build `pip install -r requirements.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, set env vars, attach Postgres and set `DATABASE_URL`.
- **VPS:** run behind nginx with systemd; example unit ships below. Use Postgres, set `ALLOWED_ORIGINS` to the real site domain, never `"*"`.
- **Security checklist:** strong `ADMIN_API_KEY`, SMTP credentials in env (never in code), HTTPS only, keep dependencies updated.

## Tests

```bash
# with the server running on :8000
python3 tests/smoke.py
```
