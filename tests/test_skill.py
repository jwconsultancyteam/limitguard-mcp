"""The agent skill follows the Agent Skills spec (agentskills.io/specification)."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    head, body = text[4:].split("\n---\n", 1)
    fields: dict[str, str] = {}
    for line in head.splitlines():
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, body


SKILL_FILES = sorted(SKILLS.glob("*/SKILL.md"))


def test_the_repo_ships_a_skill():
    assert SKILL_FILES


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_frontmatter_follows_the_spec(path):
    fields, _ = _frontmatter(path)
    assert set(fields) <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    name = fields["name"]
    assert NAME.match(name) and len(name) <= 64, name
    assert name == path.parent.name, "name must match the folder"
    assert "anthropic" not in name and "claude" not in name
    assert fields["description"] not in (">", "|", ">-", "|-"), "write the description on one line"
    assert 0 < len(fields["description"]) <= 1024
    assert "<" not in fields["description"], "no XML tags in the description"
    assert len(fields.get("compatibility", "")) <= 500


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_body_stays_short_and_its_links_resolve(path):
    _, body = _frontmatter(path)
    assert len(body.splitlines()) < 500
    for target in re.findall(r"\]\(((?:references|scripts|assets)/[^)]+)\)", body):
        assert (path.parent / target).is_file(), target


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_no_dashes_that_read_as_prose_breaks(path):
    for file in [*path.parent.rglob("*.md"), *path.parent.rglob("*.json")]:
        text = file.read_text(encoding="utf-8")
        assert "—" not in text and "–" not in text, file


def test_trigger_queries_cover_both_sides():
    for queries in SKILLS.glob("*/evals/trigger-queries.json"):
        data = json.loads(queries.read_text(encoding="utf-8"))
        hits = sum(q["should_trigger"] for q in data)
        assert hits >= 8 and len(data) - hits >= 8, queries


def test_the_plugin_lists_every_skill():
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    (entry,) = marketplace["plugins"]
    assert entry["name"] == plugin["name"]
    assert sorted(entry["skills"]) == sorted(f"./skills/{p.parent.name}" for p in SKILL_FILES)


@pytest.mark.parametrize("path", SKILL_FILES, ids=lambda p: p.parent.name)
def test_prices_live_only_in_the_generated_reference(path):
    """references/tools.md is regenerated nightly from the API; a price in the prose would go stale."""
    _, body = _frontmatter(path)
    assert not re.search(r"\$\d+\.\d\d", body), "write free/paid and point at references/tools.md"
    routed = set(re.findall(r"\| `([a-z_]+)` \| (?:free|paid) \|", body))
    if not routed:
        return  # a skill that routes to no MCP tool (paying-limitguard-with-x402) has no reference
    tools_md = (path.parent / "references/tools.md").read_text(encoding="utf-8")
    listed = set(re.findall(r"^\| `([a-z_]+)` \|", tools_md, re.M))
    assert routed == listed, f"routed {sorted(routed)} vs generated {sorted(listed)}"


def test_evals_have_unique_ids():
    for evals in SKILLS.glob("*/evals/evals.json"):
        ids = [e["id"] for e in json.loads(evals.read_text(encoding="utf-8"))["evals"]]
        assert len(ids) >= 3 and len(ids) == len(set(ids)), evals


def test_the_plugin_ships_the_oauth_server_and_the_listing_version():
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    listing = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    assert plugin["mcpServers"]["limitguard"]["url"] == "https://api.limitguard.ai/mcp-oauth"
    # Claude Code keeps an installed plugin on this version; the nightly sync moves both.
    assert plugin["version"] == listing["version"]


def test_skills_do_not_reach_into_each_other():
    """Each folder must work when copied alone: links stay inside the skill."""
    for path in SKILL_FILES:
        _, body = _frontmatter(path)
        for target in re.findall(r"\]\(([^)#]+)\)", body):
            assert not target.startswith(("..", "/", "skills/")), (path.parent.name, target)


def test_every_skill_ships_well_formed_evals():
    for path in SKILL_FILES:
        evals = json.loads((path.parent / "evals/evals.json").read_text(encoding="utf-8"))
        assert evals["skill_name"] == path.parent.name
        for case in evals["evals"]:
            assert isinstance(case["prompt"], str) and isinstance(case["expected_output"], str)
        queries = json.loads((path.parent / "evals/trigger-queries.json").read_text(encoding="utf-8"))
        for q in queries:
            assert isinstance(q["query"], str) and isinstance(q["should_trigger"], bool)


def test_no_query_should_trigger_two_skills():
    owners: dict[str, str] = {}
    for path in SKILL_FILES:
        queries = json.loads((path.parent / "evals/trigger-queries.json").read_text(encoding="utf-8"))
        for q in queries:
            if q["should_trigger"]:
                assert q["query"] not in owners, (q["query"], owners.get(q["query"]), path.parent.name)
                owners[q["query"]] = path.parent.name


LIMITGUARD_URL = re.compile(r"https://(?:docs\.|dashboard\.)?limitguard\.ai[^\s)`\"'|]*")


def test_limitguard_links_carry_the_agent_skill_utms():
    """docs/link-standard.md in limitguard-ai: utm_source agent_skill, utm_medium agent."""
    files = [*SKILLS.rglob("*.md"), *(ROOT / ".claude-plugin").glob("*.json")]
    for file in files:
        if file.name in {"tools.md", "recipients.md"}:
            continue  # generated by limitguard-ai
        for url in LIMITGUARD_URL.findall(file.read_text(encoding="utf-8")):
            assert "utm_source=agent_skill" in url and "utm_medium=agent" in url, (file, url)


def test_the_x402_skill_ships_its_recipient_pin():
    pin = (SKILLS / "paying-limitguard-with-x402/references/recipients.md").read_text(encoding="utf-8")
    assert re.search(r"`0x[0-9a-fA-F]{40}`", pin) and "Do not edit by hand" in pin
