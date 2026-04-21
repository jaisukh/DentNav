#!/bin/sh
set -e
cd /app

# Align Alembic when the DB was created manually or a volume has tables but no
# alembic_version row (common after compose down/up with persistent volume).
run_migrations() {
  alembic upgrade head
}

if ! run_migrations; then
  echo "docker-entrypoint: initial alembic upgrade failed; repairing stamp then retrying" >&2
  alembic stamp 0001 2>/dev/null || true
  if ! run_migrations; then
    alembic stamp head 2>/dev/null || true
    run_migrations
  fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
