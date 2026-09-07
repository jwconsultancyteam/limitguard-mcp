# Changelog

All notable changes to this listing are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this repository follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The version each entry heads is the `version` field of `server.json`.

Versions describe the *listing*, not the service it points at:

| Change | Level |
|--------|-------|
| A tool added, or a tool that gained an optional argument | minor |
| Pricing, descriptions or documentation only | patch |
| A tool removed, renamed, or given a signature its callers cannot keep using | major |

Entries from 1.2.0 onward are written by `scripts/sync_public_repos.py` in
`jwconsultancyteam/limitguard-ai`, which renders this repository from that service's
source and opens a pull request whenever the two diverge. There is no `Unreleased`
section: a change is released here at the moment it is merged.

## [1.2.0] - 2026-09-07

### Changed
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
