# LimitGuard MCP Server

Trust Intelligence for AI agents. Entity verification, sanctions screening, and risk scoring via the [Model Context Protocol](https://modelcontextprotocol.io/).

**Server URL:** `https://api.limitguard.ai/mcp`
**Transport:** Streamable HTTP (POST)
**Auth:** x402 micropayment protocol (pay-per-call, no API key needed)

## Tools

| Tool | Description | Inputs |
|------|-------------|--------|
| `check_entity` | Full entity trust check — KVK/CBE registry, sanctions, domain, risk scoring | `entity_name` (required), `country` (required), `kvk_number`, `domain` |
| `check_agent` | Verify AI agent identity and reputation before inter-agent transactions | `agent_id` (required), `agent_name` (required) |
| `trust_score` | Get entity trust score (0-100) with cluster assignment and recommendation | `entity_id` (required) |
| `verify_wallet` | Verify blockchain wallet address, on-chain activity and risk flags | `wallet_address` (required), `chain_id` |
| `risk_score` | Quick risk score for entity name + country pair | `entity_name` (required), `country` (required) |

## Pricing

All tools are priced via [x402](https://www.x402.org/) micropayments (USDC on Base or Solana):

| Endpoint | Price |
|----------|-------|
| Entity Check | $0.85 |
| Risk Score | $0.65 |
| Check Agent | $0.10 |
| Trust Score | $0.10 |
| Verify Wallet | $0.10 |

No API key, no subscription. Your AI agent pays per call with USDC.

## Full REST API (x402 direct)

The 5 tools above are what the MCP server exposes over the Model Context Protocol. Clients that
integrate directly over HTTP — instead of through an MCP client — can reach 13 further x402-priced
REST endpoints on `https://api.limitguard.ai`. These are **not** MCP tools and are not listed by
`/.well-known/mcp.json`; they are published in [/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json)
alongside the MCP tools' own `/v1/mcp/*` paths.

Payment works the same way: USDC on Base or Solana, pay-per-call, no API key required.

### Trust intelligence

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/entity/check` | POST | $0.85 | Full entity trust check across every verification layer — KVK/CBE registry, OpenSanctions, country risk (CPI/FATF), domain WHOIS, IBAN validation, EU VAT/VIES, wallet screening, and x402 payment history. Returns trust score 0-100 with cluster and recommendation. |
| `/v1/risk/score` | POST | $0.65 | Quick risk score (0-100) for entity name + country. Lightweight check without the full data source scan. |

### Reputation management

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/reputation/score` | POST | $0.65 | Reputation scoring with Bayesian trust decay. Tracks entity trust over time with confidence intervals. |
| `/v1/reputation/history/{id}` | GET | $0.10 | Reputation history for an entity. |

### Wallet services

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/wallet/balance` | GET | $0.10 | ERC-8004 agent wallet balance — USDC balance and transaction count for AI agent wallets. |

### Regulatory compliance

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/kyb/check` | POST | $1.50 | Know Your Business verification — company registration, sanctions screening, VAT/VIES, and domain analysis in one call. |
| `/v1/compliance/alerts` | GET | $0.10 | EU regulatory change alerts filtered by jurisdiction and severity. Covers GDPR, EU AI Act, MiCA, and AMLD6. |
| `/v1/compliance/report/{id}` | GET | $0.50 | Compliance report for an entity. |
| `/v1/compliance/readiness/{id}` | GET | $0.10 | Compliance readiness check for an entity. |

### API key tiers

One-time x402 payment upgrades an API key to a monthly call allowance.

| Endpoint | Method | Price | Tier | Allowance |
|----------|--------|-------|------|-----------|
| `/v1/keys/upgrade/indie` | GET | $29 | Indie | 1,000 calls/mo |
| `/v1/keys/upgrade/starter` | GET | $99 | Starter | 10,000 calls/mo |
| `/v1/keys/upgrade/growth` | GET | $299 | Growth | 50,000 calls/mo |
| `/v1/keys/upgrade/pro` | GET | $999 | Pro | 250,000 calls/mo |

Prices and descriptions above mirror the live x402 manifest as of 2026-09-05. The manifest is the
source of truth — fetch it if you need the current schema for any endpoint.

## Quick Start

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "limitguard": {
      "type": "url",
      "url": "https://api.limitguard.ai/mcp"
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
    "url": "https://api.limitguard.ai/mcp"
  }
}
```

### Smithery

```bash
npx -y @smithery/cli install @limitguard/trust-intelligence
```

### Any MCP Client

Connect to `https://api.limitguard.ai/mcp` using Streamable HTTP transport (POST).

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
- x402 payment protocol (no stored credentials)
- GDPR-compliant (EU-hosted, data minimization)
- All tools are read-only (no data modification)
- Rate limited per payment (abuse-proof)

## Links

- **Website:** [limitguard.ai](https://limitguard.ai)
- **Status:** [status.limitguard.ai](https://status.limitguard.ai)
- **MCP Registry:** [ai.limitguard.api/trust-intelligence](https://registry.modelcontextprotocol.io/servers/ai.limitguard.api/trust-intelligence)

## License

MIT
