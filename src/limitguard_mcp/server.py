"""Limitguard MCP server over stdio.

Each tool runs on the Limitguard REST API: the tool's arguments are the JSON body of
the REST route it is defined by (tools.json's ``rest_path``), sent with the caller's
API key. The tool names, descriptions and input schemas are generated from the served
MCP server card, so this server lists exactly what https://api.limitguard.ai/mcp lists.

A REST call is debited from the key's prepaid balance. x402 per-call payment is a
remote-transport feature: a key with no balance gets the API's 402 answer back as a
tool error that names the top-up route.
"""

from __future__ import annotations

import json
import os
from importlib import resources
from typing import Any

import anyio
import httpx
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from limitguard_mcp import __version__

DEFAULT_BASE_URL = "https://api.limitguard.ai"
KEY_ENV = "LIMITGUARD_API_KEY"
BASE_URL_ENV = "LIMITGUARD_BASE_URL"
# A lead or company check reads registers that can answer slowly; the API itself
# answers 503 within its own budget, so this only guards a hung connection.
TIMEOUT_SECONDS = 60.0
NO_KEY = (
    f"{KEY_ENV} is not set. Get a free key with POST {DEFAULT_BASE_URL}/v1/keys/create "
    'and a JSON body {"email": "you@example.com"}, then add prepaid credit to it for the paid tools.'
)


def load_tools() -> list[dict[str, Any]]:
    raw = resources.files("limitguard_mcp").joinpath("tools.json").read_text(encoding="utf-8")
    return json.loads(raw)["tools"]


TOOLS = load_tools()
TOOLS_BY_NAME = {tool["name"]: tool for tool in TOOLS}


def mcp_tools() -> list[types.Tool]:
    return [
        types.Tool.model_validate({k: v for k, v in tool.items() if k != "rest_path"})
        for tool in TOOLS
    ]


def _error(text: str) -> types.CallToolResult:
    return types.CallToolResult(content=[types.TextContent(type="text", text=text)], is_error=True)


def _problem_text(status: int, body: Any, rest_path: str) -> str:
    """One readable sentence from the API's error body, plus the raw body for an agent."""
    detail = ""
    if isinstance(body, dict):
        detail = str(body.get("detail") or body.get("error") or body.get("title") or "")
    if status == 401:
        lead = f"The API key was refused (401). Check {KEY_ENV}."
    elif status == 402:
        lead = (
            f"Payment required (402) for {rest_path}: this key has no prepaid balance for the call. "
            f"Add credit with POST {DEFAULT_BASE_URL}/v1/keys/topup/{{usd}} (from $5), or call "
            f"{DEFAULT_BASE_URL}/mcp, which also accepts an x402 payment per call."
        )
    elif status == 429:
        lead = f"Rate or daily limit reached (429) for {rest_path}."
    elif status == 503:
        lead = f"A source could not be reached (503) for {rest_path}; the call was not charged. Try again later."
    else:
        lead = f"The API answered {status} for {rest_path}."
    body_text = json.dumps(body, ensure_ascii=False) if not isinstance(body, str) else body
    return f"{lead} {detail}".strip() + f"\n\n{body_text}"


async def call_rest(
    name: str,
    arguments: dict[str, Any] | None,
    *,
    api_key: str | None,
    base_url: str,
    transport: httpx.AsyncBaseTransport | None = None,
) -> types.CallToolResult:
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        return _error(f"Unknown tool: {name}")
    if not api_key:
        return _error(NO_KEY)
    body = {k: v for k, v in (arguments or {}).items() if v is not None}
    rest_path = tool["rest_path"]
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": f"limitguard-mcp/{__version__} (stdio)",
    }
    try:
        async with httpx.AsyncClient(
            base_url=base_url, timeout=TIMEOUT_SECONDS, transport=transport
        ) as client:
            response = await client.post(rest_path, json=body, headers=headers)
    except httpx.HTTPError as exc:
        return _error(f"Could not reach {base_url}{rest_path}: {type(exc).__name__}.")
    try:
        payload: Any = response.json()
    except ValueError:
        payload = response.text
    if response.status_code >= 400:
        return _error(_problem_text(response.status_code, payload, rest_path))
    text = json.dumps(payload, ensure_ascii=False, indent=2) if not isinstance(payload, str) else payload
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        structured_content=payload if isinstance(payload, dict) else None,
    )


def build_server(transport: httpx.AsyncBaseTransport | None = None) -> Server:
    async def on_list_tools(ctx, params) -> types.ListToolsResult:
        return types.ListToolsResult(tools=mcp_tools())

    async def on_call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
        return await call_rest(
            params.name,
            params.arguments,
            api_key=os.environ.get(KEY_ENV, "").strip() or None,
            base_url=os.environ.get(BASE_URL_ENV, "").strip() or DEFAULT_BASE_URL,
            transport=transport,
        )

    return Server(
        "limitguard",
        version=__version__,
        title="Limitguard",
        website_url="https://limitguard.ai",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )


async def _run() -> None:
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    anyio.run(_run)


if __name__ == "__main__":
    main()
