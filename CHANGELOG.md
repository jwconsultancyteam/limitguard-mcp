# Changelog

All notable changes to this listing are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this repository follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The version each entry heads is the `version` field of `server.json`.

Versions describe the *listing*, not the service it points at:

| Change | Level |
|--------|-------|
| A tool added, or a tool that gained an optional argument | minor |
| A tool's `inputSchema` published for the first time, or widened so that every call which was valid before still is | minor |
| Pricing, descriptions or documentation only | patch |
| A tool removed, renamed, or given a signature its callers cannot keep using | major |

The second row is what 1.2.0 is: the tools and their arguments did not change, but the
listing had never stated the arguments, so a caller reading it gained something it could
not act on before. Descriptions changed in the same release, which is a patch on its own;
the higher level wins.

Entries from 1.2.0 onward are written by `scripts/sync_public_repos.py` in
`jwconsultancyteam/limitguard-ai`, which renders this repository from that service's
source and opens a pull request whenever the two diverge. There is no `Unreleased`
section: a change is released here at the moment it is merged.

## [1.3.1] - 2026-09-08

### Changed
- Published tool table and prices refreshed.

## [1.3.0] - 2026-09-08

### Changed
- Tool `check_agent` description updated.
- Tool `get_trust_score` description updated.
- Tool `verify_wallet` description updated.

## [1.2.2] - 2026-09-08

### Added

`glama.json` gained an `auth` block, a `pricing` block and a `tools` array: the five tool
names with their inputs, their per-call USDC price, and a `status`. Prices and
descriptions only, so this is a patch by the table above. The Glama schema this file
declares formally defines one property, `maintainers`, and permits the rest, so whether
the directory renders any of these blocks is unverified; the file is written to be true
for whoever reads it either way.

- The three tools that return placeholder data (`check_agent`, `get_trust_score`,
  `verify_wallet`) are marked `"status": "unimplemented"` and say so in their
  descriptions. That disclosure is in this file alone. `server.json`, `smithery.yaml` and
  the README still present all five as working, and the registry and Smithery read those,
  so an agent arriving by any route other than Glama is not yet told.

### Fixed

- `glama.json` listed `eip155:84532` (Base Sepolia) as a settlement network beside the two
  mainnets, with nothing marking it a testnet. The x402 manifest it names as its own
  source of truth carries two chains under `payment.chains`, both mainnet, and reports
  testnet support in a separate `testnet_supported` flag without naming a chain. The
  network list now mirrors those two and carries the flag.
- The `auth` block told agents to send `Bearer <lg_live_...>`. `POST /v1/keys/create`
  returns an `lg_live_` key on the default free tier but an `lg_sandbox_` key when the
  body asks for `"tier": "sandbox"` -- which is what the README's own example asks for.
  Both authenticate; only the server's error string still names `lg_live_`. Both prefixes
  and the request that produces each are stated now.
- Each placeholder's pricing note said charging "is suspended" while the same entry
  priced the tool at 0.10. limitguard-ai#206 decided on the suspension; the code has not
  shipped, and the live manifest still prices all three at 0.10. The note now separates
  the decision from what the API currently charges.

### Note

This entry was written by hand. The header above says entries from 1.2.0 onward come from
`scripts/sync_public_repos.py`, and that generator did not produce this one: the change is
`glama.json`-only, and the release workflow's path filter covers `server.json` and
`CHANGELOG.md`, so a `glama.json`-only merge bumps and releases nothing. The version bump
and this section are what make the change reach the tag.

## [1.2.1] - 2026-09-07

### Fixed

- "API key tiers" said an API key carries a monthly call allowance. A `free`-tier key is
  identity and usage tracking: it owes x402 on every paid endpoint, on REST exactly as on
  MCP, and the `monthly_limit` it reports is a ceiling on calls rather than a grant of free
  ones. REST enforced none of that until limitguard-ai#223 closed the bypass.
- The `POST /v1/keys/create` example asked for `"tier": "sandbox"`, and the Quick Start
  configs then wired that key into `Authorization: Bearer`. A reader following the README
  end to end paid x402 for mock answers. The example creates the `free` key those configs
  expect, and what a sandbox key is for is stated where it is offered.
