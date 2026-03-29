# Observability Skill

When the user asks about errors, performance issues, or system health:

1. **Start with error counts** — call `logs_error_count` for the relevant service and time window (default: last 10 minutes).

2. **Search logs for details** — if errors exist, call `logs_search` with a focused LogsQL query to find recent error log entries and extract `trace_id` fields.
   - Example query: `_time:10m service.name:"Learning Management Service" severity:ERROR`

3. **Fetch the trace** — if a `trace_id` is found in the logs, call `traces_get` with that ID to inspect the full span hierarchy.

4. **Summarize concisely** — do NOT dump raw JSON. Instead report:
   - How many errors occurred and in which service
   - Which operation failed (e.g. `POST /pipeline/sync`)
   - Where in the span tree the error appeared (e.g. database connection, external API)
   - The root cause if visible (e.g. "PostgreSQL unreachable", "DNS resolution failed")

## Field names in VictoriaLogs

- `service.name` — service name
- `severity` — log level (ERROR, INFO, etc.)
- `trace_id` — OpenTelemetry trace ID
- `_time` — timestamp filter (e.g. `_time:10m` = last 10 minutes)

## Service names

- `Learning Management Service` — the LMS backend
