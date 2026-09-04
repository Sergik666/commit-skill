"""Structural tests for SKILL.md — the parts Claude Code actually depends on."""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "commit-flow"
SKILL = SKILL_DIR / "SKILL.md"


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md must start with a YAML frontmatter block"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


class SkillFileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")
        cls.meta = frontmatter(cls.text)

    def test_name_matches_directory(self):
        self.assertEqual(self.meta["name"], SKILL_DIR.name)
        self.assertRegex(self.meta["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_description_is_single_line_and_bounded(self):
        description = self.meta["description"]
        self.assertNotIn("\n", description)
        self.assertLessEqual(len(description), 1024)
        self.assertGreater(len(description), 40)

    def test_description_carries_triggers(self):
        description = self.meta["description"].lower()
        for trigger in ("commit", "branch", "redmine", "pull request"):
            self.assertIn(trigger, description)

    def test_only_expected_frontmatter_keys(self):
        self.assertEqual(set(self.meta), {"name", "description", "version"})

    def test_version_is_semver(self):
        self.assertRegex(self.meta["version"], r"^\d+\.\d+\.\d+$")

    def test_body_documents_every_item(self):
        for item in ("1. Branch", "2. Commit", "3.1", "3.2", "4.1", "4.2"):
            self.assertIn(item, self.text, f"{item} is not documented")

    def test_body_states_the_hard_rules(self):
        body = self.text.lower()
        self.assertIn("textile", body)
        self.assertIn("```md", body)
        self.assertIn("3 to 15 words", body)
        self.assertIn("english", body)
        self.assertIn("blank line", body)
        self.assertIn("capital letter", body)
        self.assertIn("inline code", body)

    def test_validator_script_is_referenced_and_exists(self):
        self.assertIn("scripts/validate_output.py", self.text)
        self.assertTrue((SKILL_DIR / "scripts" / "validate_output.py").is_file())

    def test_natural_language_item_requests_are_documented(self):
        body = self.text.lower()
        for phrase in ("текст коммита", "имя ветки", "pull request", "редмайн"):
            self.assertIn(phrase, body)


if __name__ == "__main__":
    unittest.main()
