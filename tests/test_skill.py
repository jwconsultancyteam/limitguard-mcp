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
    for file in path.parent.rglob("*.md"):
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
