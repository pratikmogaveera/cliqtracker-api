# cliqtracker-api

FastAPI backend for Cliqtracker — URL shortener + click analytics platform.

## Purpose

Handles link management, JWT auth with httpOnly cookies, 302 redirects with Redis caching, async click processing (geo + UA parsing + query params tracking) via ARQ background worker. Deployed on Railway.

## Tech Stack

| Layer | Tech |
|-------|------|
| Framework | FastAPI (Python) |
| Database | PostgreSQL — SQLAlchemy async + Alembic |
| Cache / Queue | Redis — ARQ background worker |
| Auth | JWT (`python-jose`) + `httpOnly` cookies |
| Geo lookup | MaxMind GeoLite2 (local `.mmdb` file) |
| UA parsing | `user-agents` |
| Deployment | Railway |

## How to Run

```bash
cp .env.example .env
docker compose up
```

Without Docker:

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# separate terminal:
python -m app.worker
```

API at `http://localhost:8000` — interactive docs at `/docs`.

> **Note:** Download `GeoLite2-City.mmdb` from [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) and place it in the project root before running.

## File Structure

```
cliqtracker-api/
├── app/
│   ├── main.py                   — app factory, lifespan, exception handler
│   ├── deps.py                   — Annotated type aliases, get_user_id, require_scope, RequiredScope
│   ├── middleware.py              — Token Bucket rate limiting middleware
│   └── core/
│       ├── config.py             — pydantic-settings config
│       ├── database.py           — async engine, session factory, get_db
│       ├── redis.py              — get_redis, get_arq_pool dependencies
│       ├── security.py           — password hashing, JWT encode/decode
│       └── rate_limit.py         — Token Bucket check function
│   ├── models/
│   │   ├── user.py               — User ORM model
│   │   ├── link.py               — Link ORM model
│   │   ├── click_event.py        — ClickEvent ORM model
│   │   └── error_log.py          — ErrorLog ORM model
│   ├── schemas/
│   │   ├── common.py             — ApiResponse, PaginatedResponse
│   │   ├── user.py               — user request/response schemas
│   │   ├── link.py               — link request/response schemas
│   │   ├── click_event.py        — click event response schema
│   │   ├── analytics.py          — analytics response schemas
│   │   ├── redirect.py           — unlock request/response schemas
│   │   └── error_log.py          — error log create schema
│   ├── routers/
│   │   ├── auth.py               — login, refresh, logout
│   │   ├── user.py               — register, me, update, delete
│   │   ├── link.py               — link CRUD
│   │   ├── redirect.py           — /go/{short_code} redirect handler
│   │   ├── analytics.py          — /links/{link_id}/analytics/* endpoints
│   │   └── service_token.py      — service token CRUD + rotate
│   ├── services/
│   │   ├── auth.py               — authenticate, session management
│   │   ├── user.py               — user CRUD
│   │   ├── link.py               — link CRUD
│   │   ├── redirect.py           — Redis cache-aside + DB fallback
│   │   ├── click_event.py        — click event operations
│   │   ├── analytics.py          — analytics queries (summary, timeseries, geo, devices, referrers)
│   │   ├── service_token.py      — service token CRUD + rotation logic
│   │   └── error_log.py          — error log insert
│   ├── tasks.py                  — ARQ job definitions (process_click)
│   └── worker.py                 — ARQ WorkerSettings, startup/shutdown
├── alembic/                      — migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── PLAN.md
└── README.md
```

## Progress

### Phase 1 — Project Setup + Auth
- [x] Project structure + config
- [x] Async SQLAlchemy + Alembic setup
- [x] Redis connection
- [x] `POST /auth/register`
- [x] `POST /auth/login` + httpOnly cookie
- [x] `POST /auth/refresh`
- [x] `POST /auth/logout`
- [x] `GET /auth/me`

### Phase 2 — Links + Redirect
- [x] `links` + `click_events` migrations
- [x] `POST /links`
- [x] `GET /links`
- [x] `GET /links/{id}`
- [x] `PATCH /links/{id}`
- [x] `DELETE /links/{id}`
- [x] `GET /go/{short_code}` — Redis cache + 302

### Phase 3 — Background Worker + Analytics
- [x] ARQ worker setup
- [x] GeoLite2 + `user-agents` integration
- [x] `process_click` job
- [x] Swap redirect to enqueue job
- [x] Analytics endpoints (summary, timeseries, geo, devices, referrers)

### Phase 4 — Advanced Features
- [x] Link expiry
- [x] Password protection
- [x] API key auth
- [x] Rate limiting
- [~] Bulk CSV upload — intentionally skipped
- [x] QR code generation

### Phase 5 — Polish + Deploy
- [ ] Abuse detection
- [x] Dockerfile + Docker Compose
- [x] Deploy to Railway
- [x] CORS middleware (environment-aware origins)
- [x] Composite indexes (analytics + owner_id)
- [x] `hashed_ip` for unique visitor tracking
- [x] Analytics enhancements (date range, unique counts, continent breakdown)
- [x] `is_active` check in redirect flow
- [x] `secure=True` on cookies (environment-aware)
- [x] Field validations on request schemas
- [x] `RequestValidationError` handler
- [x] Generic 500 handler + `error_logs` table
- [x] Query params tracking (`params` JSONB + GIN index)

## Resources

- [FastAPI docs](https://fastapi.tiangolo.com)
- [SQLAlchemy async docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic docs](https://alembic.sqlalchemy.org/en/latest/)
- [ARQ docs](https://arq-docs.helpmanual.io/)
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [user-agents PyPI](https://pypi.org/project/user-agents/)
