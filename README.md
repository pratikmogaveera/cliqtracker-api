# cliqtracker-api

FastAPI backend for Cliqtracker — URL shortener + click analytics platform.

## Purpose

Handles link management, JWT auth with httpOnly cookies, 302 redirects with Redis caching, and async click processing (geo + UA parsing) via ARQ background worker. Deployed on Railway.

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
│   ├── deps.py                   — get_user_id dependency
│   ├── core/
│   │   ├── config.py             — pydantic-settings config
│   │   ├── database.py           — async engine, session factory, get_db
│   │   ├── redis.py              — get_redis dependency
│   │   └── security.py           — password hashing, JWT encode/decode
│   ├── models/
│   │   └── user.py               — User ORM model
│   ├── schemas/
│   │   ├── common.py             — ApiResponse generic wrapper
│   │   └── user.py               — request/response schemas
│   ├── routers/
│   │   ├── auth.py               — login, refresh, logout
│   │   └── user.py               — register, me, update, delete
│   └── services/
│       ├── auth.py               — authenticate, session management
│       └── user.py               — user CRUD
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
- [ ] `links` + `click_events` migrations
- [ ] `POST /links`
- [ ] `GET /links`
- [ ] `GET /links/{id}`
- [ ] `PATCH /links/{id}`
- [ ] `DELETE /links/{id}`
- [ ] `GET /go/{short_code}` — Redis cache + 302

### Phase 3 — Background Worker + Analytics
- [ ] ARQ worker setup
- [ ] GeoLite2 + `user-agents` integration
- [ ] `process_click` job
- [ ] Swap redirect to enqueue job
- [ ] Analytics endpoints (summary, timeseries, geo, devices, referrers)

### Phase 4 — Advanced Features
- [ ] Link expiry
- [ ] Password protection
- [ ] API key auth
- [ ] Rate limiting
- [ ] Bulk CSV upload
- [ ] QR code generation

### Phase 5 — Polish + Deploy
- [ ] Abuse detection
- [ ] Dockerfile + Docker Compose
- [ ] Deploy to Railway

## Resources

- [FastAPI docs](https://fastapi.tiangolo.com)
- [SQLAlchemy async docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic docs](https://alembic.sqlalchemy.org/en/latest/)
- [ARQ docs](https://arq-docs.helpmanual.io/)
- [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [user-agents PyPI](https://pypi.org/project/user-agents/)
