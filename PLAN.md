# cliqtracker-api — Plan

FastAPI backend for Cliqtracker. Covers auth, link CRUD, Redis-cached redirects, ARQ background click processing, and analytics queries.

---

## 1. Project Setup + Auth

**Goal:** Scaffold the project and implement JWT auth with httpOnly cookies.

**Tasks:**
- Project structure — `app/`, `routers/`, `models/`, `schemas/`, `services/`, `core/`
- Config with `pydantic-settings`
- Async SQLAlchemy engine + session factory + `get_db` dependency
- Redis connection pool + `get_redis` dependency
- Alembic init + `users` migration
- `POST /auth/register`
- `POST /auth/login` — issue access token, set httpOnly cookie, store refresh token in Redis
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

---

## 2. Links + Redirect

**Goal:** Full link CRUD and a working 302 redirect with Redis cache.

**Tasks:**
- Alembic migration — `links` + `click_events` tables
- `POST /links` — create with nanoid slug, populate Redis cache
- `GET /links` — paginated list
- `GET /links/{id}`
- `PATCH /links/{id}` — update + cache eviction
- `DELETE /links/{id}` — soft deactivate + cache eviction
- `GET /go/{short_code}` — Redis lookup → 302, synchronous click insert

---

## 3. Background Worker + Analytics

**Goal:** Move click processing to an ARQ worker and expose analytics endpoints.

**Tasks:**
- ARQ worker setup — lifespan-managed Redis pool
- GeoLite2 reader loaded once on startup
- `process_click` job — geo lookup + UA parsing + DB insert
- Swap redirect handler to enqueue ARQ job
- `GET /links/{id}/analytics/summary`
- `GET /links/{id}/analytics/timeseries` — `?granularity=hourly|daily`
- `GET /links/{id}/analytics/geo`
- `GET /links/{id}/analytics/devices`
- `GET /links/{id}/analytics/referrers`

---

## 4. Advanced Features

**Goal:** Link expiry, password protection, API keys, rate limiting, bulk upload, QR codes.

**Tasks:**
- Link expiry — check in redirect handler, align Redis TTL
- Password protection — `POST /go/{short_code}/unlock`
- API key generation + revocation
- API key auth dependency (`X-API-Key` header)
- Rate limiting per user/key
- Bulk CSV upload — `POST /links/bulk`
- QR code — `GET /links/{id}/qr`

---

## 5. Polish + Deploy

**Goal:** Abuse detection, Docker, Railway deployment.

**Tasks:**
- Abuse detection — click spike flagging
- Dockerfile + Docker Compose (`api` + `worker` + `postgres` + `redis`)
- CORS — dev origins only
- Deploy to Railway
- `.env.example` + API docs in README
