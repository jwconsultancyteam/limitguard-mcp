"""Output privacy policy shared with the remote MCP transport.

Ported from limitguard-ai apps/api/mcp_server/guardrails.py at
49877230dd08c2783938c3a8941311555cc1d275. Keep the field policy and
redaction behavior aligned when updating the remote MCP tools.
"""

BLOCKED_FIELDS = frozenset({
    "api_key",
    "api_key_id",
    "api_secret",
    "internal_score",
    "internal_id",
    "debug",
    "trace_id",
    "correlation_id",
    "stack_trace",
    "raw_query",
    "sql",
    "redis_key",
    "tenant_id",
    "session_token",
    "password",
    "secret",
})


REDACT_FIELDS = frozenset({
    "wallet_address",
    "iban",
    "email",
})


SANCTIONS_PII_FIELDS = frozenset({
    "entity_name",
    "entity_hash",
    "match_details",
    "matched_name",
    "matched_entity",
    "alias",
    "aliases",
    "birth_date",
    "national_id",
    "address",
    "nationality",
})


def sanitize_sanctions_data(response: dict) -> dict:
    """Strip PII fields from sanctions screening data in MCP responses.

    DYN-509: Sanctions data may contain natural-person PII. This function
    removes those fields before the response crosses the trust boundary to
    third-party LLM providers.

    Specific rules:
    - Fields in SANCTIONS_PII_FIELDS are removed entirely.
    - "datasets": keep only dataset name strings, not entity details.
    - "sanctions_match": keep only the boolean flag.
    - "match_score": keep the numeric score only.

    Args:
        response: Response dict that may contain sanctions data.

    Returns:
        Response dict with sanctions PII stripped.
    """
    if not isinstance(response, dict):
        return response

    sanitized = {}
    for key, value in response.items():
        # Strip PII fields outright
        if key in SANCTIONS_PII_FIELDS:
            continue

        # Keep only boolean flag for sanctions_match
        if key == "sanctions_match":
            sanitized[key] = bool(value)
            continue

        # Keep only numeric score for match_score
        if key == "match_score":
            sanitized[key] = float(value) if value is not None else None
            continue

        # Flatten datasets to name strings only
        if key == "datasets":
            if isinstance(value, list):
                sanitized[key] = [
                    item["name"] if isinstance(item, dict) and "name" in item else str(item)
                    for item in value
                ]
            else:
                sanitized[key] = value
            continue

        # Recurse into nested dicts
        if isinstance(value, dict):
            sanitized[key] = sanitize_sanctions_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_sanctions_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def strip_internal_fields(response: dict) -> dict:
    """Remove blocked fields and redact sensitive values from MCP response.

    Applies BLOCKED_FIELDS removal, REDACT_FIELDS masking, and (DYN-509)
    sanctions PII sanitization before returning the response.

    Args:
        response: Raw tool response dict

    Returns:
        Sanitized response dict safe for external consumption
    """
    if not isinstance(response, dict):
        return response

    sanitized = {}
    for key, value in response.items():
        if key in BLOCKED_FIELDS:
            continue

        if key in REDACT_FIELDS and isinstance(value, str):
            sanitized[key] = _redact_value(key, value)
        elif isinstance(value, dict):
            sanitized[key] = strip_internal_fields(value)
        elif isinstance(value, list):
            sanitized[key] = [
                strip_internal_fields(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value

    # DYN-509: Remove sanctions PII before response crosses LLM trust boundary
    return sanitize_sanctions_data(sanitized)


def _redact_value(field_name: str, value: str) -> str:
    """Redact a sensitive field value for external output."""
    if not value or len(value) < 6:
        return "****"

    if field_name == "wallet_address":
        return value[:6] + "..." + value[-4:]
    if field_name == "iban":
        return value[:2] + "****" + value[-4:]
    if field_name == "email":
        if "@" in value:
            local, domain = value.rsplit("@", 1)
            return local[0] + "***@" + domain
        return "****"

    return value[:2] + "****"
