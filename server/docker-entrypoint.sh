#!/usr/bin/env bash
# Point config.lua at the database from env, create the schema on first start, run.
set -euo pipefail
: "${DB_HOST:=db}" "${DB_PORT:=3306}" "${DB_NAME:=hunterrealms}" "${DB_USER:=hunter}" "${DB_PASSWORD:=hunter}"
sed -i \
  -e "s|^mysqlHost = .*|mysqlHost = \"${DB_HOST}\"|" \
  -e "s|^mysqlPort = .*|mysqlPort = ${DB_PORT}|" \
  -e "s|^mysqlDatabase = .*|mysqlDatabase = \"${DB_NAME}\"|" \
  -e "s|^mysqlUser = .*|mysqlUser = \"${DB_USER}\"|" \
  -e "s|^mysqlPass = .*|mysqlPass = \"${DB_PASSWORD}\"|" \
  -e "s|^ip = .*|ip = \"${GAME_HOST:-127.0.0.1}\"|" \
  config.lua
MYSQL=(mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME")
until "${MYSQL[@]}" -e "SELECT 1" >/dev/null 2>&1; do echo "waiting for database..."; sleep 2; done
if ! "${MYSQL[@]}" -e "SELECT 1 FROM accounts LIMIT 1" >/dev/null 2>&1; then
  echo "first start: creating schema"
  "${MYSQL[@]}" < schema.sql
  if [ "${SEED_DEV_ACCOUNT:-false}" = "true" ]; then "${MYSQL[@]}" < sql/seed-dev.sql; fi
fi
exec ./canary
