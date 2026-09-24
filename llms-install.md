# LimitGuard Trust Intelligence MCP server: installation

Free sandbox key, no wallet. $0.65-0.85 fresh for entity and risk checks ($1.50 KYB); $0.10 cached ($0.25 KYB) when available.

No server process, no npm or Python package: this is a remote Streamable HTTP server.

## 1. Get a free key

```bash
curl -X POST https://api.limitguard.ai/v1/keys/create \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com"}'
```

The response carries a key starting with `lg_live_`.

## 2. Add the server to cline_mcp_settings.json

Replace `YOUR_LIMITGUARD_KEY` with that key; keep the `Bearer ` prefix.

```json
{
  "mcpServers": {
    "limitguard": {
      "type": "streamableHttp",
      "url": "https://api.limitguard.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LIMITGUARD_KEY"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 3. Verify

`tools/list` answers without a key. `tools/call` needs the `Authorization` header;
without it the call is refused with a message saying how to get a key.

## Tools

- `check_entity`: Full trust intelligence check on a business entity. Returns trust score (0-100), risk level, and recommendation.
- `verify_wallet`: Screen a wallet: OFAC SDN address match, on-chain signals (contract check, native and USDC balance, transaction count, first seen on Base) and named risk rules with up to 3 advice items. On Base, also reports any ERC-8004 agent the wallet owns and its open on-chain reputation as descriptive signals, never scored. Free ($0). Supports EVM and Solana addresses.
- `get_risk_score`: Quick risk assessment without full trust check. Focuses on risk signals only.
