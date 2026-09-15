# Contributing

Issues and PRs are very welcome here. This file exists so you can tell, in about
two minutes, which kind of change lands where -- because in this repo that isn't
obvious from the file listing alone.

## What this repo is (and isn't)

This is a **listing repo**, not the server. It carries the metadata that MCP
directories (the Official MCP Registry, Smithery, Glama) and human readers need to
find and trust the actual product: a hosted MCP server at `https://api.limitguard.ai/mcp`
that does entity verification, sanctions screening and risk scoring for AI agents,
paid per call via x402.

The server implementation is closed-source and lives elsewhere. Nothing in this
repo runs. Every tracked file is either a directory manifest, a listing config, the
license, or the CI that tags releases.

## Reporting issues

Open an issue for anything -- there's no template to fill in. The usual suspects:

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
output, a directory page), and mention how you spotted it -- automated audit,
manual check, a failing client. Issue #18 is a good model: it quoted `server.json`
on `main` next to the registry's own response, named both versions, and confirmed
nothing else was affected. That one was diagnosed and fixed inside a day.

## Pull requests: which files are safe to touch

Three files in this repo are **generated**. `README.md`, `CHANGELOG.md` and
`server.json` are written by a sync job that runs from the private upstream repo
every time it cuts a release (look for commits by `limitguard-sync[bot]`). A PR
that hand-edits any of them will merge fine and then be silently overwritten on the
next release, so the effort is wasted -- and worse, it looks fixed for a while.

If you find a problem in one of those three, **open an issue instead of a PR**.
The real fix has to land in the generator, and the next sync carries it here.

The rest is hand-maintained here and nowhere else, so PRs are the right tool:

| File | Status | PRs? |
| --- | --- | --- |
| `README.md` | generated, synced from upstream | no -- file an issue |
| `CHANGELOG.md` | generated, synced from upstream | no -- file an issue |
| `server.json` | generated, synced from upstream | no -- file an issue |
| `glama.json` | hand-maintained | yes |
| `smithery.yaml` | hand-maintained | yes |
| `.github/workflows/release.yml` | hand-maintained | yes |
| `LICENSE` | organisational decision | no |

Typos, broken links, stale descriptions or CI fixes in the hand-maintained files:
just send the PR. Small and focused is ideal; there's no build to run.

## How releases and registry publishing work

So the "why" behind the table above is clear:

1. Upstream cuts a release. The sync job pushes the regenerated `README.md`,
   `CHANGELOG.md` and `server.json` (with the bumped `version`) into this repo.
2. `release.yml` fires on that merge. If `v<version>` has no tag yet, it tags it
   and creates a GitHub release with the matching `CHANGELOG.md` section as notes.
3. A `publish` job then checks whether the Official MCP Registry already has that
   version and, if not, publishes it with `mcp-publisher`.

Every step is idempotent: re-running over the same commit does nothing. If the
registry ever drifts behind `server.json` again (the #18 situation), the recovery
is a manual `workflow_dispatch` of the release workflow or a manual
`mcp-publisher publish` by a maintainer -- not a PR bumping the version field.
Report it, and it'll be re-published.

## Anything else

Not sure whether something is a listing problem or a server problem? Open the
issue anyway and say so. Sorting that out is the maintainers' job, not yours.
