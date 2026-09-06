# LimitGuard MCP Server

Trust Intelligence for AI agents. Entity verification, sanctions screening, and risk scoring via the [Model Context Protocol](https://modelcontextprotocol.io/).

**Server URL:** `https://api.limitguard.ai/mcp`
**Transport:** Streamable HTTP (POST)
**Auth:** API key (Bearer), plus an x402 micropayment per call on the free tier

## Tools

`tools/list` is public — connect and read it without any credential. These are
the names it returns, and the names `tools/call` accepts:

| Tool | Description | Inputs |
|------|-------------|--------|
| `check_entity` | Full entity trust check — KVK/CBE registry, sanctions, domain, risk scoring | `entity_name` (required), `country` (required), `kvk_number`, `domain` |
| `check_agent` | Verify AI agent identity and reputation before inter-agent transactions | `agent_id` (required), `agent_name` (required) |
| `get_trust_score` | Get entity trust score (0-100) with cluster assignment and recommendation | `entity_id` (required) |
| `verify_wallet` | Verify blockchain wallet address, on-chain activity and risk flags | `wallet_address` (required), `chain_id` |
| `get_risk_score` | Quick risk score for entity name + country pair | `entity_name` (required), `country` (required) |

## Pricing

All tools are priced via [x402](https://www.x402.org/) micropayments (USDC on Base or Solana):

| Endpoint | Price |
|----------|-------|
| Entity Check | $0.85 |
| Risk Score | $0.65 |
| Check Agent | $0.10 |
| Trust Score | $0.10 |
| Verify Wallet | $0.10 |

## Authentication

Two things gate a `tools/call`, in this order:

1. **An API key**, as `Authorization: Bearer <key>`. Without one every call comes
   back `Authentication required. Provide API key via Authorization: Bearer
   <lg_live_...> header.` Get a free one — no payment, no card:

   ```bash
   curl -X POST https://api.limitguard.ai/v1/keys/create \
     -H "Content-Type: application/json" \
     -d '{"email": "you@example.com", "tier": "sandbox"}'
   ```

2. **Payment, on the free and sandbox tiers only.** Send the x402 proof as
   `PAYMENT-SIGNATURE` (x402 v2) or `X-PAYMENT` (v1), alongside the Bearer key.
   A paid subscription (indie and up) covers usage and needs no per-call payment.

   A sandbox key does *not* lift the payment requirement on this transport. It
   does on the REST mirrors under `/v1/mcp/*` (sent as `X-API-Key`, not Bearer),
   which is the cheapest way to try the tools before wiring up payment.

## Quick Start

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "limitguard": {
      "type": "url",
      "url": "https://api.limitguard.ai/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LIMITGUARD_KEY"
      }
    }
  }
}
```

### Cursor

Add to MCP settings:

```json
{
  "limitguard": {
    "type": "url",
    "url": "https://api.limitguard.ai/mcp",
    "headers": {
      "Authorization": "Bearer YOUR_LIMITGUARD_KEY"
    }
  }
}
```

### Smithery

```bash
npx -y @smithery/cli install @limitguard/trust-intelligence
```

### Any MCP Client

Connect to `https://api.limitguard.ai/mcp` using Streamable HTTP transport (POST),
sending `Authorization: Bearer <key>` on every `tools/call`.

## Discovery Endpoints

| Endpoint | URL |
|----------|-----|
| MCP Tools | [/.well-known/mcp.json](https://api.limitguard.ai/.well-known/mcp.json) |
| x402 Pricing | [/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json) |
| Health | [/health](https://api.limitguard.ai/health) |

## Use Cases

- **KYC/KYB Automation** — AI agents verify business entities before transactions
- **Sanctions Screening** — Check entities against OpenSanctions watchlists
- **Agent-to-Agent Trust** — Verify counterparty agent reputation before collaboration
- **Wallet Verification** — Check blockchain wallet risk before on-chain transactions
- **Due Diligence** — Automated entity research with trust scoring

## Security

- HTTPS with TLS 1.3
- x402 payment protocol for per-call billing (no stored payment credentials)
- GDPR-compliant (EU-hosted, data minimization)
- All tools are read-only (no data modification)
- Rate limited per payment (abuse-proof)

## Links

- **Website:** [limitguard.ai](https://limitguard.ai)
- **Status:** [status.limitguard.ai](https://status.limitguard.ai)
- **MCP Registry:** [ai.limitguard.api/trust-intelligence](https://registry.modelcontextprotocol.io/servers/ai.limitguard.api/trust-intelligence)

## License

MIT
