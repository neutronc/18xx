# Configuration and Operations Reference

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `RACK_ENV` | Yes | `development` | `production` enables New Relic, disables source maps, precompiles assets |
| `DATABASE_URL` | Yes | — | PostgreSQL connection string, e.g. `postgres://user:pass@db:5432/18xx` |
| `APP_DATABASE_URL` | No | falls back to `DATABASE_URL` | Alternative DB URL for the app (useful if queue uses a different connection) |
| `NEW_RELIC_LICENSE_KEY` | No | — | Enables New Relic APM in production |
| `ELASTIC_KEY` | No | — | Elasticsearch integration key |
| `SLACK_WEBHOOK_URL` | No | — | Slack webhook for deployment notifications |
| `RUBYOPT` | No | — | Set to `--yjit` in production to enable YJIT JIT compiler |
| `PORT` | No | `9292` | Port the Unicorn server binds to |
| `OPAL_PREFORK_DISABLE` | No | — | Set to `"true"` to skip Opal prefork initialisation in production |

## Docker Compose Profiles

| Profile | Command | Purpose |
|---------|---------|---------|
| Development | `make` | Runs `docker compose up` with `docker-compose.dev.yml` override; uses `rerun` for auto-restart |
| Development (rebuild) | `make dev_up_b` | Same as above but forces a container rebuild |
| Production | `make prod_up` | Uses `docker-compose.prod.yml`; Unicorn server, YJIT, asset precompilation |
| Production (rebuild) | `make prod_up_b` | Forces rebuild before starting |
| Production (deploy) | `make prod_deploy` | Pulls latest master, rebuilds, restarts |

**Containers:**

| Name | Role | Exposed port |
|------|------|-------------|
| `rack` | Roda web server (Unicorn) | `9292` |
| `rack_backup` | Hot standby (production only) | — |
| `queue` | Rufus-Scheduler background jobs | — |
| `db` | PostgreSQL | `5433` (host) |
| `redis` | Redis | `6380` (host) |
| `nginx` | Reverse proxy (production only) | `80`, `443` |

## Database

The database schema is managed by Sequel migrations in `migrate/`. To run all pending migrations:

```bash
docker compose exec rack bundle exec rake migrate
```

Database data is mounted from `./db/data` on the host (UID 1000). To restore from backup:

1. Stop the stack.
2. Remove `db/data/`: `rm -rf db/data`.
3. Restart the stack (creates a fresh cluster).
4. Restore: `docker compose exec -T db pg_restore ...`

## Background Jobs (`queue.rb`)

The `queue` container runs `bundle exec ruby queue.rb`. It registers one cron job:

**Daily at 09:00 UTC** [`queue.rb:35`]:

1. Recalculates user statistics.
2. Archives games: finished games older than **365 days** and active games with no activity for **90 days**. Archival removes the action list; only metadata is retained [`queue.rb:38-48`].
3. Deletes unused pin bundles (retains the two newest) [`queue.rb:50-62`].
4. Destroys unlisted `new`-status games older than 180 days; listed `new` games older than 14 days.

**MessageBus subscribers** in `queue.rb`:

| Channel | Trigger | Action |
|---------|---------|--------|
| `/turn` | After each accepted action | Sends email or webhook notification to active players |
| `/test_notification` | Manual test | Sends a test webhook to one user |
| `/delete_user` | Account deletion | Removes all games and the user record |

## Pinned Game Bundles

Old JavaScript bundles are stored at `/18xx/public/pinned/<pin>.js.gz` (inside the container; mounted from `./public` on the host). The `queue.rb` cleanup job removes pin files that are no longer referenced by any active or finished game [`queue.rb:50-62`].

## Logging

All containers write to stdout with `max-size: 10m` (development) or `50m` (production) log rotation. Application logs use Ruby's `Logger` writing to `$stdout`. New Relic APM is active when `NEW_RELIC_LICENSE_KEY` is set and `RACK_ENV=production`.

## What's next

- Background job rationale: [Architecture Overview](architecture.html)
- System boundaries and external dependencies: [System Boundaries](systemgrenzen.html)

---
*Version: 2026-05-08 — derived from `queue.rb`, `docker-compose.yml`, `docker-compose.prod.yml`, `Makefile`, `db.rb`, `DEVELOPMENT.md`.*
