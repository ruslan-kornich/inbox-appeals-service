---
title: "Inbox Appeals Service"
description: "Private appeals channel with staff workflow and admin analytics. FastAPI + Tortoise ORM + PostgreSQL + Docker Compose."
tags: [FastAPI, "Tortoise ORM", PostgreSQL, Docker, JWT, Aerich, MongoDB]
---

# Inbox Appeals Service

A compact service that gives users a **private channel for appeals**, provides **staff** with tools to process them, and offers **admin** analytics.

- **Core stack:** FastAPI, Tortoise ORM, PostgreSQL, Docker Compose  
- **Optional:** Aerich (migrations), MongoDB  
- **Auth:** JWT-based; role model with `USER`, `STAFF`, `ADMIN`

## Prerequisites
- Docker & Docker Compose installed

## Quick Start (Docker)
```bash
docker compose down -v
docker compose build --no-cache --progress=plain
docker compose up -d
docker compose logs -f web
```
- App: `http://localhost:8000` (Swagger UI at `/docs`)  
- PostgreSQL: `localhost:55432` (user: `inbox`, db: `inbox_appeals`)

## Tests (host)
```bash
pytest -q
```

## Environment (defaults)
```dotenv
DATABASE_URL=postgres://inbox:Strong123@db:5432/inbox_appeals
TZ=Europe/Kyiv
```

## Seed Data (auto on first boot)
- **Admin:** `admin@i.ua / Strong123!`  
- **Staff:** 10 accounts with role `STAFF`, password `Strong123!`  
  (Unique emails; check `docker compose logs -f web` for the exact list.)

> To reseed manually:
> ```bash
> python -m app.utils.demo.seed_demo_data --reset
> ```

## Auth & Roles
- Login: `POST /api/v1/auth/login` → returns JWT  
- Use header: `Authorization: Bearer <token>`  
- Role-gated APIs:
  - `USER`: create appeals
  - `STAFF`: process appeals
  - `ADMIN`: analytics, staff management

## Cleanup
```bash
docker compose down -v
```