- Authentication step 2 said a sandbox key lifts the payment requirement on the `/v1/mcp/*`
  REST mirrors, "the cheapest way to try the tools before wiring up payment". Those mirrors
  answer a sandbox key with mock data, not a discounted real check -- the sandbox response
  is served before the payment check -- and on MCP a sandbox key pays like any other free
  key. Both halves are now said plainly.
- "x402 per call -- which needs no API key, as everywhere else in this README" held for 13
  of the 18 endpoints. The MCP transport takes a Bearer key on every `tools/call` and the
  five `/v1/mcp/*` mirrors take `X-API-Key`; the section now counts them.
- The upgrade table's "Allowance" column is `monthly_limit`, the field the API returns. The
  paragraph above it defines an allowance as free calls, which is the one thing a base key
  does not get, so the column contradicted the prose it sat under.
- The upgrade prices sat between "subscription prepays the calls" and "a one-time x402
  payment", against a table counting calls per month, without saying whether the price
  recurs. The manifest prices the upgrade call and says nothing about the month after, and
  the README now says so rather than implying either reading.

## [1.2.0] - 2026-09-07

### Changed

Each tool entry in `server.json` gained the `inputSchema` the live server card publishes,
under a top-level `tools` array. That array is not a field of the `2025-12-11` server
schema this file declares: the schema permits it, but the official MCP registry stores
only the fields it defines and drops the rest, as it did to the same array in 1.0.1. The
directories that read this repository's `server.json` directly -- glama.ai and Smithery
among them -- are what these signatures reach. Publishing them through the registry too
means moving the array under `_meta`, which is where that schema puts vendor data, and is
left for the maintainers to decide because the nightly `mcp-listing-parity` job reads the
array where it is now.

- Tool `check_agent` signature published.
- Tool `check_agent` description updated.
- Tool `check_entity` signature published.
- Tool `check_entity` description updated.
- Tool `get_risk_score` signature published.
- Tool `get_risk_score` description updated.
- Tool `get_trust_score` signature published.
- Tool `get_trust_score` description updated.
- Tool `verify_wallet` signature published.
- Tool `verify_wallet` description updated.

### Fixed

- The "MCP tool paths" table and the paragraph above it named `trust_score` and
  `risk_score`. The server answers to `get_trust_score` and `get_risk_score`; the tool
  table three sections up has said so since 1.1.0, so the README contradicted itself.
  That column is generated from now on.
- "Discovery Endpoints" listed `/.well-known/mcp.json` as the only tool card. The service
  serves a second one at `/.well-known/mcp/server-card.json`, and the two disagree: same
  five tools and same required arguments, different descriptions and different argument
  wording. The README's tool table and `server.json` are generated from the server card,
  so the table sent readers to the card neither of them matches. Both are listed now, and
  which one this listing follows is stated.

## [1.1.0] - 2026-09-06

### Added

- The 13 x402-priced REST endpoints outside the MCP tool set, grouped by the live
  manifest's own categories. The README previously described only the five MCP tools,
  which understated the API for anyone integrating directly over HTTP.
- How a base API key is obtained, next to the four `/v1/keys/upgrade/*` tiers that act
  on one.
- What gates a `tools/call`: an API key on every call, plus an x402 payment on the free
  and sandbox tiers.

### Changed

- Migrated `server.json` to the `2025-12-11` server schema. The nested
  `version_detail.version` became a top-level `version`.
- Corrected `repository.url` and the `glama.json` maintainer to `jwconsultancyteam`.
  The organisation the repository now belongs to was reached only through GitHub's
  redirect from the previous owner.

### Fixed

- Two tools were listed under names the server does not answer to: `trust_score` and
  `risk_score` are `get_trust_score` and `get_risk_score`. A `tools/call` using the
  published name returned `Unknown tool`. This was a breaking correction to the listing
  and should have carried a major version; it shipped inside 1.1.0.

## [1.0.1] - 2026-02-28

### Added

- Initial listing for the LimitGuard Trust Intelligence MCP server: `server.json`,
  `smithery.yaml`, `glama.json`, README and licence, covering the five tools reachable
  at `https://api.limitguard.ai/mcp`.
- `.gitignore`, and category and homepage metadata in `glama.json` (2026-03-02, released
  under this version).

### Fixed

- Copyright holder corrected to Ambulatio Consulting B.V.
- Per-call prices aligned with the live `/.well-known/x402.json` manifest.
