# Limitguard MCP server: installation

Free sandbox key, no wallet. The sandbox covers entity, risk and KYB checks; Lead Verify and the agent check need a live key or an x402 payment. Lead Verify $0.27 per lead and agent check $0.75 per wallet; $0.11-1.85 per call; entity and risk checks $0.88-1.05 fresh ($1.50 KYB), $0.11 cached ($0.25 KYB) when available.

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

- `check_entity`: Company check on a business: sanctions screening and country risk, the Dutch KVK register for an NL company, and the website domain when you send it. Returns a 0-100 score, a risk level and a recommendation.
- `get_trust_score`: Look up your own most recent trust score for an entity you checked before, from your stored checks: score, level, when, which product, trend and how many checks are on record. Runs no new check and calls no data source. Free ($0).
- `verify_wallet`: Screen a wallet: OFAC SDN address match, on-chain signals (contract check, native and USDC balance, transaction count, first seen on Base) and named risk rules with up to 3 advice items. On Base, also reports any ERC-8004 agent the wallet owns and its open on-chain reputation as descriptive signals, never scored. Free ($0). Supports EVM and Solana addresses.
- `get_risk_score`: Quick risk score from sanctions screening and country risk only, without the register or domain lookups of check_entity.
- `get_compliance_report`: Per-entity report built from one real check: registry identity, sanctions and PEP screens, domain signals, risk score with the rules that fired, correlations, every finding as a ranked action, a per-source status table (ok / unavailable / error) and a report hash.
- `sanctions_preview`: Free yes/no sanctions preview against the local OFAC SDN, EU and UN lists. Returns possible_match, lists_checked and list_dates only, never an entry. 10 per caller per UTC day.
- `sanctions_screen`: Sanctions screen against the local OFAC SDN, EU and UN lists: matched entries with list, entry id, programmes, countries, listing date and match score. A name match is not a determination.
- `check_agent_wallet`: Check a counterparty agent's EVM wallet in one call: OFAC SDN digital-currency address list match, Base USDC and ETH balance, ERC-8004 identity registration (and, given an agent id, that agent's owner and payment wallet) and open ERC-8004 feedback, which is not scored. $0.75.
- `verify_lead`: Verify a NL/BE sales lead against the registers in one call: real and active, VAT, mail server, IBAN, sanctions; a 0-100 lead score. $0.27.
