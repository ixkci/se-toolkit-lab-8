"""Clients for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import httpx


class ObsClient:
    def __init__(self, logs_url: str, traces_url: str) -> None:
        self.logs_url = logs_url.rstrip("/")
        self.traces_url = traces_url.rstrip("/")

    async def logs_search(
        self, query: str, limit: int = 20
    ) -> list[dict]:
        url = f"{self.logs_url}/select/logsql/query"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params={"query": query, "limit": limit})
            resp.raise_for_status()
            lines = [l for l in resp.text.strip().splitlines() if l.strip()]
            import json
            return [json.loads(l) for l in lines]

    async def logs_error_count(
        self, service: str, time_window: str = "10m"
    ) -> dict:
        query = f'_time:{time_window} service.name:"{service}" severity:ERROR'
        url = f"{self.logs_url}/select/logsql/query"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params={"query": query, "limit": 1000})
            resp.raise_for_status()
            lines = [l for l in resp.text.strip().splitlines() if l.strip()]
            return {"service": service, "time_window": time_window, "error_count": len(lines)}

    async def traces_list(
        self, service: str, limit: int = 5
    ) -> list[dict]:
        url = f"{self.traces_url}/select/jaeger/api/traces"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, params={"service": service, "limit": limit})
            resp.raise_for_status()
            data = resp.json()
            result = []
            for t in data.get("data", []):
                root = next(
                    (s for s in t["spans"] if not s.get("references")), None
                )
                has_error = any(
                    tag["key"] == "error"
                    for s in t["spans"]
                    for tag in s.get("tags", [])
                )
                result.append({
                    "traceID": t["traceID"],
                    "operation": root["operationName"] if root else "unknown",
                    "duration_ms": root["duration"] // 1000 if root else 0,
                    "has_error": has_error,
                })
            return result

    async def traces_get(self, trace_id: str) -> dict:
        url = f"{self.traces_url}/select/jaeger/api/traces/{trace_id}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("data"):
                return {"error": "trace not found"}
            t = data["data"][0]
            spans = []
            for s in sorted(t["spans"], key=lambda x: x["startTime"]):
                has_error = any(tag["key"] == "error" for tag in s.get("tags", []))
                spans.append({
                    "spanID": s["spanID"],
                    "operation": s["operationName"],
                    "duration_ms": s["duration"] // 1000,
                    "has_error": has_error,
                    "parent": s["references"][0]["spanID"] if s.get("references") else None,
                })
            return {"traceID": t["traceID"], "spans": spans}
