# Contributing

Issues and PRs are very welcome here. This file exists so you can tell, in about
two minutes, which kind of change lands where, because in this repo that isn't
obvious from the file listing alone.

## What this repo is (and isn't)

This is a **listing repo**, not the server. It carries the metadata that MCP
directories (the Official MCP Registry, Smithery, Glama) and human readers need to
find and trust the actual product: the hosted MCP server of Limitguard, a lead
validation service, at `https://api.limitguard.ai/mcp`. It checks the company behind
each lead against the KVK or KBO register, EU VAT and sanctions lists, and offers
company, sanctions and wallet checks to developers and AI agents. Calls are paid per
call with x402 or debited from an API key's prepaid balance.

The server implementation is closed-source and lives elsewhere. Nothing in this
repo runs. Every tracked file is a directory manifest, a listing config or page, a
brand asset, the license, or the CI that tags and publishes releases.

## Reporting issues

Open an issue for anything; there's no template to fill in. The usual suspects:

- **Metadata drift**: `server.json` says one version, the registry serves another;
  a tool description that no longer matches what the server actually returns; a
  dead link in the README.
- **Directory listing problems**: the Smithery or Glama entry is stale, missing,
  or pointing somewhere wrong.
- **Server behaviour bugs**: a tool returning wrong data, an unexpected error, a
  pricing mismatch. The fix lands upstream where you can't see it, but this is the
  intake point, so file it here anyway.

What makes a report easy to act on: name the exact file and commit (or tag) you
looked at, say what you compared it against (registry response, live server
output, a directory page), and mention how you spotted it: automated audit,
manual check, a failing client. Issue #18 is a good model: it quoted `server.json`
on `main` next to the registry's own response, named both versions, and confirmed
nothing else was affected. That one was diagnosed and fixed inside a day.

## Pull requests: which files are safe to touch

Some of this repo is **generated**. A sync job in the private upstream repo renders it
whenever an upstream change touches the server, its prices or its docs, and opens a
pull request here from the `sync/limitguard-ai` branch, titled "Sync generated content
from limitguard-ai". A PR that hand-edits a generated part will merge fine and then be
silently overwritten by the next sync, so the effort is wasted, and worse, it looks
fixed for a while.

If you find a problem in a generated part, **open an issue instead of a PR**. The
real fix has to land in the generator, and the next sync carries it here. Everything
else is hand-maintained here and nowhere else, so PRs are the right tool:

| File | Status | PRs? |
| --- | --- | --- |
| `README.md` | partly generated: the Tools table, the price, Method, Description and MCP tool cells of the endpoint tables, the "What it is" and "Start here" lines and the Smithery install command. The rest of the prose is hand-maintained. | prose yes; generated parts no, file an issue |
| `server.json` | partly generated: `tools`, `remotes` and `version`. `title`, `description` and the other fields are hand-maintained. | hand-maintained fields yes; never bump `version` |
| `CHANGELOG.md` | generated: the sync adds one entry per version it bumps | no, file an issue |
| `smithery.yaml` | generated whole; its `description` is copied from `server.json` | no, change `server.json` |
| `llms-install.md` | generated whole | no, file an issue |
| `glama.json` | hand-maintained | yes |
| `assets/logo-*.svg` | copies of the canonical Limitguard brand files | only to match the canonical logo |
| `.github/workflows/release.yml`, `scripts/off-argv-login.py` | hand-maintained | yes |
| `LICENSE` | organisational decision | no |

Typos, broken links, stale descriptions or CI fixes in the hand-maintained parts:
just send the PR. Small and focused is ideal; there's no build to run.

A change to `server.json`'s `title` or `description` reaches the registry only with a
new version, because a published registry version cannot be edited. Do not bump
`version` in the PR. The next sync sees that `smithery.yaml` no longer matches the new
description, regenerates it, bumps the patch version and adds the changelog entry;
merging that sync PR publishes the new version.

## How releases and registry publishing work

So the "why" behind the table above is clear:

1. A change lands upstream. The sync job opens (or updates) its pull request here
   with the regenerated parts, a bumped `version` in `server.json` and a matching
   `CHANGELOG.md` entry, and a maintainer merges it.
2. `release.yml` fires on that merge. If `v<version>` has no tag yet, it tags it
   and creates a GitHub release with the matching `CHANGELOG.md` section as notes.
3. A `publish` job then checks whether the Official MCP Registry already has that
   version and, if not, publishes it with `mcp-publisher`.

Every step is idempotent: re-running over the same commit does nothing. If the
registry ever drifts behind `server.json` again (the #18 situation), the recovery
is a manual `workflow_dispatch` of the release workflow or a manual
`mcp-publisher publish` by a maintainer, not a PR bumping the version field.
Report it, and it'll be re-published.

## Anything else

Not sure whether something is a listing problem or a server problem? Open the
issue anyway and say so. Sorting that out is the maintainers' job, not yours.
