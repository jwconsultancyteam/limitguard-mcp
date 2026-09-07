# LimitGuard MCP Server

Trust Intelligence for AI agents. Entity verification, sanctions screening, and risk scoring via the [Model Context Protocol](https://modelcontextprotocol.io/).

**Server URL:** `https://api.limitguard.ai/mcp`
**Transport:** Streamable HTTP (POST)
**Auth:** API key (Bearer), plus an x402 micropayment per call on the free and sandbox tiers

## Tools

`tools/list` is public — connect and read it without any credential. These are
the names it returns, and the names `tools/call` accepts:

| Tool | Description | Inputs |
|------|-------------|--------|
| `check_entity` | Full trust intelligence check on a business entity. Returns trust score (0-100), risk level, and recommendation. | `entity_name` (required), `country` (required), `kvk_number`, `domain` |
| `check_agent` | Verify AI agent trust. Checks if an AI agent is trusted based on its identifier. | `agent_id` (required), `agent_name` (required) |
| `get_trust_score` | Quick trust score lookup by entity ID. Returns cached score if available. | `entity_id` (required) |
| `verify_wallet` | Check wallet trust score for crypto payments. Supports EVM and Solana addresses. | `wallet_address` (required), `chain_id` |
| `get_risk_score` | Quick risk assessment without full trust check. Focuses on risk signals only. | `entity_name` (required), `country` (required) |

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
     -d '{"email": "you@example.com"}'
   ```

   That returns a `free`-tier key, which is the key the Quick Start configs below
   expect. Asking for `"tier": "sandbox"` instead returns a key that answers with
   mock data — see the next point before you use one here.

2. **Payment, on the free and sandbox tiers only.** Send the x402 proof as
   `PAYMENT-SIGNATURE` (x402 v2) or `X-PAYMENT` (v1), alongside the Bearer key.
   A paid subscription (indie and up) covers usage and needs no per-call payment.

   A sandbox key does *not* lift the payment requirement on this transport: it
   owes x402 per call exactly as a `free` key does, and it answers with mock
   data rather than a real check. Paying for one over MCP spends real USDC on a
   mock answer. Where a sandbox key is worth having is the REST mirrors under
   `/v1/mcp/*` (sent as `X-API-Key`, not Bearer), which serve the mock response
   before the payment check — a way to exercise the request and response shapes,
   not a cheap source of real checks.

## Full x402 API (direct HTTP)

The 5 tools above are what the MCP server exposes over the Model Context Protocol. Clients that
integrate directly over HTTP — instead of through an MCP client — can reach 18 x402-priced
endpoints on `https://api.limitguard.ai`: the 13 REST endpoints below, plus the MCP tools' own
`/v1/mcp/*` paths. All 18 are published in
[/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json); only the 5 tools above
are listed by `/.well-known/mcp.json`.

Most of the REST endpoints are capabilities the MCP tools do not expose, but two are the same
check reached over plain HTTP: `/v1/entity/check` behind `check_entity` — the manifest describes
`/v1/mcp/check-entity` as "same as `/v1/entity/check` with MCP-native interface" — and
`/v1/risk/score` behind `get_risk_score`, at the same $0.65.

Payment works the same way throughout: USDC on Base or Solana, pay-per-call. The 9 data endpoints
below need no API key at all. The 4 `/v1/keys/upgrade/*` endpoints also take payment without one,
but they act on an API key you already hold — see [API key tiers](#api-key-tiers).

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

### MCP tool paths (direct HTTP)

The 5 MCP tools are also reachable over plain HTTP at their own x402-priced paths — same
capabilities and prices as the Tools table above, for clients that pay per call without opening an
MCP session.

| Endpoint | Method | Price | MCP tool |
|----------|--------|-------|----------|
| `/v1/mcp/check-entity` | POST | $0.85 | `check_entity` |
| `/v1/mcp/check-agent` | POST | $0.10 | `check_agent` |
| `/v1/mcp/trust-score` | POST | $0.10 | `get_trust_score` |
| `/v1/mcp/verify-wallet` | GET | $0.10 | `verify_wallet` |
| `/v1/mcp/risk-score` | POST | $0.65 | `get_risk_score` |

### API key tiers

LimitGuard accepts two forms of payment: x402 per call, or a **paid-tier** API key whose
subscription prepays the calls. Paying per call needs no API key on 13 of the 18 endpoints — the
9 data endpoints above and the 4 `/v1/keys/upgrade/*` paths. The other 5 always want a key: the
MCP transport takes `Authorization: Bearer` on every `tools/call`, and its `/v1/mcp/*` mirrors
take `X-API-Key`.

A base key is free and self-service: `POST /v1/keys/create` with an email address, no payment and
no existing key needed. It identifies you and tracks your usage; it does **not** pay for calls. A
`free`-tier key still owes x402 on every paid endpoint, on REST exactly as on MCP. The
`monthly_limit` it reports is a ceiling on how many calls it may make, not an allowance of free
ones. A `sandbox` key is also free and returns mock data, never a real check — over MCP it owes
x402 like any other free key, so it earns its keep only against the REST mirrors.

The endpoints below take an x402 payment to move a key onto a paid tier, which is what lifts the
per-call charge. On a paid tier `monthly_limit` is the number of calls the subscription covers.
The manifest prices the upgrade call itself and says nothing about what happens at the end of a
month, so confirm the renewal terms before budgeting against the figures below.

| Endpoint | Method | Price | Tier | `monthly_limit` |
|----------|--------|-------|------|-----------------|
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
| MCP server card | [/.well-known/mcp/server-card.json](https://api.limitguard.ai/.well-known/mcp/server-card.json) |
| MCP Tools | [/.well-known/mcp.json](https://api.limitguard.ai/.well-known/mcp.json) |
| x402 Pricing | [/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json) |
| Health | [/health](https://api.limitguard.ai/health) |

The service publishes two tool cards, and they do not agree. Both list the same five
tools, taking the same required arguments, so a `tools/call` written against either one
works — but the descriptions and the argument wording differ between them. The Tools
table above and this repository's `server.json` are generated from the **server card**,
which is the one to read when the two disagree. Reconciling them is the service's to fix.

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
