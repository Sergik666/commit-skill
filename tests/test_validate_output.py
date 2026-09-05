"""Tests for the commit-flow output validator."""

import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "commit-flow" / "scripts" / "validate_output.py"
FIXTURES = ROOT / "tests" / "fixtures"

sys.path.insert(0, str(SCRIPT.parent))
import validate_output as vo  # noqa: E402


def fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


class ExpandItemsTest(unittest.TestCase):
    def test_defaults_to_everything(self):
        self.assertEqual(vo.expand_items(None), vo.ALL_ITEMS)
        self.assertEqual(vo.expand_items(""), vo.ALL_ITEMS)
        self.assertEqual(vo.expand_items("all"), vo.ALL_ITEMS)
        self.assertEqual(vo.expand_items("все"), vo.ALL_ITEMS)

    def test_bare_group_expands_to_both_subitems(self):
        self.assertEqual(vo.expand_items("3"), ("3.1", "3.2"))
        self.assertEqual(vo.expand_items("1 3"), ("1", "3.1", "3.2"))

    def test_separators_and_subitems(self):
        self.assertEqual(vo.expand_items("1,4"), ("1", "4.1", "4.2"))
        self.assertEqual(vo.expand_items("3.2"), ("3.2",))

    def test_unknown_item_rejected(self):
        with self.assertRaises(ValueError):
            vo.expand_items("5")


class ValidateTest(unittest.TestCase):
    def test_valid_full_answer(self):
        self.assertEqual(vo.validate(fixture("valid_all.md")), [])

    def test_valid_subset(self):
        errors = vo.validate(fixture("valid_subset_1_4.md"), vo.expand_items("1,4"))
        self.assertEqual(errors, [])

    def test_subset_checked_against_wrong_request(self):
        errors = vo.validate(fixture("valid_subset_1_4.md"), vo.expand_items("all"))
        self.assertIn("item 2: missing", errors)
        self.assertIn("item 3.1: missing", errors)

    def test_extra_item_reported(self):
        errors = vo.validate(fixture("valid_all.md"), vo.expand_items("1"))
        self.assertIn("item 2: not requested but present", errors)

    def test_invalid_answer_reports_every_rule(self):
        errors = vo.validate(fixture("invalid_multiline_and_labels.md"))
        joined = "\n".join(errors)
        self.assertIn("bad branch name", joined)
        self.assertIn("expected 3-15", joined)
        self.assertIn("expected 'textile'", joined)
        self.assertIn("expected 'md'", joined)
        self.assertEqual(joined.count("paragraph broken across multiple lines"), 2)

    def test_long_branch_name(self):
        text = "1. Branch:\n```\n" + "a" * 51 + "\n```"
        self.assertIn("longer than 50 chars (51)", "\n".join(vo.validate(text, ("1",))))

    def test_commit_word_bounds(self):
        def commit(text):
            return "2. Commit:\n```\n" + text + "\n```"

        self.assertEqual(vo.validate(commit("add price form"), ("2",)), [])
        self.assertEqual(vo.validate(commit("w " * 15), ("2",)), [])
        self.assertIn("2 words", "\n".join(vo.validate(commit("add it"), ("2",))))
        self.assertIn("16 words", "\n".join(vo.validate(commit("w " * 16), ("2",))))

    def test_single_line_item_rejects_multiline_value(self):
        text = "1. Branch:\n```\nfeat/x\nfeat/y\n```"
        self.assertIn(
            "item 1: value must be a single line inside the code block",
            vo.validate(text, ("1",)),
        )

    def test_empty_code_block(self):
        text = "3.2. Redmine description:\n```textile\n```"
        self.assertIn("item 3.2: empty description", vo.validate(text, ("3.2",)))

    def test_headings_and_paragraphs_are_allowed(self):
        text = (
            "3.2. Redmine description:\n```textile\nh3. Summary\n\n"
            "One continuous paragraph of Textile text.\n\n"
            "h3. Details\n\nAnother continuous paragraph.\n```"
        )
        self.assertEqual(vo.validate(text, ("3.2",)), [])

    def test_paragraph_split_mid_sentence_is_rejected(self):
        text = (
            "4.2. PR description:\n```md\n## Summary\n"
            "This sentence is\nwrapped mid paragraph without a blank line.\n```"
        )
        errors = vo.validate(text, ("4.2",))
        self.assertTrue(any("paragraph broken across multiple lines" in e for e in errors))

    def test_missing_code_block_after_header(self):
        errors = vo.validate("3.2. Redmine description:\nplain text, no fence", ("3.2",))
        self.assertIn("item 3.2: missing", errors)


class CliTest(unittest.TestCase):
    def run_cli(self, path, items=None):
        cmd = [sys.executable, str(SCRIPT), str(FIXTURES / path)]
        if items:
            cmd += ["--items", items]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_exit_zero_on_valid(self):
        result = self.run_cli("valid_all.md")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.strip(), "")

    def test_exit_one_and_prints_errors(self):
        result = self.run_cli("invalid_multiline_and_labels.md")
        self.assertEqual(result.returncode, 1)
        self.assertIn("item 1: bad branch name", result.stdout)

    def test_reads_stdin(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--items", "1"],
            input="1. Branch:\n```\nfeat/x\n```\n", capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
