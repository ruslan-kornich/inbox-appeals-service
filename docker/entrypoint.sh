#!/bin/sh
set -e

# --- DB wait ---
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

echo "⏳ Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} ..."
i=0
until nc -z "${DB_HOST}" "${DB_PORT}"; do
  i=$((i+1))
  if [ "$i" -gt 60 ]; then
    echo "❌ PostgreSQL is not reachable after 60s. Exiting."
    exit 1
  fi
  sleep 1
done
echo "✅ PostgreSQL is reachable."

# --- Ensure Aerich config exists (non-interactive) ---
# If aerich.ini is missing (e.g., not committed), create it on the fly.
if [ ! -f "/app/aerich.ini" ]; then
  echo "ℹ️ aerich.ini not found; initializing Aerich config..."
  aerich init -t app.config.db.TORTOISE_ORM
fi

# --- Migrations strategy ---
# MIGRATION_STRATEGY can be: auto (default) | upgrade | init-db
STRATEGY="${MIGRATION_STRATEGY:-auto}"

apply_upgrade() {
  echo "🩺 Applying migrations with 'aerich upgrade'..."
  aerich upgrade
}

apply_initdb() {
  echo "🧱 Creating initial schema with 'aerich init-db'..."
  aerich init-db
}

ensure_schemas_with_tortoise() {
  echo "⚠️ Falling back to 'Tortoise.generate_schemas(safe=True)'..."
  python3 - <<'PY'
import asyncio
from tortoise import Tortoise
from app.config.db import TORTOISE_ORM

async def main():
    # Initialize and create schemas if not present (safe=True won't drop anything)
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)
    await Tortoise.close_connections()

asyncio.run(main())
PY
  echo "✅ Schemas ensured via Tortoise."
}

case "$STRATEGY" in
  upgrade)
    if apply_upgrade; then
      echo "✅ 'aerich upgrade' applied."
    else
      echo "❌ 'aerich upgrade' failed. Exiting."
      exit 1
    fi
    ;;
  init-db)
    if apply_initdb; then
      echo "✅ 'aerich init-db' completed."
    else
      echo "❌ 'aerich init-db' failed."
      ensure_schemas_with_tortoise
    fi
    ;;
  auto|*)
    # Try 'upgrade' first; if it fails (fresh DB/no revision table), fall back to 'init-db'.
    if apply_upgrade; then
      echo "✅ 'aerich upgrade' applied."
    else
      echo "⚠️ 'aerich upgrade' failed; trying 'aerich init-db'..."
      if apply_initdb; then
        echo "✅ 'aerich init-db' completed."
      else
        echo "⚠️ 'aerich init-db' failed; ensuring schemas via Tortoise..."
        ensure_schemas_with_tortoise
      fi
    fi
    ;;
esac

# --- Seeding (optional, default = true) ---
if [ "${SEED_ON_START:-true}" = "true" ]; then
  echo "🌱 Running seed demo data..."
  # If your seeder relies on Tortoise, it MUST init Tortoise inside.
  # If it doesn't, add Tortoise.init/close around its logic.
  python3 -m app.utils.demo.seed_demo_data --reset || true
  echo "✅ Seed step finished."
fi

# --- Start app ---
echo "🚀 Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
