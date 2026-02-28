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
| Trust Score | $0.65 |
| KYB Check | $1.50 |

No API key, no subscription. Your AI agent pays per call with USDC.

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
