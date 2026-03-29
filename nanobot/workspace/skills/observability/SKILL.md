# Observability Skill

When the user asks "What went wrong?", "Check system health", or about errors/performance issues:

## Investigation flow (always follow this order)

1. **Count errors** — call `logs_error_count` for `Learning Management Service`, time window `5m`
2. **Search logs** — call `logs_search` with a focused LogsQL query to find recent error entries and extract `trace_id`
   - Example: `_time:5m service.name:"Learning Management Service" severity:ERROR`
3. **Fetch the trace** — call `traces_get` with the most recent `trace_id` found in logs
4. **Summarize** — write one short paragraph that mentions:
   - How many errors, in which service
   - Which endpoint/operation failed
   - Where in the span tree the error appeared
   - The root cause (e.g. "PostgreSQL unreachable", "DNS resolution failed")
   - Note any discrepancy between what the HTTP response says and what logs/traces reveal

## Rules
- ALWAYS use both log evidence AND trace evidence before answering
- Do NOT dump raw JSON
- Do NOT skip `traces_get` if a `trace_id` is available

## Field names in VictoriaLogs
- `service.name` — service name
- `severity` — log level (ERROR, INFO, etc.)
- `trace_id` — OpenTelemetry trace ID
- `_time` — timestamp filter (e.g. `_time:5m` = last 5 minutes)

## Service names
- `Learning Management Service` — the LMS backend
