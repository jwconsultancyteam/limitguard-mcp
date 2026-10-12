# Limitguard MCP tools

<!-- Generated from https://api.limitguard.ai/.well-known/mcp/server-card.json. Do not edit by hand. -->

Prices are per call in USD, paid from the API key's prepaid balance or with x402.

| Tool | Price | Required inputs | Optional inputs |
|---|---|---|---|
| `check_entity` | $1.05 | `entity_name`, `country` | `kvk_number`, `domain` |
| `get_trust_score` | free | `entity_id` | none |
| `verify_wallet` | $0.11 | `wallet_address` | `chain_id` |
| `get_risk_score` | $0.90 | `entity_name`, `country` | none |
| `get_compliance_report` | $1.85 | none | `entity_name`, `country`, `kvk_number`, `cbe_number`, `vat_number`, `domain`, `iban`, `wallet_address`, `wallet_chain`, `check_id` |
| `sanctions_preview` | free | `name` | `country` |
| `wallet_sanctions_preview` | free | `wallet_address` | `chain_id` |
| `sanctions_screen` | $0.11 | `name` | `country` |
| `check_agent_wallet` | $0.75 | `wallet` | `agent_id`, `domain` |
| `verify_lead` | $0.27 | `country` | `company_number`, `name`, `vat_number`, `email`, `domain`, `address`, `iban`, `phone`, `target_industries`, `target_size` |

## check_entity

Company check on a business: sanctions screening and country risk, the Dutch KVK register for an NL company, and the website domain when you send it. Returns trust_score (0-100, 100 = best), trust_level (high means low risk), cluster, recommendation, confidence, top_factors and sources_checked.

- `entity_name`: Full legal name of the entity
- `country`: ISO 3166-1 alpha-2 country code
- `kvk_number`: Optional Dutch KVK number (8 digits)
- `domain`: Optional company website domain

## get_trust_score

Look up your own most recent trust score for an entity you checked before, from your stored checks: score, level, when, which product, trend and how many checks are on record. Runs no new check and calls no data source. Free ($0).

- `entity_id`: Entity name, as sent to check_entity

## verify_wallet

Screen a wallet: OFAC SDN address match, on-chain signals (contract check, native and USDC balance, transaction count, first seen on Base) and named risk rules with up to 3 advice items. On Base, also reports any ERC-8004 agent the wallet owns and its open on-chain reputation as descriptive signals, never scored. $0.11. Supports EVM and Solana addresses.

- `wallet_address`: Blockchain wallet address
- `chain_id`: CAIP-2 chain ID (default: eip155:8453 for Base); base, eth, solana, btc also accepted

## get_risk_score

Quick risk score from sanctions screening and country risk only, without the register or domain lookups of check_entity. Returns risk_score (0-100, 100 = riskiest), risk_level (high means high risk, the reverse of check_entity's trust_level), sanctions_match and fatf_status; no recommendation or factors.

- `entity_name`: Full legal name of the entity
- `country`: ISO 3166-1 alpha-2 country code

## get_compliance_report

Per-entity report built from one real check: registry identity, sanctions and PEP screens, domain signals, risk score with the rules that fired, correlations, every finding as a ranked action, a per-source status table (ok / unavailable / error) and a report hash.

- `entity_name`: Full legal name (with country; omit when sending check_id)
- `country`: ISO 3166-1 alpha-2 country code
- `kvk_number`: Optional Dutch KVK number (8 digits)
- `cbe_number`: Optional Belgian CBE number (0XXX.XXX.XXX or 10 digits)
- `vat_number`: Optional EU VAT number
- `domain`: Optional company website domain
- `iban`: Optional IBAN (never stored raw)
- `wallet_address`: Optional crypto wallet address (format check only)
- `wallet_chain`: Optional chain for wallet_address (eth, base, btc, sol, ...)
- `check_id`: Id of a check from an earlier report, instead of identifiers

## sanctions_preview

Free yes/no sanctions preview against the local OFAC SDN, EU and UN lists. Returns possible_match, lists_checked, list_dates and list_note only, never an entry. 10 per caller per UTC day.

- `name`: Company or person name to screen
- `country`: Optional ISO 3166-1 alpha-2 country code (orders matches, never excludes one)

## wallet_sanctions_preview

Free yes/no check of a wallet address against the OFAC SDN list: sanctioned, lists, the list date and its freshness, no programmes or entry ids. 10 per caller per UTC day, separate from sanctions_preview. The full wallet screen is verify_wallet ($0.11).

- `wallet_address`: Blockchain wallet address
- `chain_id`: CAIP-2 chain ID (default: eip155:8453 for Base); base, eth, solana, btc also accepted

## sanctions_screen

Sanctions screen against the local OFAC SDN, EU and UN lists: matched entries with list, entry id, programmes, countries, listing date and match score. A name match is not a determination.

- `name`: Company or person name to screen
- `country`: Optional ISO 3166-1 alpha-2 country code (orders matches, never excludes one)

## check_agent_wallet

Check a counterparty agent's EVM wallet in one call: OFAC SDN digital-currency address list match, Base USDC and ETH balance, ERC-8004 identity registration (and, given an agent id, that agent's owner and payment wallet) and open ERC-8004 feedback, which is not scored. $0.75.

- `wallet`: EVM wallet address (0x + 40 hex characters)
- `agent_id`: Optional ERC-8004 agentId (decimal) the wallet claims
- `domain`: Optional website domain the agent gives for itself (e.g. example.com)

## verify_lead

Verify a NL/BE sales lead against the registers in one call: real and active, VAT, mail server, IBAN, sanctions; a 0-100 lead score. $0.27.

- `country`: NL (KVK) or BE (KBO)
- `company_number`: 8-digit KVK number or 10-digit KBO/CBE number
- `name`: Company name as the lead gave it (NL without a number)
- `vat_number`: EU VAT number, checked with VIES
- `email`: Contact email; only its domain is checked
- `domain`: Company website domain
- `address`: {street, house_number, postcode, city} the lead gave
- `iban`: IBAN the lead gave; only country, bank, BIC and last 4 are returned
- `phone`: Phone number the lead gave; compared with the numbers the company publishes, never echoed. Rejected until website phone lookup is switched on
- `target_industries`: Ideal-customer industries: SBI/NACE code prefixes ("62") or whole words; information only
- `target_size`: Ideal-customer employee range {min, max}, both inclusive; information only
