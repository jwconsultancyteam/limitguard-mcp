import json

import anyio
import httpx
from limitguard_mcp import server

BASE = "https://api.example.test"


def _call(name, arguments, handler, api_key="lg_live_test"):
    async def go():
        return await server.call_rest(
            name, arguments, api_key=api_key, base_url=BASE, transport=httpx.MockTransport(handler)
        )

    return anyio.run(go)


def test_every_tool_has_a_rest_path_and_schema():
    assert len(server.TOOLS) == 10
    for tool in server.TOOLS:
        assert tool["rest_path"].startswith("/v1/"), tool["name"]
        assert tool["inputSchema"]["type"] == "object", tool["name"]
        assert tool["description"], tool["name"]


def test_list_tools_matches_tools_json_without_rest_path():
    listed = server.mcp_tools()
    assert [t.name for t in listed] == [t["name"] for t in server.TOOLS]
    dumped = listed[0].model_dump(by_alias=True, exclude_none=True)
    assert "rest_path" not in json.dumps(dumped)
    assert dumped["inputSchema"] == server.TOOLS[0]["inputSchema"]


def test_call_posts_arguments_as_body_with_api_key():
    seen = {}

    def handler(request: httpx.Request):
        seen["path"] = request.url.path
        seen["key"] = request.headers["X-API-Key"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"verdict": "proceed", "lead_score": 91})

    result = _call("verify_lead", {"country": "NL", "company_number": "12345678", "email": None}, handler)
    assert seen == {
        "path": "/v1/leads/verify",
        "key": "lg_live_test",
        "body": {"country": "NL", "company_number": "12345678"},
    }
    assert not result.is_error
    assert result.structured_content == {"verdict": "proceed", "lead_score": 91}


def test_402_is_a_tool_error_naming_the_top_up_route():
    def handler(request):
        return httpx.Response(402, json={"detail": "Insufficient balance"})

    result = _call("sanctions_screen", {"name": "Acme BV"}, handler)
    assert result.is_error
    text = result.content[0].text
    assert "402" in text and "/v1/keys/topup/" in text and "Insufficient balance" in text


def test_missing_key_never_calls_the_api():
    def handler(request):
        raise AssertionError("no request without a key")

    result = _call("check_entity", {"entity_name": "Acme", "country": "NL"}, handler, api_key=None)
    assert result.is_error
    assert "LIMITGUARD_API_KEY" in result.content[0].text


def test_unknown_tool_is_an_error():
    result = _call("nope", {}, lambda r: httpx.Response(200, json={}))
    assert result.is_error


def test_network_failure_is_a_tool_error():
    def handler(request):
        raise httpx.ConnectError("down")

    result = _call("get_risk_score", {"entity_name": "Acme", "country": "NL"}, handler)
    assert result.is_error
    assert "Could not reach" in result.content[0].text
