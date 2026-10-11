from limitguard_mcp.guardrails import strip_internal_fields


def test_sanctions_entries_keep_scores_and_dataset_names_only():
    result = strip_internal_fields({
        "sanctions_match": 1,
        "match_score": "0.8",
        "datasets": [{"name": "OFAC", "address": "Private street"}],
        "entries": [{"aliases": ["Private alias"], "nationality": "BE", "list": "OFAC"}],
    })
    assert result == {
        "sanctions_match": True,
        "match_score": 0.8,
        "datasets": ["OFAC"],
        "entries": [{"list": "OFAC"}],
    }


def test_internal_fields_are_removed_at_every_depth():
    private = {name: "internal" for name in (
        "api_key", "api_key_id", "api_secret", "internal_score", "internal_id", "debug",
        "trace_id", "correlation_id", "stack_trace", "raw_query", "sql", "redis_key",
        "tenant_id", "session_token", "password", "secret",
    )}
    assert strip_internal_fields({**private, "nested": [private], "score": 91}) == {
        "nested": [{}], "score": 91,
    }


def test_short_and_empty_sensitive_values_do_not_escape_redaction():
    assert strip_internal_fields({"iban": "", "email": "abc", "wallet_address": "12345"}) == {
        "iban": "****", "email": "****", "wallet_address": "****",
    }
