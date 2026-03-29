"""Stdio MCP server for observability tools."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_obs.observability import ObsClient

TOOLS: list[Tool] = [
    Tool(
        name="logs_search",
        description="Search logs in VictoriaLogs by LogsQL query and optional time range.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "LogsQL query, e.g. '_time:10m service.name:\"Learning Management Service\" severity:ERROR'"},
                "limit": {"type": "integer", "default": 20, "description": "Max number of log entries to return"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="logs_error_count",
        description="Count ERROR-level log entries for a service over a time window.",
        inputSchema={
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Service name, e.g. 'Learning Management Service'"},
                "time_window": {"type": "string", "default": "10m", "description": "Time window, e.g. '10m', '1h'"},
            },
            "required": ["service"],
        },
    ),
    Tool(
        name="traces_list",
        description="List recent traces for a service from VictoriaTraces.",
        inputSchema={
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Service name"},
                "limit": {"type": "integer", "default": 5, "description": "Max number of traces"},
            },
            "required": ["service"],
        },
    ),
    Tool(
        name="traces_get",
        description="Fetch a specific trace by ID from VictoriaTraces and return its span hierarchy.",
        inputSchema={
            "type": "object",
            "properties": {
                "trace_id": {"type": "string", "description": "Trace ID to fetch"},
            },
            "required": ["trace_id"],
        },
    ),
]


def create_server(client: ObsClient) -> Server:
    server = Server("obs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        args = arguments or {}
        try:
            if name == "logs_search":
                result = await client.logs_search(args["query"], args.get("limit", 20))
            elif name == "logs_error_count":
                result = await client.logs_error_count(args["service"], args.get("time_window", "10m"))
            elif name == "traces_list":
                result = await client.traces_list(args["service"], args.get("limit", 5))
            elif name == "traces_get":
                result = await client.traces_get(args["trace_id"])
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    logs_url = os.environ.get("VICTORALOGS_URL", "http://localhost:9428")
    traces_url = os.environ.get("VICTORIATRACES_URL", "http://localhost:10428")
    client = ObsClient(logs_url, traces_url)
    server = create_server(client)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
