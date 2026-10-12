---
name: verifying-sales-leads
description: Verifies Dutch and Belgian B2B sales leads and counterparties with the Limitguard MCP server, checking the KVK and KBO business registers, EU VAT (VIES), the OFAC, EU and UN sanctions lists, the email domain and the IBAN, and screens crypto wallets on Base and Solana. Use when the user wants to know whether a company or lead is real, active and safe to contact, pay or onboard, wants to validate a KVK, KBO or VAT number, wants a name or wallet screened against sanctions lists, or wants a counterparty agent's wallet checked. Requires the Limitguard MCP server.
license: MIT
compatibility: Needs the Limitguard MCP server (https://api.limitguard.ai/mcp with an API key, or https://api.limitguard.ai/mcp-oauth with OAuth sign-in) and network access. Paid tools are charged per call.
metadata:
  author: Limitguard
  homepage: https://limitguard.ai
  docs: https://docs.limitguard.ai
---

# Verifying sales leads with Limitguard

Limitguard answers one question before you spend effort on a company: is it real, active and safe to deal with? Every answer carries its source. Business-register coverage is the Netherlands (KVK) and Belgium (KBO); VAT works for EU numbers; sanctions and wallet checks work for any name or address.

## Before the first call

The Limitguard tools must be connected (names such as `verify_lead`, `sanctions_preview`). If they are not, tell the user to add the MCP server `https://api.limitguard.ai/mcp` with a Limitguard API key as a Bearer token, or `https://api.limitguard.ai/mcp-oauth` to sign in. Keys come from https://dashboard.limitguard.ai.

Paid tools are charged per call from the key's prepaid balance. Tell the user the price before a paid call they did not ask for, and before checking more than five companies at once. Prices and inputs: [references/tools.md](references/tools.md).

## Pick the tool

| The user wants | Call | Price |
|---|---|---|
| A Dutch or Belgian sales lead checked | `verify_lead` | $0.27 |
| A quick "is this name on a sanctions list?" | `sanctions_preview` | free |
| The sanctions entries behind a possible match | `sanctions_screen` | $0.11 |
| A wallet checked quickly | `wallet_sanctions_preview` | free |
| A full wallet screen | `verify_wallet` | $0.11 |
| A counterparty agent's wallet and ERC-8004 identity | `check_agent_wallet` | $0.75 |
| A trust score with factors for a company (NL register) | `check_entity` | $1.05 |
| A risk score from sanctions and country only | `get_risk_score` | $0.90 |
| A full written report on one company | `get_compliance_report` | $1.85 |
| The last score for a company checked before | `get_trust_score` | free |

Default to `verify_lead` for anything about a lead or a prospect: one call covers the register, VAT, mail server, IBAN and sanctions. Do not add `check_entity` or `sanctions_screen` on top unless the user asks for more.

## Verify a lead

1. Collect what the user has: country (NL or BE), company number, company name, VAT number, email, website domain, address, IBAN. Send everything you have; an input left out is not checked and never counts against the lead.
2. Call `verify_lead`. Belgian leads need the 10-digit KBO number in `company_number`; Belgian companies cannot be looked up by name. Dutch leads work with the 8-digit KVK number or the name.
3. Read `verdict` first, then `flags`, then `lead_score` (0 to 100, higher is better). Meanings: [references/lead-verify-results.md](references/lead-verify-results.md).
4. For each flag, give the user the matching `findings[].action` and `why` from the response. Do not write your own advice for a flag; the response already says what to do.

For a list of leads, check them one by one, keep a running total of the cost, and summarise at the end: how many are `real_active` without flags, how many need a follow-up, and which to drop.

## Report back

Lead with the verdict in plain words ("real and active", "not found in the register"), then the flags with their actions, then the score. Name the source of each fact (KVK, KBO, VIES, OFAC, EU, UN). Never present a sanctions name match as a finding that the company is sanctioned: it is a possible match to review.

## Gotchas

- `sandbox` API keys do not work for `verify_lead`; it only runs on the live registers. The error says so and nothing is charged. Ask for a live key.
- `verdict: ambiguous` means a Dutch name matched more than one company. Ask the user for the KVK number and call again; do not guess between them.
- `verdict: unverifiable` with `reason: be_requires_number` means a Belgian lead was sent without its KBO number.
- `check_entity` reads the Dutch register only. For a Belgian company use `verify_lead` with the KBO number.
- The two scores run in opposite directions: `check_entity` returns `trust_score` (100 is best); `get_risk_score` returns `risk_score` (100 is riskiest).
- `check_entity` returns a `recommendation`: `proceed` (80 to 100), `review` (60 to 79), `enhanced_due_diligence` (40 to 59) or `block` (0 to 39).
- `sanctions_preview` and `wallet_sanctions_preview` allow 10 calls per caller per UTC day each. When the limit is reached, offer the paid screen instead of retrying.
- `get_trust_score` runs no new check; it returns the caller's own stored score for a company checked before, looked up by the name as sent to `check_entity`. Use it to avoid paying twice for the same company.
- The `phone` input of `verify_lead` is refused while website phone lookup is switched off. Leave it out.
