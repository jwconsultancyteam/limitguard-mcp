<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.svg">
  <img src="assets/logo-light.svg" alt="Limitguard" width="220">
</picture>

# Limitguard MCP Server

[![Limitguard MCP server: quality and maintenance score on Glama](https://glama.ai/mcp/servers/jwconsultancyteam/limitguard-mcp/badges/card.svg)](https://glama.ai/mcp/servers/jwconsultancyteam/limitguard-mcp)
[![Listed on MCP Market](https://mcpmarket.com/badge/server/limitguard.svg)](https://mcpmarket.com/server/limitguard?utm_source=readme&utm_medium=badge)

Check Dutch and Belgian companies, sales leads and crypto wallets before you deal with them, over the [Model Context Protocol](https://modelcontextprotocol.io/): the KVK (Netherlands) and KBO (Belgium) registers, EU VAT (VIES), the OFAC, EU and UN sanctions lists and wallet risk on Base and Solana, with the source and date of every answer.

**Server URL:** `https://api.limitguard.ai/mcp`
**Transport:** Streamable HTTP (POST)
**Auth:** API key (Bearer), plus an x402 micropayment per call on the free and sandbox tiers

**What it is:** Limitguard is a lead validation service for lead generation agencies, B2B marketing and sales teams: it checks the company behind each lead against official business registers (full coverage in the Netherlands and Belgium), EU VAT and sanctions lists, with website age in the company check, and returns proceed, review or block with the source on every line. Developers and AI agents can use its HTTP API, MCP server and A2A service, hosted in the EU.

**Start here:** On MCP a paid tool takes an x402 payment per call, or debits prepaid credit (a paid key, or a funded workspace); wallet_sanctions_preview, sanctions_preview and get_trust_score are free; the free sandbox key returns mock data on the REST API only, not on MCP. Lead Verify $0.27 per lead and agent check $0.75 per wallet; $0.11-1.85 per call; entity and risk checks $0.88-1.05 fresh ($1.50 KYB), $0.11 cached ($0.25 KYB) when available.

## Features

- **Lead verify** for Dutch and Belgian sales leads: is it a real, active company? A verdict, a 0-100 lead score and one action per flag ($0.27).
- **Company check** against the KVK and KBO registers, EU VAT (VIES), the domain and the IBAN, with a 0-100 score and a recommendation.
- **Sanctions screen** of company and person names against the OFAC, EU and UN lists, with a free yes/no preview.
- **Crypto wallet screen** on Base and Solana: OFAC address match, balances, wallet age, recent activity and risk rules with advice ($0.11).
- **Free wallet sanctions check**: a yes/no against the OFAC list.
- **AI agent wallet check** before your agent pays: sanctions, balance, ERC-8004 identity and public reputation ($0.75).
- **Pay per call** in USDC on Base or Solana with x402, or with an API key and prepaid credit. A check that fails is not charged.
- **MCP, REST and A2A**, and agents can pay inside A2A with x402.
- **Sources on every answer**, with the date each one was read. Hosted in the EU.

## Tools

`tools/list` is public: connect and read it without any credential. These are
the names it returns, and the names `tools/call` accepts:

| Tool | Description | Inputs |
|------|-------------|--------|
| `check_entity` | Company check on a business: sanctions screening and country risk, the Dutch KVK register for an NL company, and the website domain when you send it. Returns trust_score (0-100, 100 = best), trust_level (high means low risk), cluster, recommendation, confidence, top_factors and sources_checked. | `entity_name` (required), `country` (required), `kvk_number`, `domain` |
| `get_trust_score` | Look up your own most recent trust score for an entity you checked before, from your stored checks: score, level, when, which product, trend and how many checks are on record. Runs no new check and calls no data source. Free ($0). | `entity_id` (required) |
| `verify_wallet` | Screen a wallet: OFAC SDN address match, on-chain signals (contract check, native and USDC balance, transaction count, first seen on Base) and named risk rules with up to 3 advice items. On Base, also reports any ERC-8004 agent the wallet owns and its open on-chain reputation as descriptive signals, never scored. $0.11. Supports EVM and Solana addresses. | `wallet_address` (required), `chain_id` |
| `get_risk_score` | Quick risk score from sanctions screening and country risk only, without the register or domain lookups of check_entity. Returns risk_score (0-100, 100 = riskiest), risk_level (high means high risk, the reverse of check_entity's trust_level), sanctions_match and fatf_status; no recommendation or factors. | `entity_name` (required), `country` (required) |
| `get_compliance_report` | Per-entity report built from one real check: registry identity, sanctions and PEP screens, domain signals, risk score with the rules that fired, correlations, every finding as a ranked action, a per-source status table (ok / unavailable / error) and a report hash. | `entity_name`, `country`, `kvk_number`, `cbe_number`, `vat_number`, `domain`, `iban`, `wallet_address`, `wallet_chain`, `check_id` |
| `sanctions_preview` | Free yes/no sanctions preview against the local OFAC SDN, EU and UN lists. Returns possible_match, lists_checked, list_dates and list_note only, never an entry. 10 per caller per UTC day. | `name` (required), `country` |
| `wallet_sanctions_preview` | Free yes/no check of a wallet address against the OFAC SDN list: sanctioned, lists, the list date and its freshness, no programmes or entry ids. 10 per caller per UTC day, separate from sanctions_preview. The full wallet screen is verify_wallet ($0.11). | `wallet_address` (required), `chain_id` |
| `sanctions_screen` | Sanctions screen against the local OFAC SDN, EU and UN lists: matched entries with list, entry id, programmes, countries, listing date and match score. A name match is not a determination. | `name` (required), `country` |
| `check_agent_wallet` | Check a counterparty agent's EVM wallet in one call: OFAC SDN digital-currency address list match, Base USDC and ETH balance, ERC-8004 identity registration (and, given an agent id, that agent's owner and payment wallet) and open ERC-8004 feedback, which is not scored. $0.75. | `wallet` (required), `agent_id`, `domain` |
| `verify_lead` | Verify a NL/BE sales lead against the registers in one call: real and active, VAT, mail server, IBAN, sanctions; a 0-100 lead score. $0.27. | `country` (required), `company_number`, `name`, `vat_number`, `email`, `domain`, `address`, `iban`, `phone`, `target_industries`, `target_size` |

## Pricing

A paid tool call is debited from your API key's prepaid balance, or paid per call with an
[x402](https://www.x402.org/) micropayment (USDC on Base or Solana). The tools with their own
`/v1/mcp/*` path are priced below; the other tools are priced at the REST endpoint they call,
in [Full x402 API](#full-x402-api-direct-http).

| Endpoint | Price |
|----------|-------|
| Entity Check (`/v1/mcp/check-entity`) | $1.05 |
| Risk Score (`/v1/mcp/risk-score`) | $0.90 |
| Check Agent (`/v1/mcp/check-agent`) | $0.00: hidden placeholder, not in `tools/list`; returns placeholder data |
| Trust Score (`/v1/mcp/trust-score`) | $0.00, free (your own stored score) |
| Verify Wallet (`/v1/mcp/verify-wallet`) | $0.11 |

## Authentication

Two things gate a `tools/call`, in this order:

1. **An API key**, as `Authorization: Bearer <key>`. Without one every call comes
   back `Authentication required. Provide API key via Authorization: Bearer
   <lg_live_...> header.` Get a free one (no payment, no card):

   ```bash
   curl -X POST https://api.limitguard.ai/v1/keys/create \
     -H "Content-Type: application/json" \
     -d '{"email": "you@example.com"}'
   ```

   That returns a `free`-tier key, which is the key the Quick Start configs below
   expect. Asking for `"tier": "sandbox"` instead returns a key that answers with
   mock data; see the next point before you use one here.

2. **Payment, on the free and sandbox tiers only.** Send the x402 proof as
   `PAYMENT-SIGNATURE` (x402 v2) or `X-PAYMENT` (v1), alongside the Bearer key.
   A key with a prepaid balance (indie and up) is debited per call instead and
   needs no per-call payment. API keys have no subscription; see
   [API keys and prepaid balance](#api-keys-and-prepaid-balance).

   A sandbox key does *not* lift the payment requirement on this transport: it
   owes x402 per call exactly as a `free` key does, and it answers with mock
   data rather than a real check. Paying for one over MCP spends real USDC on a
   mock answer. Where a sandbox key is worth having is the REST mirrors under
   `/v1/mcp/*` (sent as `X-API-Key`, not Bearer), which serve the mock response
   before the payment check: a way to exercise the request and response shapes,
   not a cheap source of real checks.

## Full x402 API (direct HTTP)

The tools above are what the MCP server exposes over the Model Context Protocol. Clients that
integrate directly over HTTP, instead of through an MCP client, can reach every x402-priced
endpoint on `https://api.limitguard.ai`: the REST endpoints below, plus the MCP tools' own
`/v1/mcp/*` paths. All of them are published in
[/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json); `/.well-known/mcp.json`
lists only the tools above.

Most of the REST endpoints are capabilities the MCP tools do not expose, but two run the same
engine over plain HTTP: `/v1/entity/check` behind `check_entity` (the MCP tool takes the entity
name, country, KVK number and domain only, so no IBAN or VAT), and `/v1/risk/score` behind
`get_risk_score`, at the same price.

Payment works the same way throughout: USDC on Base or Solana, pay-per-call. The data endpoints below need no API key at all. The `/v1/keys/upgrade/*` endpoints also take payment without one,
but they act on an API key you already hold; see [API keys and prepaid balance](#api-keys-and-prepaid-balance).

### Lead and company checks

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/leads/verify` | POST | $0.27 | Lead verify for one NL or BE sales lead: is it a real, active company? Checks the KVK or KBO register and cross-checks what the lead holds: VAT with VIES, mail server and disposable domain, IBAN country and bank (not the holder), and the company name against the OFAC, EU and UN sanctions lists. Returns a verdict, a 0-100 lead score and flags, each with one action. An input not given is not checked. |
| `/v1/agent/check` | POST | $0.75 | Agent wallet check in one call: screens an EVM wallet against the OFAC SDN digital-currency address list, reads its Base USDC and ETH balance, looks up its ERC-8004 identity registration (and, given an agent id, that agent's owner and payment wallet) and lists open ERC-8004 feedback, which is not scored. Returns one verdict and each part's status; a part that could not be read says so. |
| `/v1/sanctions/screen` | POST | $0.11 | Sanctions screen of a company or person name against the OFAC SDN, EU and UN sanctions lists, held locally and refreshed daily. Returns each matched entry: list, entry id, matched name, programmes, countries, listing date and match score. Exact normalised or word-order-insensitive name match only; a name match is not a determination. |
| `/v1/entity/check` | POST | $1.05 | Full entity trust check across multiple verification layers: KVK/CBE registry, OpenSanctions, country risk (CPI/FATF), domain WHOIS, IBAN validation and EU VAT/VIES. Returns trust score 0-100 with cluster and recommendation. |
| `/v1/risk/score` | POST | $0.90 | Quick risk score (0-100) for entity name + country. Lightweight check without full data source scan. |
| `/v1/entity/deep-check` | POST | $0.88 | Extended screening in two tiers. fresh ($0.88): PEP and relative/close-associate matches from OpenSanctions, plus a Dutch insolvency register screen (NL only). enhanced ($1.71): the same plus adverse media screening. If a tier's source cannot be reached the call returns 503 and is not charged. |
| `/v1/reports/entity` | POST | $1.85 | Per-entity report built from one real check's signals: identity, sanctions and PEP screening, domain signals, trust score (risk.trust_score, 0-100, 100 = best), correlations with the caller's earlier reports, sources and an evidence hash. A source that did not answer is shown unavailable, never clean. |

### Reputation management

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/reputation/score` | POST | $0.90 | Reputation scoring with linear trust decay: after its first week a score loses 2-5 points a week by risk cluster (none for a sanctions-flagged entity), plus a bonus of up to 5 points for repeat verifications. |
| `/v1/reputation/history/{id}` | GET | $0.11 | Historical reputation trend data. Returns the trust score timeline with the decay applied at each point and an overall trend. |

### Wallet services

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/wallet/balance` | GET | $0.11 | ERC-8004 agent wallet balance check. Returns the on-chain USDC balance (Base mainnet) for a registered ERC-8004 agent wallet. |

### Regulatory compliance

| Endpoint | Method | Price | Description |
|----------|--------|-------|-------------|
| `/v1/kyb/check` | POST | $1.50 | Know Your Business verification: company registration, sanctions screening, VAT/VIES, and domain analysis in one call. |
| `/v1/compliance/alerts` | GET | $0.11 | Daily changes to the OFAC, EU and UN sanctions lists, plus alerts when an entity or wallet this key checked is listed. Poll this route; alerts about entities or wallets this key checked are also sent to a webhook registered for sanctions.match.new (POST /v1/webhooks). Filter by jurisdiction and severity. |
| `/v1/compliance/readiness/{id}` | GET | $0.11 | EU AI Act readiness self-assessment for one AI system. Send the system_type and the checklist items you have completed (completed_items); returns the EU AI Act risk level for that system type, a readiness score and the open gaps. entity_id is your label: nothing is looked up about it. |

### MCP tool paths (direct HTTP)

The MCP tools that mirror a REST check are also reachable over plain HTTP at their own
x402-priced `/v1/mcp/*` paths, with the same capabilities and prices as the Tools table above,
for clients that pay per call without opening an MCP session. The other tools call one of the
REST endpoints above directly.

| Endpoint | Method | Price | MCP tool |
|----------|--------|-------|----------|
| `/v1/mcp/check-entity` | POST | $1.05 | `check_entity` |
| `/v1/mcp/check-agent` | POST | $0.00 | `check_agent` |
| `/v1/mcp/trust-score` | POST | $0.00 | `get_trust_score` |
| `/v1/mcp/verify-wallet` | POST | $0.11 | `verify_wallet` |
| `/v1/mcp/risk-score` | POST | $0.90 | `get_risk_score` |

### API keys and prepaid balance

Limitguard accepts two forms of payment: x402 per call, or an API key with a **prepaid balance**
that each priced call is debited from. API keys and x402 have no subscription (the Limitguard dashboard also has optional monthly plans, paid in euros). Paying per call needs no API key on the data endpoints above or the `/v1/keys/upgrade/*` paths.
The MCP transport always wants one: it takes `Authorization: Bearer` on every `tools/call`, and
its `/v1/mcp/*` mirrors take `X-API-Key`.

A base key is free and self-service: `POST /v1/keys/create` with an email address, no payment and
no existing key needed. It identifies you and tracks your usage; it does **not** pay for calls. A
`free`-tier key holds no balance and still owes x402 on every paid endpoint, on REST exactly as on
MCP. The `monthly_limit` it reports is a ceiling on how many calls it may make, not an allowance of
free ones. A `sandbox` key is also free and returns mock data, never a real check. Over MCP it owes
x402 like any other free key, so it earns its keep only against the REST mirrors.

The endpoints below take an x402 payment, credit the same amount 1:1 to the prepaid balance of a
key you already hold, and set its tier label. Each priced call is then debited from that balance
at the prices above, with no per-call x402 payment. When the balance is too low for a call, that
call answers 402 with an x402 quote and the top-up path, and `POST /v1/keys/topup/{usd}`
adds any whole-dollar amount from $5. On every tier `monthly_limit` is an abuse limit, not an
allowance of included calls.

| Endpoint | Method | Price | Tier label | `monthly_limit` (abuse limit) |
|----------|--------|-------|------------|-------------------------------|
| `/v1/keys/upgrade/indie` | POST | $29 | Indie | 1,000 calls/mo |
| `/v1/keys/upgrade/starter` | POST | $99 | Starter | 10,000 calls/mo |
| `/v1/keys/upgrade/growth` | POST | $299 | Growth | 50,000 calls/mo |
| `/v1/keys/upgrade/pro` | POST | $999 | Pro | 250,000 calls/mo |

Prices and descriptions above are generated from the service and were last checked against the
live x402 manifest on 2026-10-06. The manifest is the source of truth: fetch it if you need the
current schema for any endpoint.

## Quick Start

### Claude (Desktop and claude.ai)

This is a remote server, so it is added as a custom connector, not in
`claude_desktop_config.json` (that file is for local servers only):

1. Open **Customize > Connectors**, then **+ Add > Add custom connector**.
   On a Team or Enterprise plan an owner adds it under **Organization settings > Connectors**.
2. URL: `https://api.limitguard.ai/mcp`
3. Under **Request headers**, add `Authorization` with the value `Bearer YOUR_LIMITGUARD_KEY`.

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
npx -y @smithery/cli install team-mehs/limitguard
```

### Any MCP Client

Connect to `https://api.limitguard.ai/mcp` using Streamable HTTP transport (POST),
sending `Authorization: Bearer <key>` on every `tools/call`.

### Run locally (stdio)

For a client that only runs local servers, this repository also ships a stdio server
with the same tools. Each tool calls the Limitguard REST API with your key, so a paid
call is debited from the key's prepaid balance; paying per call with x402 needs the
remote server above.

```bash
uvx --from git+https://github.com/jwconsultancyteam/limitguard-mcp limitguard-mcp
```

```json
{
  "mcpServers": {
    "limitguard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/jwconsultancyteam/limitguard-mcp", "limitguard-mcp"],
      "env": { "LIMITGUARD_API_KEY": "YOUR_LIMITGUARD_KEY" }
    }
  }
}
```

Or in a container: `docker build -t limitguard-mcp .` then
`docker run -i --rm -e LIMITGUARD_API_KEY limitguard-mcp`.

## Agent skill

[`skills/verifying-sales-leads`](skills/verifying-sales-leads/SKILL.md) is an [Agent Skill](https://agentskills.io) that teaches an agent when to call which tool, the cheapest order of calls, and how to read a lead verdict. It works with any agent that reads `SKILL.md` files.

- Claude Code (skill plus the MCP server, OAuth sign-in):

  ```
  /plugin marketplace add jwconsultancyteam/limitguard-mcp
  /plugin install limitguard@limitguard
  ```

- Other agents: `npx skills add jwconsultancyteam/limitguard-mcp`, or copy the `skills/verifying-sales-leads` folder into the agent's skills directory.

The tool and price reference in `references/tools.md` is generated from the served server card; do not edit it by hand.

## Discovery Endpoints

| Endpoint | URL |
|----------|-----|
| MCP server card | [/.well-known/mcp/server-card.json](https://api.limitguard.ai/.well-known/mcp/server-card.json) |
| MCP Tools | [/.well-known/mcp.json](https://api.limitguard.ai/.well-known/mcp.json) |
| x402 Pricing | [/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json) |
| Health | [/health](https://api.limitguard.ai/health) |

The service publishes two tool cards, and they do not fully agree. Both list the same
tools, taking the same required arguments, so a `tools/call` written against either one
works, but the descriptions and the argument wording differ between them. The Tools
table above and this repository's `server.json` are generated from the **server card**,
which is the one to read when the two disagree. Reconciling them is the service's to fix.

## Use Cases

- **Lead validation:** check the company behind each lead (KVK or KBO register, EU VAT via VIES, sanctions lists and email domain) before it reaches a client, and get a verdict, a 0-100 lead score and flags (`verify_lead`).
- **Company checks:** developers and AI agents verify a business entity before a deal or a payment (`check_entity`, `get_risk_score`), or build a per-entity report with every source's status (`get_compliance_report`).
- **Sanctions screening:** screen a company or person name against the OFAC, EU and UN lists (`sanctions_preview`, `sanctions_screen`).
- **Agent-to-agent checks:** check a counterparty agent's wallet and ERC-8004 identity before working with it (`check_agent_wallet`).
- **Wallet screening:** screen a wallet address before an on-chain payment (`verify_wallet`).

## Security

- HTTPS with TLS 1.3
- x402 payment protocol for per-call billing (no stored payment credentials)
- Hosted in the EU (API and dashboard in the EU, database in Ireland); data minimisation
- All tools are read-only (no data modification)
- Rate limited per payment (abuse-proof)

## FAQ

**What is Limitguard?**
Limitguard checks the company, sales lead or crypto wallet behind a deal before you call, sign or pay. It reads official sources (the KVK and KBO business registers, EU VAT through VIES, the OFAC, EU and UN sanctions lists and public blockchain data for wallets) and answers with what it found, where and when.

**How is it priced?**
Per check, with no subscription for API keys or x402: lead verify $0.27, company check $1.05 ($0.11 from cache when available), risk score $0.90, KYB check $1.50, sanctions screen $0.11, wallet screen $0.11, agent wallet check $0.75, company report $1.85. Free: the name sanctions preview, the wallet sanctions check and your own stored trust score. A check that fails is not charged. Live prices: [/.well-known/x402.json](https://api.limitguard.ai/.well-known/x402.json).

**How do I connect it to Claude, Cursor or another MCP client?**
Add `https://api.limitguard.ai/mcp` with your API key in the header `Authorization: Bearer lg_live_...` (a free key: see [Authentication](#authentication)). In Claude you can instead add `https://api.limitguard.ai/mcp-oauth` as a custom connector and sign in with your Limitguard account; paid checks are then taken from your workspace credit.

**Can an AI agent pay without an account?**
Yes. Over REST or A2A an unpaid call returns HTTP 402 with the price. The agent signs a USDC payment on Base or Solana (x402), sends it with the call and gets the answer with a receipt. No account or API key is needed.

**Which countries and chains does it cover?**
Full business register coverage for the Netherlands (KVK) and Belgium (KBO), EU VAT numbers through VIES, worldwide sanctions lists (OFAC, EU and UN) and crypto wallets on Base and Solana.

## Links

- **Website:** [limitguard.ai](https://limitguard.ai/?utm_source=mcp_readme&utm_medium=package&utm_campaign=home&utm_content=links)
- **Status:** [status.limitguard.ai](https://status.limitguard.ai)
- **MCP Registry:** [ai.limitguard.api/limitguard](https://registry.modelcontextprotocol.io/v0.1/servers/ai.limitguard.api%2Flimitguard/versions/latest) (JSON; the registry has no HTML page per server)

## License

MIT
